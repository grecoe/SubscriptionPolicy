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

total = 0
unlocked = []
for subid in cfg.subscriptions:
    vaults = AzKeyVaultUtils.list_vaults(subid)

    if vaults and len(vaults):
        total += 1
        for vault in vaults:
            props = AzKeyVaultUtils.get_vault(vault["name"], subid)
            sd_enabled = props["properties"]["enableSoftDelete"]
            print(vault["name"], "->", sd_enabled)
            if not sd_enabled:
                unlocked.append(vault["name"])                
                AzKeyVaultUtils.enable_softdelete(vault["name"], subid)


with open("./vault_scan.json", "w") as output:
    data = {
        "total_subs" : len(cfg.subscriptions),
        "total_vaults" : total,
        "unlocked_vaults" : unlocked
    }
    output.writelines(json.dumps(data, indent=4))

print("Done...")
