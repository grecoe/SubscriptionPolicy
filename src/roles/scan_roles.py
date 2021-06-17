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
    groups = []
    types_coll = {}
    
    types = [x.principalType for x in output]
    for t in types:
        if t not in types_coll:
            types_coll[t] = 0
        types_coll[t] += 1

    unknown = 1
    for role in output:
        if role.principalType.lower() == 'user':
            users[str(unknown)] = {
                "name" : role.principalName if role.principalName else role.principalId,
                "command" : role.get_delete_command()
            }
            unknown += 1

        if role.principalType.lower() == 'group':
            toadd = role.principalName if role.principalName else role.principalId

            if not toadd or len(toadd) == 0:
                toadd = "Not Found"

            if toadd not in groups:
                groups.append(toadd)
        
    output_data = {
        "Summary" : types_coll,
        "Groups" : groups,
        "Users" : users
    }        

    file_path = os.path.join(usable_path, "{}.json".format(subid))
    with open(file_path, "w") as summary_report:
        summary_report.writelines(
            json.dumps(output_data, indent=4)
        )

print("Role summary collected")