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
import json
import sys
sys.path.insert(0, "..")
from utils.config import Configuration
from utils.cmdline import CmdUtils
from utils.pathutils import PathUtils

# Load configuration
cfg = Configuration("../../configuration.json")

# Ensure we have data
if not len(cfg.subscriptions):
    raise Exception("Update configuration.json with sub ids")
if "required_tags" not in cfg.tagging:
    raise Exception("Missing required_tags from tagging")
if "delete_on_missing" not in cfg.tagging:
    raise Exception("Missing delete_on_missing from tagging")
if "tagDirectory" not in cfg.tagging:
    raise Exception("Missing tagDirectory from tagging")

tagging_path = "./" + cfg.tagging["tagDirectory"] 
PathUtils.ensure_path(tagging_path)

if cfg.tagging["delete_on_missing"]:
    answer = input("Delete on missing tags is set, continue will delete untagged groups? (Y/y)> ")
    if answer not in ["y", "Y"]:
        print("Quitting program...")
        quit()
else:
    print("No groups will be deleted this run")

for subid in cfg.subscriptions:

    output = {
        "totalGroups" : 0,
        "untaggedGroups" : 0,
        "managedGroups" : 0,
        "ignoredGroups" : 0,
        "untagged" : []
    }

    print("Getting reource groups for", subid)
    groups = CmdUtils.get_command_output(
        [
            "az", 
            "group", 
            "list", 
            "--subscription", 
            subid
        ]
    )

    output["totalGroups"] = len(groups)
    for group in groups:
        ignored = False
        for ignored_name in cfg.tagging["ignored"]:
            if group["name"].lower().startswith(ignored_name):
                output["ignoredGroups"] += 1
                ignored = True

        if ignored:
            continue

        flag_untagged = False
        if group["managedBy"]: 
            output["managedGroups"] += 1
        elif group["tags"]:
            rg_tags = list(group["tags"].keys())
            rg_tags = [x.lower() for x in rg_tags]
            for tag in cfg.tagging["required_tags"]:
                if tag not in rg_tags:
                    flag_untagged = True
                    break
        else:
            flag_untagged = True

        if flag_untagged:
            output["untaggedGroups"] += 1
            output["untagged"].append(group["name"])
            if cfg.tagging["delete_on_missing"] is True:
                print("Deleting ", group["name"])
                # Note: the following code will work in many instances however
                # not in these:
                #   RG is locked
                #   Vault or other instance has soft delete enabled
                """
                UNCOMMENT WHEN ACTUALLY READY TO FIRE IT
                CmdUtils.get_command_output(
                    [
                        "az",
                        "group",
                        "delete",
                        "--name",
                        group["name"],
                        "--subscription",
                        subid,
                        "--no-wait",
                        "--yes"       
                    ]
                )
                """
           
    file_path = os.path.join(tagging_path, "{}.json".format(subid))
    with open(file_path, "w") as output_file:
        output_file.writelines(json.dumps(output, indent=4))