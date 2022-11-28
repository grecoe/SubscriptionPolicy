

import os
import json
import typing
import logging
from microsoft.submaintenance import AzIdentities
from microsoft.submaintenance.utils import(
    Configuration,
    AzLoginUtils
)
from microsoft.submaintenance.utils.grouputils import (
    UserAssignment,
    GroupConfiguration
)

# MCIReaderTest
# MCIExternalReaderTest

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

  
# --------------------------------------------------------------
# Application code
# --------------------------------------------------------------

# Load up the groups 
CREDENTIALS_FILE = "./credentials.json"
CONFIGURATION_FILE = "./configuration.json"
config = "./groupconfiguration.json"

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

# Load configuration and create instance of identities and load groups
configuration = Configuration(CONFIGURATION_FILE)
az_identities = AzIdentities()
group_config = GroupConfiguration(az_identities, config)

# Get the users
user_assignments: typing.List[UserAssignment] = []
sub_role_summary = az_identities.get_role_summary(group_config.subscription)
for rs in sub_role_summary:
    user_assignments.append(UserAssignment(az_identities, rs, sub_role_summary[rs]))

    
print("Separate users from all assignements")
users = [x for x in user_assignments if x.type == "User"]

# For each role, get the users that might be associated with it
failed_loads: typing.Dict[str, typing.List[UserAssignment]] = {}

for role in group_config.roles:
    failed_users = []

    info_msg = "Check users for role definition : {}".format(role.name) 
    logging.info(info_msg)
    print(info_msg)
    current = 1
    total_adds = 0

    for user in users:
        print(role.name, ": {} of {}".format(current, len(users)))
        current += 1

        if user.supports_role_definition(role.name):
            if user.get_oid() is None:
                failed_users.append(user)
            else:
                role.add_user_to_role_group(user)
                total_adds += 1

    failed_users = [x.name for x in failed_users]
    failed_user_message = "Role: {}\nFailed User:\n {}".format(
        role.name, 
        json.dumps(failed_users, indent=4)
    )            
    logging.info("Added {} users for role definition {} to groups".format(
        total_adds, 
        role.name
    ))
    logging.warning(failed_user_message)
