"""
AGCI Has a problem with princippals as well and unsure how to map those to users. 

This script is used to pull their S360 report apart and create something actionable.
"""
import os
import json
import sys
sys.path.insert(0, "..")

from utils.csvloader import S360Reader
from utils.pathutils import PathUtils

"""
subscriptionName
subscription
servicePrincipal
principalId
roleScope - scope
role - text
roleId - identifier
"""

external_map_path = "./external_map"
PathUtils.ensure_path(external_map_path)

# This is the CSV output collected from s360/Lens with all the
# over priviledged principals
warnings = S360Reader.read_file("./anita.csv")

subscription_map = {}
subscription_delete_ps1 = {}

for warning in warnings:
    if warning.subscriptionName not in subscription_map:
        subscription_map[warning.subscriptionName] = {}
        subscription_delete_ps1[warning.subscriptionName] = []

    if warning.principalId not in subscription_map[warning.subscriptionName]:
        subscription_map[warning.subscriptionName][warning.principalId] = []


    sub_sp_list = subscription_map[warning.subscriptionName][warning.principalId]

    command = "az role assignment delete --assignee {} --scope {} --role {} --subscription {}".format(
                warning.principalId,
                warning.roleScope,
                warning.roleId,
                warning.subscription
            )
    subscription_delete_ps1[warning.subscriptionName].append(command)

    sub_sp_list.append(
        {
            "role" : warning.role,
            "roleScope" : warning.roleScope,
            "cleanup" : command
        }
    )


# Json listing them out
for sub in subscription_map:
    file_name = os.path.join(external_map_path, "{}.json".format(sub))
    with open(file_name, "w") as output_file:
        output_file.writelines(json.dumps(subscription_map[sub], indent=4))

# PS1 file to execute
for sub in subscription_delete_ps1:
    file_name = os.path.join(external_map_path, "{}.ps1".format(sub))
    with open(file_name, "w") as output_file:
        for command in subscription_delete_ps1[sub]:
            output_file.writelines(command + "\n")
