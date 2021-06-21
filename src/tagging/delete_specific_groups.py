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

sub_id = "2eedf122-c960-4ddc-9146-ac93dbf8b2b0"
groups = [
        "devops-test-28735",
        "devops-test-27548",
        "devops-test-8686",
        "devops-test-20434",
        "devops-test-5708",
        "devops-test-11361",
        "devops-test-29141",
        "devops-test-649",
        "devops-test-20333",
        "devops-test-9005",
        "devops-test-31062",
        "devops-test-20210",
        "devops-test-27805",
        "devops-test-14183",
        "devops-test-14078",
        "devops-test-18907",
        "devops-test-7417",
        "devops-test-11719",
        "devops-test-24377",
        "devops-test-19011",
        "devops-test-6473",
        "devops-test-9574",
        "devops-test-7902",
        "devops-test-21057",
        "devops-test-21427",
        "devops-test-13352",
        "devops-test-510",
        "devops-test-14155",
        "devops-test-15912",
        "devops-test-28492",
        "devops-test-31454",
        "devops-test-16651",
        "devops-test-26784",
        "devops-test-30702",
        "devops-test-3086",
        "devops-test-24313",
        "devops-test-2541",
        "devops-test-14938",
        "devops-test-16368",
        "devops-test-8775",
        "devops-test-17951",
        "devops-test-11554",
        "devops-test-24273",
        "devops-test-20894",
        "devops-test-31394"
]

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