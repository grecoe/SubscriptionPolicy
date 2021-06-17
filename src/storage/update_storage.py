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

Other options:
    --https-only {false, true}

    Logging: https://docs.microsoft.com/en-us/cli/azure/storage/logging?view=azure-cli-latest

    But we need account key or connection string

    az storage account show-connection-string -g MyResourceGroup -n MyStorageAccount

    OK
    az storage account show-connection-string -g NAME -n ACCNAME
    
    DID NOT WORK WITH JUST NAME
    az storage logging show --account-name NAME --services b

    OK GETS ALL
    az storage logging show --connection-string "CONN_STR"
"""
import os
import json
import sys
sys.path.insert(0, "..")
from utils.config import Configuration
from utils.storage import AzStorageUtil
from utils.pathutils import PathUtils
from utils.group import AzResourceGroup
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
if "storageSummaryDirectory" not in cfg.storage:
    raise Exception("Missing storageSummaryDirectory setting in storage.")
if "forceUpdate" not in cfg.storage:
    raise Exception("Missing forceUpdate setting in storage.")

# Ensure we have the output folder
usable_path = "./" + cfg.storage["storageSummaryDirectory"]
PathUtils.ensure_path(usable_path)


for subid in cfg.subscriptions:
    # Stats to collect
    account_overview = {
        "managedGroupStorage" : {"total" : 0, "open" : 0, "accounts" : []},
        "unmanagedGroupStorage" : {"total" : 0, "open" : 0, "accounts" : []},
    }

    print("Inspect subscripiton", subid)
    accounts = AzStorageUtil.list_accounts(subid)

    for account in accounts:
        print("\tInspect Storage", account["name"])

        group_info = AzResourceGroup.get_group(subid, account["resourceGroup"])
        blob_access_open = False

        if cfg.storage["forceUpdate"] == False:
            # Only get this flag if we aren't forcing update. Faster
            blob_access_open = AzStorageUtil.is_blob_access_public(
                subid,
                account["name"],
                account["resourceGroup"]
            )

        index = "managedGroupStorage" if group_info["managedBy"] is not None else "unmanagedGroupStorage"
        account_overview[index]["total"] += 1
        if blob_access_open or cfg.storage["forceUpdate"]:
            # Eitehr open or forced, do the update
            account_overview[index]["open"] += 1
            account_overview[index]["accounts"].append(account["name"])

            print("\tEnable logging")
            AzStorageUtil.enable_logging(
                subid,
                account["name"],
                account["resourceGroup"]
            )
            # Disable public blob AND enforce https
            print("\tUpdating blob access/https/logging")
            AzStorageUtil.disable_public_blob_access(
                subid,
                account["name"],
                account["resourceGroup"]
            )

        # Dump out the results for this sub
        file_path = os.path.join(usable_path, "{}.json".format(subid))
        with open(file_path, "w") as output_stats:
            output_stats.writelines(json.dumps(account_overview, indent=4))
