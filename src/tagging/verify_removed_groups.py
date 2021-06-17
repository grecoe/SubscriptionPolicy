"""
Verify the removal of groups that were picked up with the check_tagging script.

Just determines if they are there or not and reports so they can be hand inspected.
"""
import os
import json
import sys
sys.path.insert(0, "..")
from utils.login import AzLoginUtils
from utils.config import Configuration
from utils.pathutils import PathUtils
from utils.jsonloader import JsonFileUtil
from utils.group import AzResourceGroup


# Ensure a login and switch to SP if requested
try:
    AzLoginUtils.validate_login("../../credentials.json")
except Exception as ex:
    print(str(ex))
    quit()

# Load configuration
cfg = Configuration("../../configuration.json")

# Ensure we have data
if "tagDirectory" not in cfg.tagging:
    raise Exception("Missing tagDirectory from tagging")

# Load up the data from the check_tagging script
tagging_path = "./" + cfg.tagging["tagDirectory"] 
file_paths = PathUtils.get_files_in_path(tagging_path)

loaded_paths = {}
for file_path in file_paths:
    path_parts = os.path.split(file_path)
    sub_id = path_parts[1][:path_parts[1].index('.')] 
    loaded_paths[sub_id] = JsonFileUtil.read_file_as_json(file_path)


# Now go through each and see if they exist or not. Script WILL output a lot of
# errors if the check_tagging dumped the groups, but results of what's left pops
# out at the end. This may run slow depending on the number of groups to check.
undeleted_groups = {}
for sub_id in loaded_paths:
    print(sub_id)
    undeleted_groups[sub_id] = []
    for group_name in loaded_paths[sub_id]['untagged']:
        res = AzResourceGroup.group_exists(sub_id, group_name)
        if res:
            undeleted_groups[sub_id].append(group_name)
    break

print("\n\nUndeleted ->")
print(json.dumps(undeleted_groups, indent=4))
