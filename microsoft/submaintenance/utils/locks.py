from .cmdline import CmdUtils

class AzLock:
    def __init__(self, subscription, lock_data):
        self.id = None
        self.level = None
        self.name = None,
        self.resourceGroup = None,
        self.subscription = subscription

        for key in lock_data:
            setattr(self, key, lock_data[key])

    def delete(self):
        AzLockUtils.delete_lock(self.id, self.subscription)

class AzLockUtils:
    @staticmethod
    def get_group_locks(rg_name:str, sub_id:str):
        return_locks = []
        locks = CmdUtils.get_command_output(
            [
                "az",
                "lock",
                "list",
                "--resource-group",
                rg_name,
                "--subscription",
                sub_id
            ]
        )

        if locks and len(locks):
            for lock in locks:
                return_locks.append(
                    AzLock(sub_id, lock)
                )

        return return_locks


    @staticmethod 
    def delete_lock(id:str,sub_id:str):
        print("Delete management lock:\n\t{}".format(id))
        return CmdUtils.get_command_output(
                [
                    "az",
                    "lock",
                    "delete",
                    "--ids",
                    id, 
                    "--subscription",
                    sub_id
                ]
            )

