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

cfg = Configuration("../../configuration.json")

# Ensure we have data
if not len(cfg.subscriptions):
    raise Exception("Update configuration.json with sub ids")
if "roleDirectory" not in cfg.principals:
    raise Exception("Missing roleDirectory from principals")

# Ensure we have the output folder
usable_path = "./" + cfg.principals["roleDirectory"]
PathUtils.ensure_path(usable_path)

for subid in cfg.subscriptions:
    print("Getting role assigments for", subid)
    output = AzRolesUtils.get_all_roles(subid, True)
    
    if output:
        file_path = os.path.join(usable_path, "{}.json".format(subid))
        with open(file_path, "w") as out_file:
            out_file.writelines(json.dumps(output, indent=4))

print("Role assignments collected")