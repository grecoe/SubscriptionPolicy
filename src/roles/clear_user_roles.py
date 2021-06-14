"""
    Use this file to remove User roles from a subscription
"""
import sys
sys.path.insert(0, "..")
from utils.roles import AzRolesUtils


subcription_id = "YOUR_SUB_ID"
roles = AzRolesUtils.get_sub_roles(subcription_id, False)

for role in roles:
    if role.principalType == "User":
        role.delete()