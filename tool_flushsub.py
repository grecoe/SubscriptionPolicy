"""
Use this script sparingly, this will clear all resource groups from a subscription

1. Ensure we have the right sub and make user verify
2. Collect groups and for each
    - Delete any present locks
    - Delete group
"""
from microsoft.submaintenance.utils import(
    AzLoginUtils,
    AzResourceGroupUtils
)

CREDENTIALS_FILE = "./credentials.json"
SUBSCRIPTION_TO_CLEAR = "YOUR_SUBSCRIPTION_ID_TO_CLEAR"

try:
    AzLoginUtils.validate_login(CREDENTIALS_FILE)
except Exception as ex:
    print(str(ex))
    quit()

cur_acct = AzLoginUtils.get_current_account()
if not cur_acct or cur_acct["id"] != SUBSCRIPTION_TO_CLEAR:
    print("Setting account...")
    AzLoginUtils.set_current_account(SUBSCRIPTION_TO_CLEAR)
    cur_acct = AzLoginUtils.get_current_account()

if not cur_acct:
    print("Problem retrieving account...")
    quit()

if cur_acct["id"] == SUBSCRIPTION_TO_CLEAR:
    response = input("Are you sure you want to clear {}? (Y/y) >".format(cur_acct["name"]))
    if response not in ["Y","y"]:
        print("You have chosen NOT to clear this subscription!")
        quit()
else:
    print("Error collecting the subscription", SUBSCRIPTION_TO_CLEAR)
    quit()

groups = AzResourceGroupUtils.get_groups(SUBSCRIPTION_TO_CLEAR)

print("Number of groups to clear:", len(groups))
if len(groups):
    for group in groups:
        if group["managedBy"]:
            print("Cannot delete managed group", group["name"])
        else:
            print("Deleting group: ", group["name"])
            AzResourceGroupUtils.delete_group(group["name"], SUBSCRIPTION_TO_CLEAR)

