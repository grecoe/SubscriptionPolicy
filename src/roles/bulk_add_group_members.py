import os
import sys
import json
sys.path.insert(0, "..")
from utils.cmdline import CmdUtils

aad_group_name = "AAD group to add members to"
users = [
    "list of users to add. Email address or objid"
    ]

unique = list(set(users))
print(len(unique))    

def get_info(user_name):
    command = "az ad user show --id {}".format(user_name)
    return CmdUtils.get_command_output(command.split(" "))

def add_user_to_group(group_name, user_id):
    command = "az ad group member add --group {} --member-id {}".format(
      group_name,
      user_id  
    )
    CmdUtils.get_command_output(command.split(" "))

groups = {}
for user in unique:
    info = get_info(user)

    if info:
        print("Add ", user)
        add_user_to_group(aad_group_name, info["objectId"])
