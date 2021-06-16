"""
    Use this file to remove User roles from a subscription

    Required settings from configuartion.json is 
    roles["deleteUserRoles"]

    If true, user roles are deleted, if false, no user roles deleted
    
    In either case the only output will be to the command line.
"""
import sys
sys.path.insert(0, "..")
from utils.roles import AzRolesUtils
from utils.config import Configuration

cfg = Configuration("../../configuration.json")

if "deleteUserRoles" not in cfg.roles:
    raise Exception("Missing deleteUserRoles from roles")

# If shutting down, let user know
if cfg.roles["deleteUserRoles"]:
    answer = input("This action will delete user roles, do you want to continue? (Y/y)> ")
    if answer not in ["y", "Y"]:
        print("Quitting program...")
        quit()
else:
    print("No roles will be removed")

subcription_id = "989b90f7-da4f-41f9-84c9-44848802052d"
roles = AzRolesUtils.get_sub_roles(subcription_id, False)

for role in roles:
    if role.principalType == "User":
        print("User Role:", role.principalName)
        if cfg.roles["deleteUserRoles"]:
            role.delete()