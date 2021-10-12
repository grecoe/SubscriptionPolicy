from .cmdline import CmdUtils

class AzResourceGroupUtils:

    @staticmethod
    def get_group(sub_id: str, group_name: str):
        return CmdUtils.get_command_output(
            [
                "az", 
                "group", 
                "show",
                "--name",
                group_name, 
                "--subscription", 
                sub_id
            ]
        )

    @staticmethod
    def get_group_locks(sub_id: str, group_name: str) -> list:
        """
        {
            "id": "/subscriptions/b0844137-4c2f-4091-b7f1-bc64c8b60e9c/resourceGroups/testgp/providers/Microsoft.Authorization/locks/test",
            "level": "ReadOnly",
            "name": "test",
            "notes": "some note",
            "owners": null,
            "resourceGroup": "testgp",
            "type": "Microsoft.Authorization/locks"
        }
        """
        return CmdUtils.get_command_output(
            [
                "az", 
                "group", 
                "lock",
                "list",
                "--resource-group",
                group_name, 
                "--subscription", 
                sub_id
            ]
        )

    @staticmethod
    def delete_group_lock(lock_name:str, sub_id: str, group_name: str) -> list:
        return CmdUtils.get_command_output(
            [
                "az", 
                "group", 
                "lock",
                "delete",
                "--name",
                lock_name,
                "--resource-group",
                group_name, 
                "--subscription", 
                sub_id
            ]
        )

    @staticmethod
    def update_group_tags(sub_id: str, group_name: str, set_command:str):
        return CmdUtils.get_command_output(
            [
                "az", 
                "group", 
                "update",
                "--resource-group",
                group_name, 
                "--set",
                set_command,
                "--subscription", 
                sub_id
            ]
        )

    @staticmethod
    def get_tag_content(group:dict, tag:str) -> str:
        return_value = None
        if "tags" in group and group["tags"]:
            if tag in group["tags"]:
                return_value = group["tags"][tag]
        return return_value

    @staticmethod
    def group_exists(sub_id: str, group_name: str):
        return CmdUtils.get_command_output(
            [
                "az", 
                "group", 
                "exists",
                "--name",
                group_name, 
                "--subscription", 
                sub_id
            ]
        )

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

        # Get locks and delete if any
        lock_list = AzResourceGroupUtils.get_group_locks(sub_id, group_name)
        if len(lock_list):
            for lock in lock_list:
                print("Deleting group lock -", lock["name"])
                AzResourceGroupUtils.delete_group_lock(lock["name"],sub_id, group_name)

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
