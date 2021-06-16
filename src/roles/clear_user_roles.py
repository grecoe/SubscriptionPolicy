"""
    Use this file to remove User roles from a subscription
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

# Energy
#subcription_id = "789908e0-5fc2-4c4d-b5f5-9764b0d602b3"
# FSI
#subcription_id = "1b365fe2-5882-4935-bd81-8027e0816b45"
# Energy
# subcription_id = "789908e0-5fc2-4c4d-b5f5-9764b0d602b3"
# Supply Chain
subcription_id = "6187b663-b744-4d24-8226-7e66525baf8f"
roles = AzRolesUtils.get_sub_roles(subcription_id, False)

for role in roles:
    if role.principalType == "User":
        print(role.principalName)
        if cfg.roles["deleteUserRoles"]:
            print("Delete role!")
            #role.delete() Really making sure we don't accidentally delete during testing