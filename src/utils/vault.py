from .cmdline import CmdUtils


class AzKeyVaultUtils:
    @staticmethod
    def list_vaults(sub_id : str):
        command = "az keyvault list --subscription {}".format(
            sub_id
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
