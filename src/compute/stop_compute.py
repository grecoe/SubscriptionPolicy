import os
import json
import sys
from time import perf_counter
sys.path.insert(0, "..")
from utils.config import Configuration
from utils.cmdline import CmdUtils
from utils.pathutils import PathUtils
from utils.vm import Compute, ComputeUtil

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
total_computes = 0
running_computes = 0
for subid in cfg.subscriptions:
    start = perf_counter()
    computes = ComputeUtil.get_compute(subid, cfg.compute["include_managed_compute"])
    stop = perf_counter()

    print("Took {} to get {}".format(
        stop-start,
        len(computes)
    ))

    report = ComputeUtil.parse_compute_to_report(computes)
    total_computes += report["overall"]["total"]
    running_computes += report["states"]["running"]

    file_name = os.path.join(usable_path, "{}.txt".format(subid))
    with open(file_name, "w") as output_file:
        output_file.writelines(json.dumps(report, indent=4))

    # If it has a powerState then it was included managed or not. Check
    # shutdown flag and if set, turn it off (deallocated)
    if cfg.compute["stop_running"]:
        running_vms = ComputeUtil.get_running_compute(computes)
        for rvm in running_vms:
            rvm.deallocate()

    break

total_end = perf_counter()
print("All processing took {}".format(total_end-total_start))
print("Total {} running {}".format(total_computes, running_computes))