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
