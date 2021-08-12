from .cmdline import CmdUtils


class AzKeyVaultUtils:
    @staticmethod
    def list_vaults(sub_id : str):
        command = "az keyvault list --subscription {}".format(
            sub_id
        )

        return CmdUtils.get_command_output(command.split(' '))

    @staticmethod
    def list_deleted_vaults(sub_id : str):
        command = "az keyvault list-deleted --subscription {}".format(
            sub_id
        )

        return CmdUtils.get_command_output(command.split(' '))

    @staticmethod
    def purge_deleted_vault(sub_id: str, vault_name:str):
        command = "az keyvault purge --subscription {} --name {} --no-wait".format(
            sub_id,
            vault_name
        )

        return CmdUtils.get_command_output(command.split(' '))

    @staticmethod
    def get_vault(vault: str, sub_id: str):
        command = "az keyvault show --name {} --subscription {}".format(
            vault,
            sub_id
        )


        return CmdUtils.get_command_output(command.split(' '))

    @staticmethod
    def enable_softdelete(vault: str, sub_id: str):
        command = "az keyvault update --name {} --enable-soft-delete true --subscription {}".format(
            vault,
            sub_id
        )

        return CmdUtils.get_command_output(command.split(' '))

    @staticmethod
    def check_soft_delete_status(subscriptions: list):
        statistics = {
            "total" : 0,
            "unlocked" : []
        }

        for subid in subscriptions:
            print("Validating vaults in : {}".format(subid))
            
            vaults = AzKeyVaultUtils.list_vaults(subid)

            if vaults and len(vaults):
                statistics["total"] += len(vaults)
                for vault in vaults:
                    props = AzKeyVaultUtils.get_vault(vault["name"], subid)
                    sd_enabled = props["properties"]["enableSoftDelete"]
                    print(vault["name"], "->", sd_enabled)
                    if not sd_enabled:
                        statistics["unlocked"].append(vault["name"])                
                        AzKeyVaultUtils.enable_softdelete(vault["name"], subid)
        
        return statistics