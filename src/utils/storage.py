import json
import os
from .group import AzResourceGroup
from .cmdline import CmdUtils

class AzStorageUtil:
    @staticmethod
    def list_accounts(sub_id: str):
        command = "az resource list --resource-type Microsoft.Storage/storageAccounts --subscription {}".format(
            sub_id
        )

        return CmdUtils.get_command_output(command.split(' '))

    @staticmethod
    def get_account_details(sub_id, storage_acc, resource_group):
        command = "az storage account show --name {} --resource-group {} --subscription {}".format(
            storage_acc, 
            resource_group,
            sub_id
        )

        return CmdUtils.get_command_output(command.split(' '))

    @staticmethod
    def is_blob_access_public(sub_id, storage_acc, resource_group):
        command = "az storage account show --name {} --resource-group {} --subscription {} --query allowBlobPublicAccess".format(
            storage_acc, 
            resource_group,
            sub_id
        )

        value = CmdUtils.get_command_output(command.split(' '))

        # If there is no value then the default is enabled
        return_val = True
        if isinstance(value, bool):
            return_val = value
        elif isinstance(value, str):
            if not len(value):
                return_val = True
            else:
                return_val = bool(value)

        return return_val

    @staticmethod
    def disable_public_blob_access(sub_id, storage_acc, resource_group):
        command = "az storage account update --name {} --resource-group {} --subscription {} --allow-blob-public-access false --https-only true".format(
            storage_acc,
            resource_group,
            sub_id
        )

        CmdUtils.get_command_output(command.split(' '), False)

    @staticmethod
    def _enable_logging(connection_string, sub_id, services="bqt", logtype="rwd"):
        command = [
            "az", 
            "storage", 
            "logging", 
            "update", 
            "--log",
            logtype,
            "--retention",
            "10",
            "--services",
            services,
            "--connection-string",
            connection_string,
            "--subscription",
            sub_id
        ]
        CmdUtils.get_command_output(command)

    @staticmethod
    def enable_logging(sub_id, storage_acc, resource_group):
        command = "az storage account show-connection-string -g {} -n {} --subscription {}".format(
            resource_group,
            storage_acc,
            sub_id
        )

        output = CmdUtils.get_command_output(command.split(" "))

        if isinstance(output, dict):
            connection_string = output["connectionString"]
            AzStorageUtil._enable_logging(connection_string, sub_id)

    @staticmethod 
    def secure_storage(logging_path:str, subscriptions: list, force_update:bool):
        for subid in subscriptions:
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

                # Only get this flag if we aren't forcing update. Faster
                blob_access_open = False
                if force_update == False:
                    blob_access_open = AzStorageUtil.is_blob_access_public(
                        subid,
                        account["name"],
                        account["resourceGroup"]
                    )

                index = "managedGroupStorage" if group_info["managedBy"] is not None else "unmanagedGroupStorage"
                account_overview[index]["total"] += 1
                if blob_access_open or force_update:
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
            file_path = os.path.join(logging_path, "{}.json".format(subid))
            with open(file_path, "w") as output_stats:
                output_stats.writelines(json.dumps(account_overview, indent=4))
