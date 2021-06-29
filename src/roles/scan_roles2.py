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

def get_subscription(scope : str):
    parts = scope.split('/')
    return parts[2]


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

statistics = {
    "types" : {},
    "distribution" : {},
    "scopes" : {}
}

total_sps_all = 0
owning_sps = 0
total_sps = []

for subid in cfg.subscriptions:
    print("Getting role assigments for", subid)
    output = AzRolesUtils.get_all_roles(subid, False)

    
    # Summary or all of them
    types = [x.principalType for x in output if subid in x.scope]
    for t in types:
        if t not in statistics["types"]:
            statistics["types"][t] = 0
        statistics["types"][t] += 1

    unknown = 1
    for role in output:
        if subid not in role.scope:
            continue 

        toadd = role.principalName if role.principalName else role.principalId

        dist = get_type(role.scope)
        if dist not in statistics["distribution"]:
            statistics["distribution"][dist] = 0

            if dist not in statistics["scopes"]:
                statistics["scopes"][dist] = [] 
            statistics["scopes"][dist].append("{} - {}".format(toadd, role.scope))

        statistics["distribution"][dist] += 1


        if role.principalType == "ServicePrincipal":
            if role.roleDefinitionName == "Owner":
                owning_sps += 1
            total_sps_all += 1
            if toadd not in total_sps:
                total_sps.append(toadd)
            
        """
        if role.scope not in statistics["scopes"]:
            statistics["scopes"][role.scope] = {}

        if role.roleDefinitionName.lower() not in statistics["scopes"][role.scope]:
            statistics["scopes"][role.scope][role.roleDefinitionName.lower()] = {}

        if role.principalType.lower() not in statistics["scopes"][role.scope][role.roleDefinitionName.lower()]:
            statistics["scopes"][role.scope][role.roleDefinitionName.lower()][role.principalType.lower()] = 0

        statistics["scopes"][role.scope][role.roleDefinitionName.lower()][role.principalType.lower()] += 1
        """

    file_path = os.path.join(usable_path, "{}.json".format(subid))
    with open(file_path, "w") as summary_report:
        summary_report.writelines(
            json.dumps(statistics, indent=4)
        )

print("Role summary collected")

print("All SP Assignments", total_sps_all)
print("Unique SP's ->", len(total_sps))
print("Owner SPs", owning_sps)