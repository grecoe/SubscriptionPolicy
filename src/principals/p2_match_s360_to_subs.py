"""
Map S360 principals with the sub and collect owner information.

NOTE> Requires that you first download the CSV from S360, see ReadMe 
and run get_roles.py first.
"""
import os
import json
import sys
sys.path.insert(0, "..")

from utils.csvloader import S360Reader
from utils.jsonloader import JsonFileUtil
from utils.cmdline import CmdUtils
from utils.pathutils import PathUtils
from utils.config import Configuration

cfg = Configuration("../../configuration.json")

# Ensure we have data
if not len(cfg.subscriptions):
    raise Exception("Update configuration.json with sub ids")
if "mapDirectory" not in cfg.principals:
    raise Exception("Missing mapDirectory from principals")
if "roleDirectory" not in cfg.principals:
    raise Exception("Missing roleDirectory from principals")

role_path = "./" + cfg.principals["roleDirectory"] 
map_path = "./" + cfg.principals["mapDirectory"]
PathUtils.ensure_path(map_path)


# This is the CSV output collected from s360/Lens with all the
# over priviledged principals
warnings = S360Reader.read_file("./June18.csv")

# With the S360 list, iterate over the subscriptions to create
# a file for each sub. 
count = 0
for sub in cfg.subscriptions:
    print("Matching S360 to actual sub", sub)
    sub_file = os.path.join(role_path, "{}.json".format(sub))
    applied = JsonFileUtil.read_file_as_generic_objects(sub_file)

    matches = []
    for warning in warnings:
        if warning.principalId in applied:

            # Get the service principal
            # az ad sp owner list --id ID
            """
            Slash and burn policy, don't care who the user is.
            owners = ""
            try:
                owner = CmdUtils.get_command_output([
                    "az",
                    "ad",
                    "sp",
                    "owner",
                    "list",
                    "--id",
                    warning.principalId])

                for own in owner:
                    if "mail" in own:
                        owners += own["mail"] + " "
                    else:
                        owners += own["objectId"] + " "
            except Exception as ex:
                print("Failed to get owner, using id")
                onwers = "UNK_" + warning.principalId
            """

            command = "az role assignment delete --assignee {} --scope {} --role {}".format(
                warning.principalId,
                applied[warning.principalId].scope,
                applied[warning.principalId].roleDefinitionId
            )

            warned = {
                "principalId" : warning.principalId,
                "applicationId" : warning.applicationId,
                "principalName" : applied[warning.principalId].principalName,
                "owner" : warning.subscription,
                "role" : applied[warning.principalId].roleDefinitionName,
                "subscription" : warning.subscription,
                "cleanup" : command
            }
            matches.append(warned)

    print("Matched - ", len(matches))
    matched_output = os.path.join(map_path, "{}.json".format(sub))
    with open(matched_output, "w") as results:
        results.writelines(json.dumps(matches, indent=4))
