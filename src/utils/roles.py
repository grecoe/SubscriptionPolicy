from .cmdline import CmdUtils


class AzRole:
    def __init__(self):
        self.subscription = None
        self.id = None
        self.name = None
        self.principalId = None
        self.principalName = None
        self.principalType = None
        self.roleDefinitionName = None
        self.roleDefinitionId = None
        self.scope = None

    def get_delete_command(self):
        command = "az role assignment delete --assignee {} --role {} --scope {} --subscription {}".format(
            self.principalId,
            self.roleDefinitionId,
            self.scope, 
            self.subscription
        )
        return command

    def delete(self):
        command = self.get_delete_command()
        command = command.split(' ')
        print("Deleting {} role for {}\n\t{}".format(
            self.principalType,
            self.principalName
        ))
        CmdUtils.get_command_output(command,False)

    def _load_raw(self, az_role_json:dict):
        for key in az_role_json:
            setattr(self, key, az_role_json[key])

class AzRolesUtils:
    @staticmethod
    def get_sub_roles(sub_id, raw:bool = True):
        output = CmdUtils.get_command_output(
            [
                "az", 
                "role", 
                "assignment", 
                "list", 
                "--include-classic-administrators",
                "false",
                "--subscription", 
                sub_id
            ]
        )

        if raw is True:
            return output

        return AzRolesUtils._convert_raw_roles(output, sub_id)

    @staticmethod
    def get_all_roles(sub_id : str, raw:bool = True):
        output = CmdUtils.get_command_output(
            [
                "az", 
                "role", 
                "assignment", 
                "list", 
                "--all",
                "--include-classic-administrators",
                "false",
                "--subscription", 
                sub_id
            ]
        )

        if raw is True:
            return output

        return AzRolesUtils._convert_raw_roles(output, sub_id)

    @staticmethod
    def _convert_raw_roles(raw_roles, sub_id):
        return_list = []
        for r in raw_roles:
            cur_role = AzRole()
            cur_role._load_raw(r)
            cur_role.subscription = sub_id
            return_list.append(cur_role)
        return return_list

