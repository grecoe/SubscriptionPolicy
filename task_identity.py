"""
Tasks to perform on identities, options are

ReportAssignments (list out all assignments on a sub to a file)
ClearUserAssignments (at sub level)
ClearInvalidPrincipals (SP's assigned but not found in AD)

Configuration needs to have the following (example)
    "identity" : {
        "taskOutputDirectory" : "./identity_summary",
        "availableTasks" : { 
            "ReportAssignments" : "Report all assignments to a file",
            "ClearUserAssignments" : "Remove all sub level user assignments", 
            "ClearInvalidPrincipals" : "Remove any SP that does not have an AAD entry"
        },
        "active_tasks" : {
            "ReportAssignments" : null,
            "ClearUserAssignments" : {
                "deleteAssignments" : false
            },
            "ClearInvalidPrincipals" : null
        }
    },
"""
import os
import json
from microsoft.submaintenance import AzIdentities
from microsoft.submaintenance.utils import(
    Configuration,
    AzLoginUtils,
    PathUtils
)

CREDENTIALS_FILE = "./credentials.json"
CONFIGURATION_FILE = "./configuration.json"

# Ensure a login and switch to SP if requested
try:
    AzLoginUtils.validate_login(CREDENTIALS_FILE)
except Exception as ex:
    print(str(ex))
    quit()

# Load configuration and create instance of identities
configuration = Configuration(CONFIGURATION_FILE)
az_identities = AzIdentities()

allowed_tasks = [
    "reportassignments",
    "clearuserassignments",
    "clearinvalidprincipals"]


# Validate the minimum on the configuration
if not hasattr(configuration, "subscriptions") or len(configuration.subscriptions) == 0:
    raise Exception("Update configuration.json with sub ids")
if not hasattr(configuration, "identity"):
    raise Exception("Update configuration.json identity section")
if not configuration.identity["taskOutputDirectory"]:
    raise Exception("Update configuration.json identity.taskOutputDirectory section")

# Create output path for all tasks
task_output_path = PathUtils.ensure_path(configuration.identity["taskOutputDirectory"])

# Iterate tasks 
for task_name in configuration.identity["active_tasks"]:
    if task_name.lower() not in allowed_tasks:
        print("Unknown task {} skipping...".format(task_name))

    task_settings = configuration.identity["active_tasks"][task_name]

    if task_name.lower() == allowed_tasks[0]:
        print("Performing ReportAssignments task")

        for sub_id in configuration.subscriptions:
            role_summary = az_identities.get_role_summary(sub_id)
            file_path = os.path.join(task_output_path, "{}.json".format(sub_id))
            with open(file_path, "w") as output_file:
                output_file.writelines(json.dumps(role_summary, indent=4))

    if task_name.lower() == allowed_tasks[1]:
        print("Clear user sub level assignments")
        stats = {"Found" : 0, "Removed" : 0, "Details" : {}}

        for sub_id in configuration.subscriptions:
            user_assignments = az_identities.get_users_sub_scope(sub_id)

            stats["Found"] += len(user_assignments)

            if "deleteAssignments" not in task_settings:
                raise Exception("Must have deleteAssignments in identity.active_tasks.ClearUserAssignments in configuration")

            perform_delete = task_settings["deleteAssignments"]
            if configuration.automation:
                perform_delete = True

            for user_assignment in user_assignments:
                if sub_id not in stats["Details"]:
                    stats["Details"][sub_id] = []
                stats["Details"][sub_id].append(user_assignment.principalName)

                if perform_delete:
                    stats["Removed"] += 1
                    user_assignment.delete()

        file_path = os.path.join(task_output_path, "sub_scoped_users.json")
        with open(file_path, "w") as output_file:
            output_file.writelines(json.dumps(stats, indent=4))

    if task_name.lower() == allowed_tasks[2]:
        print("Clear invalid service principals")
        stats = {}

        for sub_id in configuration.subscriptions:
            stats[sub_id] = az_identities.clear_invalid_principals(sub_id)

        file_path = os.path.join(task_output_path, "invalid_principals.json")
        with open(file_path, "w") as output_file:
            output_file.writelines(json.dumps(stats, indent=4))

