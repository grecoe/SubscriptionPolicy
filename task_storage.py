"""
Tasks to perform enabling security on storage accounts. 

EnableSecurity (Disable public blob, enable https only, enable logging)

    "storage" : {
        "taskOutputDirectory" : "./logs/status_status",
        "availableTasks" : { 
            "EnableSecurity" : {
                "Descripton" :"Scans subscriptions for storage and optionally force updates public blob, logging, and https",
                "Parameters" : {
                    "forceUpdate" : "Flag on whether to force security or not, overridden by automation if true"
                }
            }
        },
        "active_tasks" : {
            "EnableSecurity" : {
                "forceUpdate" : false
            }
        } 
    }
"""
import os
import json
from microsoft.submaintenance.utils import(
    Configuration,
    AzLoginUtils,
    PathUtils,
    AzStorageUtil
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
    "enablesecurity"
    ]

# Validate the minimum on the configuration
if not hasattr(configuration, "subscriptions") or len(configuration.subscriptions) == 0:
    raise Exception("Update configuration.json with sub ids")
if not hasattr(configuration, "storage"):
    raise Exception("Update configuration.json keyvault section")
if not configuration.storage["taskOutputDirectory"]:
    raise Exception("Update configuration.json storage.taskOutputDirectory section")

# Create output path for all tasks
task_output_path = PathUtils.ensure_path(configuration.storage["taskOutputDirectory"])

for task_name in configuration.storage["active_tasks"]:
    if task_name.lower() not in allowed_tasks:
        print("Unknown task {} skipping...".format(task_name))

    task_settings = configuration.storage["active_tasks"][task_name]

    if task_name.lower() == allowed_tasks[0]:
        print("Performing Storage Security task")
        
        if "forceUpdate" not in task_settings:
            raise Exception("Must have forceUpdate in storage.active_tasks.EnableSecurity in configuration")

        force_update = task_settings["forceUpdate"]
        if configuration.automation:
            force_update = True

        # Now secure storage accounts (based on forceUpdate)
        AzStorageUtil.secure_storage(
            task_output_path,
            configuration.subscriptions,
            force_update
        )

