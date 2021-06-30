"""
Tasks to perform enabling soft delete on AKV. 

EnableSoftDelete (Force soft delete on all key vaults)

    "keyvault" : {
        "taskOutputDirectory" : "./logs/kevault_status",
        "availableTasks" : { 
            "EnableSoftDelete" : {
                "Descripton" :"Scans subscriptions and forces soft delete on for key vaults",
                "Parameters" : null
            }
        },
        "active_tasks" : {
            "EnableSoftDelete" : null
        } 
    },
"""
import os
import json
from microsoft.submaintenance.utils import(
    Configuration,
    AzLoginUtils,
    PathUtils,
    AzKeyVaultUtils
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
    "enablesoftdelete"
    ]

# Validate the minimum on the configuration
if not hasattr(configuration, "subscriptions") or len(configuration.subscriptions) == 0:
    raise Exception("Update configuration.json with sub ids")
if not hasattr(configuration, "keyvault"):
    raise Exception("Update configuration.json keyvault section")
if not configuration.compute["taskOutputDirectory"]:
    raise Exception("Update configuration.json compute.taskOutputDirectory section")

# Create output path for all tasks
task_output_path = PathUtils.ensure_path(configuration.keyvault["taskOutputDirectory"])

for task_name in configuration.keyvault["active_tasks"]:
    if task_name.lower() not in allowed_tasks:
        print("Unknown task {} skipping...".format(task_name))

    task_settings = configuration.keyvault["active_tasks"][task_name]

    if task_name.lower() == allowed_tasks[0]:
        print("Performing Key Vault Soft Delete task")
        stats = AzKeyVaultUtils.check_soft_delete_status(configuration.subscriptions)

        file_name = os.path.join(task_output_path, "vault_scan.json")
        with open(file_name, "w") as output:
            data = {
                "total_subs" : len(configuration.subscriptions),
                "total_vaults" : stats["total"],
                "unlocked_vaults" : stats["unlocked"]
            }
            output.writelines(json.dumps(data, indent=4))        
