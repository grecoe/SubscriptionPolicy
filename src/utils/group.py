from .cmdline import CmdUtils

class AzResourceGroup:
    @staticmethod
    def get_groups(sub_id:str):
        return CmdUtils.get_command_output(
            [
                "az", 
                "group", 
                "list", 
                "--subscription", 
                sub_id
            ]
        )

    @staticmethod
    def delete_group(group_name:str, sub_id: str):
        print("Delete Resource Group: {} in {}".format(
            group_name,
            sub_id
        ))
        CmdUtils.get_command_output(
            [
                "az",
                "group",
                "delete",
                "--name",
                group_name,
                "--subscription",
                sub_id,
                "--no-wait",
                "--yes"       
            ]
        )
