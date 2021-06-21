import os
import sys
from time import perf_counter

sys.path.insert(0, "./src")
from src.utils.cmdline import CmdUtils


scripts = [
    {
        "description" : "CLEANUP: Check for required tags, see configuration.json tagging.delete_on_missing",
        "path" : "./src/tagging/",
        "script" : "check_tagging.py"
    },
    {
        "description" : "COMPUTE: Check for running computes, see configuration.json compute.stop_running",
        "path" : "./src/compute/",
        "script" : "stop_compute.py"
    },
    {
        "description" : "STORAGE: Enforce public blob access off on all storage accounts, see storage.forceUpdate",
        "path" : "./src/storage/",
        "script" : "update_storage.py"
    },
    {
        "description" : "KEYVAULT: Enforce soft delete",
        "path" : "./src/keyvault/",
        "script" : "enable_sd.py"
    }
]

root_path = os.getcwd()
print("Checking now")
for script in scripts:
    task_start = perf_counter()

    print(script["description"])
    
    os.chdir(script["path"])
    res = CmdUtils.get_command_output(["python", script["script"]], False)
    os.chdir(root_path)

    print("{}\nRunning Time:{}".format(
        script["description"], 
        (perf_counter() - task_start)
    ))

print("DONE")