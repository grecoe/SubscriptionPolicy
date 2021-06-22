import os
import json
import sys
from time import perf_counter
sys.path.insert(0, "..")
from utils.config import Configuration
from utils.pathutils import PathUtils
from utils.vm import ComputeUtil
from utils.login import AzLoginUtils


# Ensure a login and switch to SP if requested
try:
    AzLoginUtils.validate_login("../../credentials.json")
except Exception as ex:
    print(str(ex))
    quit()

# Load configuration
cfg = Configuration("../../configuration.json")

# Ensure we have data
if not len(cfg.subscriptions):
    raise Exception("Update configuration.json with sub ids")
if "computeDirectory" not in cfg.compute:
    raise Exception("Missing computeDirectory from compute")
if "stop_running" not in cfg.compute:
    raise Exception("Missing stop_running from compute")
if "include_managed_compute" not in cfg.compute:
    raise Exception("Missing include_managed_compute from compute")

# If shutting down, let user know
print("Configuration is to include managed computes: ", cfg.compute["include_managed_compute"] )
if cfg.compute["stop_running"]:
    answer = input("This action will shut down running compute, do you want to continue? (Y/y)> ")
    if answer not in ["y", "Y"]:
        print("Quitting program...")
        quit()
else:
    print("No compute will be shut down")

# Ensure we have the output path
usable_path = "./" + cfg.compute["computeDirectory"]
PathUtils.ensure_path(usable_path)

total_start = perf_counter()
stats = ComputeUtil.deallocate_vms(
            usable_path,
            cfg.subscriptions,
            cfg.compute["include_managed_compute"],
            cfg.compute["stop_running"]    
        )
total_end = perf_counter()

print("All processing took {}".format(total_end-total_start))
print("Total {} running {}".format(stats["total"], stats["running"]))