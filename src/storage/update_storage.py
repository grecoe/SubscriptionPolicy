"""
Inspect storage accounts 
    - IN a managed RG
    - Is Open (public blob store access)
    - Disable public blob store access

Now, it can be done a couple of ways, just blindy set the 
blob store public access to False requires only one call. 

If you want more, like the list above, it takes several calls
and is quite slow. For 700 storage accounts its ~45 minutes. 

It's marginally faster to just blindy set them, but it's still not
quick.
"""
import sys
sys.path.insert(0, "..")
from utils.config import Configuration
from utils.storage import AzStorageUtil
from utils.pathutils import PathUtils
from utils.login import AzLoginUtils


# Ensure a login and switch to SP if requested
try:
    AzLoginUtils.validate_login("../../credentials.json")
except Exception as ex:
    print(str(ex))
    quit()

# Load configuration
cfg = Configuration("../../configuration.json")

# Make sure we have subscriptions and settings
if not len(cfg.subscriptions):
    raise Exception("Update configuration.json with sub ids")
if "storageSummaryDirectory" not in cfg.storage:
    raise Exception("Missing storageSummaryDirectory setting in storage.")
if "forceUpdate" not in cfg.storage:
    raise Exception("Missing forceUpdate setting in storage.")

# Ensure we have the output folder
usable_path = "./" + cfg.storage["storageSummaryDirectory"]
PathUtils.ensure_path(usable_path)

# Now secure storage accounts (based on forceUpdate)
AzStorageUtil.secure_storage(
    usable_path,
    cfg.subscriptions,
    cfg.storage["forceUpdate"]
    )
