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
    
    return parts[6].lower()


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

for subid in cfg.subscriptions:
    print("Getting role assigments for", subid)
    output = AzRolesUtils.get_all_roles(subid, False)

    users = {}
    groups = {}
    principals = {}
    types_coll = {}
    

    # Summary or all of them
    types = [x.principalType for x in output if subid in x.scope]
    for t in types:
        if t not in types_coll:
            types_coll[t] = 0
        types_coll[t] += 1
    types_coll["UserAssignments"] = 0
    types_coll["GroupAssignments"] = 0
    types_coll["SPAssignments"] = 0

    for role in output:
        toadd = role.principalName if role.principalName else role.principalId
        if not toadd:
            toadd = "UNKNOWN"

        if subid not in role.scope:
                continue         
        
        if role.principalType.lower() == 'user':
            types_coll["UserAssignments"] += 1
            dist = get_type(role.scope)
            if dist not in users:
                users[dist] = []
            users[dist].append("USER - {} - {} - {}".format(
                toadd,
                role.roleDefinitionName,
                role.scope
            ))

        if role.principalType.lower() == "serviceprincipal":
            types_coll["SPAssignments"] += 1
            dist = get_type(role.scope)
            if dist not in principals:
                principals[dist] = []
            principals[dist].append("SP - {} - {} - {}".format(
                toadd,
                role.roleDefinitionName,
                role.scope
            ))


        if role.principalType.lower() == 'group':
            types_coll["GroupAssignments"] += 1
            dist = get_type(role.scope)
            if dist not in groups:
                groups[dist] = []
            groups[dist].append("AAD GROUP - {} - {} - {}".format(
                toadd,
                role.roleDefinitionName,
                role.scope
            ))
        
    output_data = {
        "Summary" : types_coll,
        "Groups" : groups,
        "Users" : users,
        "Principals" : principals
    }        

    file_path = os.path.join(usable_path, "{}.json".format(subid))
    with open(file_path, "w") as summary_report:
        summary_report.writelines(
            json.dumps(output_data, indent=4)
        )

print("Role summary collected")