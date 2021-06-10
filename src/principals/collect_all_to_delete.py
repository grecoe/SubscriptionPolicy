# Collect all from the raw_sp_owners for the clean_principals.py script
import json
import sys
sys.path.insert(0, "..")
from utils.config import Configuration
from utils.pathutils import PathUtils

cfg = Configuration("../../configuration.json")

# Ensure we have data
if not len(cfg.subscriptions):
    raise Exception("Update configuration.json with sub ids")
if "mapDirectory" not in cfg.principals:
    raise Exception("Missing mapDirectory from principals")
if "ownerMap" not in cfg.principals:
    raise Exception("Missing roleDirectory from principals")

# Get paths and ensure owner_path exists for output
owner_path = "./" + cfg.principals["ownerMap"] 

# Load up all the map files
map_files = PathUtils.load_json_files(owner_path)

if not len(map_files):
    raise Exception("Ensure you have run match_s360_to_subs.py")

print(len(map_files))
all = []
for mapf in map_files:
    all.extend(mapf)

with open("./killall.json", "w") as output:
    output.write(json.dumps(all, indent=4))

