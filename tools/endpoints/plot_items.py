import os
import json
from enum import Enum
import sys
sys.path.insert(0, "..")
from utils.pathutils import PathUtils
from utils.cmdline import CmdUtils

usable_path = "./open_endpoints"
PathUtils.ensure_path(usable_path)

class Indexes(Enum):
    ID_IDX = 0
    SUB_ID_IDX = 1
    SUB_NAME_IDX = 10
    RG_NAME_IDX = 7
    RES_NAME_IDX = 5
    RES_TYPE_IDX = 6

class MissingEndpointResource:
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

# Load file data
data_files = ["./other.tsv", "./batch.tsv"]
file_data = []
for data_file in data_files:
    with open(data_file, "r") as inputf:
        file_data.extend(inputf.readlines())

# Translate the file data
all_assets = []
for line in file_data:
    res  = line.split("\t")
    # Try and get the resource, add a new field to the object
    # if it's there? 
    mi = MissingEndpointResource(res)
    all_assets.append(mi)

breakdown = {}

# Local Tracking
flagged = {}
# Local Tracking

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

# Now dump out everything for all subs
for sub in breakdown:
    filename = os.path.join(usable_path, "{}.json".format(sub))
    with open(filename, "w") as outputfile:
        outputfile.writelines(json.dumps(breakdown[sub], indent=4))

print(json.dumps(flagged, indent=4))
