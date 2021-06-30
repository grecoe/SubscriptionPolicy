"""
Tasks to perform deallocation of VMs. 

DeallocateUserCompute (Deallocates VM's)

    "compute" : {
        "taskOutputDirectory" : "./logs/compute_status",
        "availableTasks" : { 
            "DeallocateUserCompute" : {
                "Descripton" :"Deallocate VMs not in managed group",
                "Parameters" : {
                    "include_managed_compute" : "boolean to look at managed compute as well",
                    "stop_running" : "Flag on whether to dealloate or not, overridden by automation if true"
                }
            }
        },
        "active_tasks" : {
            "DeallocateUserCompute" : {
                "include_managed_compute" : false,
                "stop_running" : false
            }
        } 
    },

"""
from microsoft.submaintenance.utils import(
    Configuration,
    AzLoginUtils,
    PathUtils,
    ComputeUtil
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
    "deallocateusercompute"
    ]

# Validate the minimum on the configuration
if not hasattr(configuration, "subscriptions") or len(configuration.subscriptions) == 0:
    raise Exception("Update configuration.json with sub ids")
if not hasattr(configuration, "compute"):
    raise Exception("Update configuration.json compute section")
if not configuration.compute["taskOutputDirectory"]:
    raise Exception("Update configuration.json compute.taskOutputDirectory section")

# Create output path for all tasks
task_output_path = PathUtils.ensure_path(configuration.compute["taskOutputDirectory"])

for task_name in configuration.compute["active_tasks"]:
    if task_name.lower() not in allowed_tasks:
        print("Unknown task {} skipping...".format(task_name))

    task_settings = configuration.compute["active_tasks"][task_name]

    if task_name.lower() == allowed_tasks[0]:
        print("Performing Compute Deallocation task")

        if "include_managed_compute" not in task_settings:
            raise Exception("Must have include_managed_compute in compute.active_tasks.DeallocateUserCompute in configuration")
        if "stop_running" not in task_settings:
            raise Exception("Must have stop_running in compute.active_tasks.DeallocateUserCompute in configuration")

        stop_machines_flag = False
        if configuration.automation:
            print("Automation will bypass asking for permission....")
            stop_machines_flag = True
        elif task_settings["stop_running"]:
            resp = input("Deallocate running machines (Y/y)? > ")
            if resp.lower() != "y":
                stop_machines_flag = False

        # Wrapped this up already....
        ComputeUtil.deallocate_vms(
            task_output_path,
            configuration.subscriptions,
            task_settings["include_managed_compute"],
            stop_machines_flag
        )