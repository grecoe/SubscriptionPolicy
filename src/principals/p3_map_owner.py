"""
Create a file for each owner of an SP that was paired with an
S360 SP. Output to configuration principals.ownerMap
"""
import os
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
map_path = "./" + cfg.principals["mapDirectory"]
PathUtils.ensure_path(owner_path)

# Load up all the map files
map_files = PathUtils.load_json_files(map_path)

if not len(map_files):
    raise Exception("Ensure you have run match_s360_to_subs.py")

# Go over each file and each entry and get the owner field which
# is either an email address (owned) or empty (probably AML) and
# map each SP ID to the owner.
owner_map = {}
for match in map_files:
    for sp in match:
        owner = sp["owner"]
        if not owner or len(owner) == 0:
            owner = "unknown"

        if owner not in owner_map:
            owner_map[owner] = []

        if sp["principalId"] not in owner_map[owner]:
            owner_map[owner].append(sp["principalId"])


# Using the map, create a file for each user/entity
# that owns SP's so we know who to contact
for entry in owner_map:
    path = os.path.join(owner_path, entry + ".json")
    with open(path, "w") as output:
        output.writelines(json.dumps(owner_map[entry],  indent=4))

print("Done")
