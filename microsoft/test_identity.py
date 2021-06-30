import json
from submaintenance.identity import AzIdentities


sub_id = "2eedf122-c960-4ddc-9146-ac93dbf8b2b0"

az_id = AzIdentities()

sub_level_users = az_id.get_users_sub_scope(sub_id)
print("Total Users", len(sub_level_users))

"""This takes a long time to check...but works
rem_count = az_id.clear_invalid_principals(sub_id)
print("Total Removed", rem_count)
"""

""" Get all role assignments in a form to dump to a file
overview = az_id.get_role_summary(sub_id)
print(json.dumps(overview, indent=4))
"""

s360report = "C:\\gitrepogrecoe\\SubscriptionPolicy\\src\\principals\\June29.csv"
res = az_id.clear_s360_principals(s360report)
print(json.dumps(res, indent=4))