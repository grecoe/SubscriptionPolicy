"""
This tool will filter down Network Isolation reports to usable and actionable lists
of resources that are causing the reports. 

The tool exists because the reporting can:

1. Be out of date, so the tool verifies that the resource group in which the 
resource resides in still exists. We experienced several items being reported 
on days after they no longer existed in the Subscription. 

2. Can also contain duplicates which effectively are noise and get filtered out 
of the net result. 

Due to reporting on S360, there is no easy export of the information from Lens 
and it has to be done by hand. 

1. Go to the S360 Dashboard
2. Click on [C + AI] Network Isolation missed SLA
3. For each entry:
    - Click on the NetIsoActionItems link 
    - This brings up Lens but you cannot export.
    - Highlight all content in the bottom table and paste it to a file in this 
      directory (preferably named *.tsv so you know whats in it)
4. When done, modify modify line 121 with whatever 
   files you have created from step 3. 
5. Run the script, it will create a file for each subscription denoted in the 
   downloaded TSV files in the ./logs/open_endpoints directory.

Each of the generated files is a JSON structure that calls out
1. The resource type causing the alert
2. For each resource it lists out
    - Azure Resource ID
    - Azure Resource Name
    - Azure Resource Group
    - NOTE: Two of the above can be gleaned from the resource ID but they are there anyway. 


Example Output:
I've created two outputs from S360 that contain BatchPools and PostgreSQL endpoints
that have been reported on. Now, the files were a few days old BUT each section 
reports:

total -> Total number of resource being reported
exists -> Of the total, how many actually exist in the sub
duplicate -> List of resources that were duplicates in the report

The actual number of items needing attention is

exists - len(duplicate)

{
    "Microsoft.Batch/batchAccounts/pools": {
        "total": 4,
        "exists": 0,
        "duplicate": []
    },
    "Microsoft.DBforPostgreSQL/servers": {
        "total": 17,
        "exists": 2,
        "duplicate": [
            "carbonaigeoserverlje5ny"
        ]
    }
}

"""
import os
import json
from enum import Enum
from microsoft.submaintenance.utils import (
    PathUtils, 
    CmdUtils,
    AzLoginUtils
)

CREDENTIALS_FILE = "./credentials.json"

# Ensure a login and switch to SP if requested
try:
    AzLoginUtils.validate_login(CREDENTIALS_FILE)
except Exception as ex:
    print(str(ex))
    quit()

# Output path for logs
usable_path = PathUtils.ensure_path("./logs/open_endpoints")

class Indexes(Enum):
    """CSV Indexes into the data which we care about. Batch and PostgreSQL
    reports are almost identical and I believe the NetIsoActionItems follow
    the same output pattern"""
    ID_IDX = 0
    SUB_ID_IDX = 1
    SUB_NAME_IDX = 10
    RG_NAME_IDX = 7
    RES_NAME_IDX = 5
    RES_TYPE_IDX = 6

class MissingEndpointResource:
    """Class to check for existence of a resource being reported on."""
    def __init__(self, props_arr):
        setattr(self, "id", props_arr[Indexes.ID_IDX.value])
        setattr(self, "subid", props_arr[Indexes.SUB_ID_IDX.value])
        setattr(self, "subname", props_arr[Indexes.SUB_NAME_IDX.value])
        setattr(self, "resourceGroup", props_arr[Indexes.RG_NAME_IDX.value])
        setattr(self, "resource", props_arr[Indexes.RES_NAME_IDX.value])
        setattr(self, "restype", props_arr[Indexes.RES_TYPE_IDX.value])

        command = "az resource show --ids {}".format(self.id)
        res = CmdUtils.get_command_output(command.split(" "))
        self.exists = False
        if isinstance(res, dict):
            self.exists = True


################################################
# Load data files, update data_files to contain 
# the files you wish to validate against. 
################################################
data_files = [
    "C:\\...\\batchPools.tsv", 
    "C:\\...\\postGreSQL.tsv"]
file_data = []
for data_file in data_files:
    with open(data_file, "r") as inputf:
        file_data.extend(inputf.readlines())

################################################
# Copy paste from Lens creates TSV formatted data
# parse it into MissingEndpointResource objects
# as a list.
################################################
all_assets = []
for line in file_data:
    res  = line.split("\t")
    mi = MissingEndpointResource(res)
    all_assets.append(mi)


# Local Tracking
flagged = {}
# Local Tracking

################################################
# Break down the data to subscriptions - remove
# duplicates and record if it even exists.
################################################
breakdown = {}
for mer in all_assets:
    if mer.subid not in breakdown:
        breakdown[mer.subid] = {}
    
    if mer.restype not in breakdown[mer.subid]:
        breakdown[mer.subid][mer.restype] = []

    # Local Tracking
    if mer.restype not in flagged:
        flagged[mer.restype] = {"total": 0, "exists": 0, "duplicate" : [] }
    flagged[mer.restype]["total"] += 1
    flagged[mer.restype]["exists"] += 1 if mer.exists else 0
    # Local Tracking

    # Check for a duplicate
    duplicate = [x for x in breakdown[mer.subid][mer.restype] if x["id"] == mer.id]
    is_duplicate = False
    if len(duplicate) > 0:
        # Found the same ID, make sure it's in the same group
        if duplicate[0]["group"] == mer.resourceGroup and mer.exists:
            is_duplicate = True
            flagged[mer.restype]["duplicate"].append(mer.resource)

    if not is_duplicate and mer.exists:
        # Record ONLY if unique and exists
        breakdown[mer.subid][mer.restype].append(
            {
                "id": mer.id,
                "resource": mer.resource,
                "group": mer.resourceGroup,
                "exists" : mer.exists
            }
    )

################################################
# Now dump out everything for all subs
################################################
for sub in breakdown:
    filename = os.path.join(usable_path, "{}.json".format(sub))
    with open(filename, "w") as outputfile:
        outputfile.writelines(json.dumps(breakdown[sub], indent=4))

# Give an overview on the command line to the user. 
print(json.dumps(flagged, indent=4))
