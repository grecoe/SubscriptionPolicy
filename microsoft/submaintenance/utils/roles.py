from .cmdline import CmdUtils

class AzAdLoader:
    @staticmethod
    def load_props(obj, props):
        for key in obj.__dict__:
            if key in props:
                setattr(obj, key, props[key])

class AzAdSp:
    def __init__(self, props):
        # Display name, appId, servicePrincipalType
        self.displayName = None
        self.appId = None
        self.servicePrincipalType = None
        self.owners = []
        AzAdLoader.load_props(self,props)

class AzAdUser:
    def __init__(self, props):
        # objectId, mail, department
        self.objectId = None
        self.mail = None
        self.department = None
        AzAdLoader.load_props(self,props)

class AzAdGroupMember:
    def __init__(self, props):
        # objectId, mail, department
        self.objectId = None
        self.objectType = None
        self.userType = None
        AzAdLoader.load_props(self,props)

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

    def delete(self):
        command = AzRole.get_delete_command(self.id)
        command = command.split(' ')

        name = self.principalName if self.principalName else self.principalId 
        print("Deleting {} role for {}".format(
            self.principalType,
            name
        ))
        CmdUtils.get_command_output(command,False)

    @staticmethod
    def get_delete_command(assignment_id:str) -> str:
        """Command to delete an assignment based on id (most effective)
        Parameters
        assignment_id : Azure Identifier for the role assignment

        Returns:
        String for the command to execute
        """
        command = "az role assignment delete --ids {}".format(
            assignment_id
        )
        return command

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

    @staticmethod
    def get_aad_sp_info(principal_id:str):
        command = "az ad sp show --id {}".format(principal_id)
        raw =  CmdUtils.get_command_output(command.split(' '))
        if raw:
            sp_obj = AzAdSp(raw)
            owners = AzRolesUtils._get_aad_sp_owners(principal_id)
            if owners and len(owners):
                for owner in owners:
                    sp_obj.owners.append(AzAdUser(owner))
            return sp_obj

        return None

    @staticmethod
    def get_aad_user_info(principal_id:str):
        command = "az ad user show --id {}".format(principal_id)
        raw =  CmdUtils.get_command_output(command.split(' '))
        if raw:
            return AzAdUser(raw)
        return None

    @staticmethod
    def _get_aad_sp_owners(principal_id: str):
        command = "az ad sp owner list --id {}".format(principal_id)
        return CmdUtils.get_command_output(command.split(' '))

    @staticmethod
    def get_aad_group_members(group : str):
        command = "az ad group member list --group {}".format(group)
        print("CALLLING", command)
        return CmdUtils.get_command_output(command.split(' '))

    @staticmethod
    def add_group_member(group: str, object_id: str):
        command = "az ad group member add --group {} --member-id {}".format(
                group,
                object_id
        )
        return CmdUtils.get_command_output(command.split(' '))

    @staticmethod
    def is_user_group_member(group: str, object_id: str):
        command = "az ad group member check --group {} --member-id {}".format(
                group,
                object_id
        )
        return CmdUtils.get_command_output(command.split(' '))
