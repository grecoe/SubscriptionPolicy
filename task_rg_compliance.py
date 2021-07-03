"""
Tasks to perform on identities, options are

EnforceCompliance (deletes on flag true or reports on non compliant RGs)
DeleteGroups (deletes specified groups from specified sub)

    "groupCompliance" : {
        "taskOutputDirectory" : "./logs/group_compliance",
        "availableTasks" : { 
            "EnforceCompliance" : "Remove groups not meeting a specific rule set",
            "DeleteGroups" : "Non automatable, fill in sub ID and groups to remove"
        },
        "active_tasks" : {
            "EnforceCompliance" : {
                "required_tags": ["alias"],
                "ignored" : ["cleanupservice", "defaultresourcegroup","networkwatcherrg", "visualstudioonline-", "cloud-shell-storage-"],
                "delete_on_missing" : false
            },
            "DeleteGroups" : {
                "subscription" : "YOUR_SUB_ID",
                "groups" : [
                    "devops-test-15449",
                    "devops-test-24407",
                    "devops-test-29027",
                    "devops-test-4715"
                ]
            }
        }
    },

"""
import os
import json
from microsoft.submaintenance import AzGroupCompliance
from microsoft.submaintenance.utils import(
    Configuration,
    AzLoginUtils,
    PathUtils,
    AzResourceGroupUtils
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

allowed_tasks = [
    "enforcecompliance",
    "deletegroups"]

# Validate the minimum on the configuration
if not hasattr(configuration, "subscriptions") or len(configuration.subscriptions) == 0:
    raise Exception("Update configuration.json with sub ids")
if not hasattr(configuration, "groupCompliance"):
    raise Exception("Update configuration.json groupCompliance section")
if not configuration.groupCompliance["taskOutputDirectory"]:
    raise Exception("Update configuration.json groupCompliance.taskOutputDirectory section")

# Create output path for all tasks
task_output_path = PathUtils.ensure_path(configuration.groupCompliance["taskOutputDirectory"])

delete_groups_flag_set = False
delete_groups_flag = False

# Iterate tasks 
group_compliance = AzGroupCompliance()
for task_name in configuration.groupCompliance["active_tasks"]:
    if task_name.lower() not in allowed_tasks:
        print("Unknown task {} skipping...".format(task_name))

    task_settings = configuration.groupCompliance["active_tasks"][task_name]


    if task_name.lower() == allowed_tasks[0]:
        print("Performing GroupCompliance task")

        if "required_tags" not in task_settings:
            raise Exception("Must have required_tags in groupCompliance.active_tasks.EnforceCompliance in configuration")
        if "ignored" not in task_settings:
            raise Exception("Must have ignored in groupCompliance.active_tasks.EnforceCompliance in configuration")
        if "delete_on_missing" not in task_settings:
            raise Exception("Must have delete_on_missing in groupCompliance.active_tasks.EnforceCompliance in configuration")

        if not delete_groups_flag_set:
            delete_groups_flag_set = True
            if configuration.automation:
                print("Automation will bypass asking for permission....")
                delete_groups_flag = True
            elif task_settings["delete_on_missing"]:
                delete_groups_flag = True
                resp = input("Delete untagged groups (Y/y)? > ")
                if resp.lower() != "y":
                    delete_groups_flag = False

        for sub_id in configuration.subscriptions:
            filtered_groups = group_compliance.get_filtered_groups(
                sub_id,
                task_settings["ignored"],
                task_settings["required_tags"]
            )
            

            if delete_groups_flag:
                for group in filtered_groups.untagged:
                    AzResourceGroupUtils.delete_group(group, sub_id)

            file_path = os.path.join(task_output_path, "{}.json".format(sub_id))
            with open(file_path, "w") as output_file:
                output_file.writelines(json.dumps(filtered_groups.__dict__, indent=4))

    if task_name.lower() == allowed_tasks[1]:
        print("Performing DeleteGroups task")
        print(json.dumps(task_settings, indent=4))

        if "subscription" not in task_settings:
            raise Exception("Must have subscription in groupCompliance.active_tasks.DeleteGroups in configuration")
        if "groups" not in task_settings:
            raise Exception("Must have groups in groupCompliance.active_tasks.DeleteGroups in configuration")

        if len(task_settings["groups"]) == 0:
            print("No groups were identified to be deleted")
        else:
            for group in task_settings["groups"]:
                AzResourceGroupUtils.delete_group(group, task_settings["subscription"])
