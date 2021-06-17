"""
    Use this file to remove User roles from a subscription

    Required settings from configuartion.json is 
    roles["deleteUserRoles"] <- Flag indicating whether to delete or not
    roles["clearRolesSubId] <- the sub to remove user roles from

    If true, user roles are deleted, if false, no user roles deleted
    
    In either case the only output will be to the command line.
"""
import sys
sys.path.insert(0, "..")
from utils.roles import AzRolesUtils
from utils.config import Configuration
from utils.login import AzLoginUtils

# Ensure a login and switch to SP if requested
try:
    AzLoginUtils.validate_login("../../credentials.json")
except Exception as ex:
    print(str(ex))
    quit()

# Get configuration for run
cfg = Configuration("../../configuration.json")

if "deleteUserRoles" not in cfg.roles:
    raise Exception("Missing deleteUserRoles from roles")
if "clearRolesSubId" not in cfg.roles:
    raise Exception("Missing clearRolesSubId from roles")


# If shutting down, let user know
if cfg.roles["deleteUserRoles"]:
    answer = input("This action will delete user roles, do you want to continue? (Y/y)> ")
    if answer not in ["y", "Y"]:
        print("Quitting program...")
        quit()
else:
    print("No roles will be removed")

subcription_id = cfg.roles["clearRolesSubId"]
print("Scanning sub - ", subcription_id)
roles = AzRolesUtils.get_sub_roles(subcription_id, False)

for role in roles:
    if role.principalType == "User":
        print("User Role:", role.principalName if role.principalName else role.principalId)
        if cfg.roles["deleteUserRoles"]:
            role.delete()