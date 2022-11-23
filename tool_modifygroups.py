"""
When you want to finally start organizing your users into AAD groups and block out 
individual access, this app can help. 

Open groupconfiguration.json and make the following adjustments

- subscription: One subscription ID in which you want to scan for individual users.
- groups:
    Key (role definition name) : Value (AAD Group to add users to)

The app scans the sub and for any role definitions that have a mapping to an AAD group,
users (only) found with that role definition are added (if not already present) to the
associated AAD group. 

The code DOES NOT MODIFY any Azure Role Assignments. It is up to the operator to then delete
by hand the individual role assignments on the subscription itself. 

A log file ./identityassignmnet.log is generated. At the end you will see what, if any,
assignments failed to be created. 
"""

import os
import json
import logging
from microsoft.submaintenance import AzIdentities
from microsoft.submaintenance.utils import(
    Configuration,
    AzLoginUtils
)

#------------------------------------------
# Set up logging
#------------------------------------------
if os.path.exists("./identityassignment.log"):
    os.remove("./identityassignment.log")

logging.basicConfig(
    filename="./identityassignment.log",
    encoding="utf-8",
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S'
)

CREDENTIALS_FILE = "./credentials.json"
CONFIGURATION_FILE = "./configuration.json"
GROUP_CONFIGURATION_FILE = "./groupconfiguration.json"

#------------------------------------------
# Ensure we have an identity to use, for 
# this you need az login with rights to the
# sub you have configured.
#------------------------------------------
try:
    AzLoginUtils.validate_login(CREDENTIALS_FILE)
except Exception as ex:
    print(str(ex))
    quit()

# Load configuration and create instance of identities
configuration = Configuration(CONFIGURATION_FILE)
group_configuration = Configuration(GROUP_CONFIGURATION_FILE)
az_identities = AzIdentities()

#------------------------------------------
# Load configured group memmbers
#------------------------------------------
print("Collect group information")
group_info = {}
for role in group_configuration.groups:
    if group_configuration.groups[role] is not None:
        logging.info("Collect members for: {}".format(group_configuration.groups[role]))
        if role not in group_info:
            group_info[role] = {
                "group" : group_configuration.groups[role], 
                "members" : []
            }

            members = az_identities.get_group_members(group_configuration.groups[role])
            for member in members:
                if member.objectId not in group_info[role]["members"]:
                    group_info[role]["members"].append(member.objectId)


#------------------------------------------
# Scan subscription and make assignments
#------------------------------------------
logging.info("Scanning subscription: {}".format(group_configuration.subscription))
print("Getting role assignments on subscription")
sub_role_summary = az_identities.get_role_summary(group_configuration.subscription)
#print(list(sub_role_summary.keys()))

current_user = 1
total_users = len(sub_role_summary)
un_assigned = {}
total_assignments = {}
for rs in sub_role_summary:
    print("Organizing {} of {}".format(current_user, total_users))
    current_user += 1

    # Have to be able to look the user up in AAD and get an object ID
    # but no sense looking if it's not an indivudual user, so verify 
    # that before proceeding.
    user_info = None
    user_assignments = [x["roleDefinitionName"] for x in sub_role_summary[rs]]
    p_types = [x["principalType"] for x in sub_role_summary[rs]]
    if "User" not in p_types:
        logging.warning("{} is a {} and will be skipped".format(
                rs,
                list(set(p_types))
            )
        )
        continue

    # If here, it's a user and we need to get it's object ID
    # which is required for group assignment
    logging.info("Processing: {}".format(rs))
    
    try:
        user_info = az_identities.get_aad_user_info(rs)
    except Exception as ex:
        un_assigned[rs] = user_assignments
        logging.error("Exception looking up user: {}".format(rs))
        logging.warning("Unable to make assignemts for {} on {}".format(
            rs,
            user_assignments
        ))
        logging.error(ex)
        continue

    if not user_info or user_info.objectId is None:
        un_assigned[rs] = user_assignments
        logging.error("Failed to look up user: {}".format(rs))
        logging.warning("Unable to make assignemts for {} on {}".format(
            rs,
            user_assignments
        ))
        continue

    # We have a user fully, now go through the role assignments and 
    # see if"
    # 1. We have a group for it
    # 2. The user is not in it
    # if 1 and 2 are true, add user to the group. 
    for assignment in sub_role_summary[rs]:
        role_def = assignment["roleDefinitionName"]
        if role_def in group_info:
            if user_info.objectId not in group_info[role_def]["members"]:
                logging.info("Adding user {} with objid {} to group {}".format(
                    rs,
                    user_info.objectId, 
                    group_info[role_def]["group"]
                ))

                group_info[role_def]["members"].append(user_info.objectId)
                # Now add them
                az_identities.add_group_member(group_info[role_def]["group"], user_info.objectId)
                if group_info[role_def]["group"] not in total_assignments:
                    total_assignments[group_info[role_def]["group"]] = 0
                total_assignments[group_info[role_def]["group"]] += 1

logging.info("Total Succesful Assignments")
logging.warning(json.dumps(total_assignments, indent=4))
logging.warning("Unassigned Due To User Lookup Failures")
logging.warning(json.dumps(un_assigned, indent=4))
print("Done")