"""
This file assumes you have created all the mapping files you need
to map service princpals to.

You need to provide the output directory of the match_s360_to_subs.py
which if unchanged is raw_matched.
"""
import os
import sys
sys.path.insert(0, "..")
from utils.jsonloader import JsonFileUtil
from utils.cmdline import CmdUtils
from utils.pathutils import PathUtils
from utils.config import Configuration

# Load configuration
cfg = Configuration("../../configuration.json")

# This setting must be there AND we must be able to load them
if "mapDirectory" not in cfg.principals:
    raise Exception("Missing mapDirectory from principals")

# Load up all the map files
map_path = "./" + cfg.principals["mapDirectory"]
map_files = PathUtils.load_json_files(map_path)

if not len(map_files):
    raise Exception("Ensure you have run match_s360_to_subs.py")


# Principals to clear out
principals_to_clean = [
]

if not len(principals_to_clean):
    raise Exception("Provide some SP ID's to clear out")

# Walk all the files and for the principals to clean we build
# up a collection in the form
# {
# 	principalId : {
# 		subId :[list of cleanup calls]
# 	}
# }
cleanup_map = {}
for match in map_files:
    for id_to_clean in principals_to_clean:
        for sp in match:
            if sp["principalId"] == id_to_clean:
                if sp["principalId"] not in cleanup_map:
                    cleanup_map[sp["principalId"]] = {}

                if sp["subscription"] not in cleanup_map[sp["principalId"]]:
                    cleanup_map[sp["principalId"]][sp["subscription"]] = []

                if sp["cleanup"] not in cleanup_map[sp["principalId"]][sp["subscription"]]:
                    cleanup_map[sp["principalId"]][sp["subscription"]].append(sp["cleanup"])


# Now with the map we can start issuing deletion of the assignemnts
for principal in cleanup_map:
    for sub in cleanup_map[principal]:
        for cleanup in cleanup_map[principal][sub]:
            cleanup = cleanup.replace("'", "")
            cleanup = cleanup.replace('"', "")

            deletion_command = "{} --subscription {}".format(
                cleanup,
                sub
            )

            print("Removing principal {} from {}".format(
                principal,
                sub
            ))
            print("\t{}".format(deletion_command))

            #commands = deletion_command.split(' ')
            #CmdUtils.get_command_output(commands, False)
