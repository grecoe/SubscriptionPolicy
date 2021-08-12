import os
import json
from enum import Enum
from microsoft.submaintenance.utils import (
    PathUtils, 
    AzLoginUtils,
    Configuration,
    AzKeyVaultUtils
)

CREDENTIALS_FILE = "./credentials.json"
CONFIGURATION_FILE = "./configuration.json"

# Ensure a login and switch to SP if requested
try:
    AzLoginUtils.validate_login(CREDENTIALS_FILE)
except Exception as ex:
    print(str(ex))
    quit()

# Load configuration and create instance of identities
configuration = Configuration(CONFIGURATION_FILE)
log_path = PathUtils.ensure_path(configuration.keyvault["taskOutputDirectory"])


purge_protected = 0
vault_details = {}
total_purged = 0

for sub_id in configuration.subscriptions:
    print("Processing", sub_id)
    deleted_vaults = AzKeyVaultUtils.list_deleted_vaults(sub_id)

    total_purged += len(deleted_vaults)
    print("There are", len(deleted_vaults), "vaults to purge....")

    for vault in deleted_vaults:

        can_delete = True
        if "purgeProtectionEnabled" in vault["properties"]: 
            if vault["properties"]["purgeProtectionEnabled"] == True:
                purge_protected += 1
                can_delete = False

        location = vault["properties"]["location"] 

        if sub_id not in vault_details:
            vault_details[sub_id] = {}

        if location not in vault_details[sub_id]:
            vault_details[sub_id][location] = 0

        vault_details[sub_id][location] += 1      

        if '/deletedVaults' in vault["id"] and can_delete:
            print("Purging -", vault["name"])
            result = AzKeyVaultUtils.purge_deleted_vault(
                sub_id, 
                vault["name"]
                )

stats = {
    "total" : total_purged,
    "purgeProtected" : purge_protected,
    "regional" : vault_details
}        

log_file = os.path.join(log_path, "purge_fault_status.json")
with open(log_file, "w") as output_log:
    output_log.writelines(json.dumps(stats, indent=4))