"""
Provide a list of groups and a sub id and just blindly delete
by removing locks first. 
"""
import json
import sys
sys.path.insert(0, "..")
from utils.login import AzLoginUtils
from utils.locks import AzLockUtils
from utils.group import AzResourceGroup


# Ensure a login and switch to SP if requested
try:
    AzLoginUtils.validate_login("../../credentials.json")
except Exception as ex:
    print(str(ex))
    quit()

sub_id = "sub id to clean"
groups = ["list of group names"]

print("Deleting {} groups from {}".format(
    len(groups),
    sub_id
))

unfound_groups = []
for group in groups:
    print("Delete ->", group)

    res = AzResourceGroup.get_group(sub_id, group)
    if not isinstance(res, dict):
        unfound_groups.append(group)
        continue


    # Get locks first
    locks = AzLockUtils.get_group_locks(group, sub_id)
    if locks and len(locks):
        for lock in locks:
            lock.delete()

    # Now the group - When ready
    AzResourceGroup.delete_group(group, sub_id)        

print("\n\nNot Found:\n")
print(json.dumps(unfound_groups, indent=4))