"""
This script can be used to find out team owned vs system owned 
principals. 

System owned can be User Assigned identities

It also clears out any SP role assignment in which the SP cannot be found in AAD 
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

seen_principals = []
cleaned = 0
team_owned = {}
system_owned = {} # no owners
for subid in cfg.subscriptions:
    print("Getting role assigments for", subid)
    output = AzRolesUtils.get_all_roles(subid, False)

    
    for role in output:
        if subid not in role.scope:
            print("Skip it....not in requested sub")
            continue 

        if role.principalType == "ServicePrincipal":
            print("TEST -> ", role.principalId)

            if role.principalId in seen_principals:
                print("Duplicate lookup....")
                continue
            else:
                seen_principals.append(role.principalId)

            sp = AzRolesUtils.get_aad_sp_info(role.principalId)

            if sp is None:
                print("Invalid Role with Unfound SP")
                cleaned += 1
                role.delete()
                continue

            usable_dict = team_owned if len(sp.owners) > 0 else system_owned

            if sp.servicePrincipalType not in usable_dict:
                usable_dict[sp.servicePrincipalType] = {}
            usable_dict = usable_dict[sp.servicePrincipalType]

            if sp.displayName not in usable_dict:
                usable_dict[sp.displayName] = []
            usable_dict = usable_dict[sp.displayName]

            if sp.owners and len(sp.owners):
                usable_dict.extend([x.__dict__ for x in sp.owners])
    break

print("Cleaned up ", cleaned)

path = os.path.join(usable_path, "team.json")
with open(path, 'w') as outupt_file:
    outupt_file.writelines(json.dumps(team_owned, indent=4))

path = os.path.join(usable_path, "sysowned.json")
with open(path, 'w') as outupt_file:
    outupt_file.writelines(json.dumps(system_owned, indent=4))    