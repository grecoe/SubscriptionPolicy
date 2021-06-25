import os
import json
import sys
sys.path.insert(0, "..")
from utils.config import Configuration
from utils.vault import AzKeyVaultUtils
from utils.login import AzLoginUtils


# Ensure a login and switch to SP if requested
try:
    AzLoginUtils.validate_login("../../credentials.json")
except Exception as ex:
    print(str(ex))
    quit()

# Load configuration
cfg = Configuration("../../configuration.json")

# Make sure we have subscriptions
if not len(cfg.subscriptions):
    raise Exception("Update configuration.json with sub ids")

stats = AzKeyVaultUtils.check_soft_delete_status(cfg.subscriptions)

with open("./vault_scan.json", "w") as output:
    data = {
        "total_subs" : len(cfg.subscriptions),
        "total_vaults" : stats["total"],
        "unlocked_vaults" : stats["unlocked"]
    }
    output.writelines(json.dumps(data, indent=4))

print("Done...")
