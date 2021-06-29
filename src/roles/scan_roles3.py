"""
This file uses the configuration.json in the root folder and 
collects all current role assignemnts for each identified sub.

Configuration Settings
    subscriptions - List of subscription ID's
    principals.roleDirectory - Directory to put assignments in

Outputs all data into 
    ./[principals.roleDirectory]/[subid].json
"""
import os
import sys
import json
sys.path.insert(0, "..")
from utils.config import Configuration
from utils.pathutils import PathUtils
from utils.roles import AzRolesUtils
from utils.login import AzLoginUtils


def get_type(scope):
    # /subscriptions/1b365fe2-5882-4935-bd81-8027e0816b45/resourceGroups/daden1/providers/Microsoft.Storage/storageAccounts/daden1exp2ws2677378701
    parts = scope.split('/')
    if len(parts) == 3:
        return "Subscription"
    if len(parts) == 5:
        return "ResourceGroup"
    
    if len(parts) >= 7:
        return parts[6].lower()
    else:
        return "GLOBAL"

# Ensure a login and switch to SP if requested
try:
    AzLoginUtils.validate_login("../../credentials.json")
except Exception as ex:
    print(str(ex))
    quit()

# Get configuration for run
cfg = Configuration("../../configuration.json")

# Ensure we have data
if not len(cfg.subscriptions):
    raise Exception("Update configuration.json with sub ids")
if "roleSummaryDirectory" not in cfg.roles:
    raise Exception("Missing roleSummaryDirectory from roles")

# Ensure we have the output folder
usable_path = "./" + cfg.roles["roleSummaryDirectory"]
PathUtils.ensure_path(usable_path)


# Stats
#{
#   sub : {
#        dist : {
#           [role name, id, scope]    
#       }
#   }
#}
"""
    Total Stats
        Users : Total
        Groups: Total
        SPs : Total;
"""
statistics = { }
totals = {}
assignments = {}

for subid in cfg.subscriptions:
    print("Getting role assigments for", subid)
    output = AzRolesUtils.get_all_roles(subid, False)

    
    for role in output:

        toadd = role.principalName if role.principalName else role.principalId

        try: 
            dist = get_type(role.scope)
            subscope = role.subscription
        except Exception as ex:
            print(json.dumps(role.__dict__, indent=4))
            quit()

        # Entry for subscription (toop level)
        usable_entry = None
        if subscope not in statistics:
            statistics[subscope] = {}
        usable_entry = statistics[subscope]

        # Now the distribution
        if dist not in usable_entry:
            usable_entry[dist] = {}
        usable_entry = usable_entry[dist]

        # Now the role def name roleDefinitionName
        if role.roleDefinitionName not in usable_entry:
            usable_entry[role.roleDefinitionName] = {}
        usable_entry = usable_entry[role.roleDefinitionName]

        # Now the type
        if role.principalType not in usable_entry:
            usable_entry[role.principalType] = []
        usable_entry = usable_entry[role.principalType]

        usable_entry.append("{} - {}".format(
            toadd,
            role.scope
        ))



        # Now collect totals and assignments 
        if role.principalType not in totals:
            totals[role.principalType] = {}

        if role.principalType not in assignments:
            assignments[role.principalType] = 0
        assignments[role.principalType] += 1

        usable_entry = totals[role.principalType]
        if role.principalId not in usable_entry:
            usable_entry[role.principalId] = []
        usable_entry = usable_entry[role.principalId]

        if subscope not in usable_entry: 
            usable_entry.append(subscope)

for subid in statistics:
    file_path = os.path.join(usable_path, "{}.json".format(subid))
    with open(file_path, "w") as summary_report:
        summary_report.writelines(
            json.dumps(statistics[subid], indent=4)
        )

# Patch it
inject_dict = {}
for roletype in totals:
    inject_dict[roletype] = len(totals[roletype]) 

totals["OverallCountsGlobal"] = inject_dict
totals["OverallAssignments"] = assignments

file_path = os.path.join(usable_path, "global_summary.json")
with open(file_path, "w") as summary_report:
    summary_report.writelines(
        json.dumps(totals, indent=4)
    )
