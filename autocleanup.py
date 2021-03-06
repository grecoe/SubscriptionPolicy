import os
from time import perf_counter
from microsoft.submaintenance.utils import CmdUtils
from microsoft.submaintenance.utils import PathUtils


scripts = [
    {
        "description" : "CLEANUP: Check for required tags, see configuration.json groupCompliance",
        "script" : "./task_rg_compliance.py"
    },
    {
        "description" : "IDENTITY: Clean up user roles and dead service principals, see configuration.json identity",
        "script" : "./task_identity.py"
    },
    {
        "description" : "COMPUTE: Check for running computes, see configuration.json compute",
        "script" : "./task_compute.py"
    },
    {
        "description" : "STORAGE: Enforce public blob access off on all storage accounts, see storage",
        "script" : "./task_storage.py"
    },
    {
        "description" : "KEYVAULT: Purge deleted key vaults",
        "script" : "./tool_purge_sd_vaults.py"
    },
    {
        "description" : "KEYVAULT: Enforce soft delete see configuration.json keyvault",
        "script" : "./task_keyvaults.py"
    }
]

root_path = os.getcwd()
print("Checking now")
for script in scripts:
    task_start = perf_counter()

    print(script["description"])
    res = CmdUtils.get_command_output(["python", script["script"]], False)

    log_file = PathUtils.ensure_path("./logs")
    log_file = os.path.join(log_file, "{}.log".format(script["script"]))
    with open(log_file, "w") as output_log:
        output_log.write(res)
        output_log.write("\nSTDERR\n")
        output_log.write(CmdUtils.get_last_errors())

    print("{}\nRunning Time:{}".format(
        script["description"], 
        (perf_counter() - task_start)
    ))

print("DONE")