import os
import json
import typing
import logging
from enum import Enum
from microsoft.submaintenance import AzIdentities

class UserAssignment:
    def __init__(self, az_identities:AzIdentities, name, assignments:list):
        self.__az_identities = az_identities
        self.__oid = None
        self.name = name
        self.type = None
        self.assignments = []

        if len(assignments) > 0:
            self.type = assignments[0]["principalType"]

            for assigment in assignments:
                self.assignments.append({
                    "role" : assigment["roleDefinitionName"],
                    "scope" : assigment["scopeType"]
                })
    
    def supports_role_definition(self, role_def:str, scopes: typing.List[str]) -> bool:
        support = [x for x in self.assignments if x["role"].lower() == role_def.lower()]
        if scopes and len(support):
            support = [x for x in support if x["scope"].lower() in scopes]
        return len(support) > 0

    def get_oid(self) -> str:
        if self.__oid is None and self.type == "User":
            ad_user = self.__az_identities.get_aad_user_info(self.name)
            if not ad_user:
                print("{} could not be located".format(self.name))
            else:
                self.__oid = ad_user.objectId

        return self.__oid
    
    def is_user(self):
        return self.type == "User"

    def get_sub_roles(self):
        return [x for x in self.assignments if x["scope"] == "Subscription"]

class GroupType(Enum):
    internal_group = 0
    external_group = 1

class Group:
    def __init__(self,az_identities:AzIdentities, settings:dict):
        self.az_identities = az_identities
        self.type: GroupType = None
        self.name: str = None
        self.members = []

        # Get settings from config
        for setting in settings:
            setattr(self, setting, settings[setting])

        # Determine an internal or external group
        if isinstance(self.type, int):
            self.type = GroupType(self.type)
        elif self.type in GroupType.internal_group.name:
            self.type = GroupType.internal_group
        else:
            self.type = GroupType.external_group

        # Load the acutal member OID's
        members = az_identities.get_group_members(self.name)
        for member in members:
            if member.objectId not in self.members:
                self.members.append(member.objectId)
        
            
    def __str__(self):
        members = ""
        for member in self.members:
            members += "\t\t{}\n".format(member)

        return """
    group_name : {}
    group_type : {}
    members: \n{}
        """.format(self.name, self.type.name, members)
    
class Role:
    def __init__(
            self, 
            az_identities:AzIdentities, 
            name:str, 
            filter:str,
            scopes: typing.List[str],  
            groups:typing.List[typing.Dict[str, object]]):
        self.az_identities = az_identities
        self.name = name
        self.scopes = [x.lower() for x in scopes]
        self.groups:typing.List[Group] = []
        self.external_filter = filter

        for group in groups:
            self.groups.append(Group(self.az_identities, group))

    def add_user_to_role_group(self, user: UserAssignment):

        if len(self.groups) == 0:
            error = "There are no groups for role {} to add user {} to.".format(
                self.name,
                user.name
            )
            logging.error(error)
            raise Exception(error)
        
        active_group = self.groups[0]
        if self.is_filtered() or True:
            if self.external_filter in user.name:
                active_group = [x for x in self.groups if x.type == GroupType.external_group][0]
            else: 
                active_group = [x for x in self.groups if x.type == GroupType.internal_group][0]

        user_oid = user.get_oid()
        if user_oid is None:
            error = "User is not supported, no OID - {}".format(user.name)
            logging.error(error)
            raise Exception(error)

        if user_oid not in active_group.members:
            logging.info("{} NEW: {} to {} ({})".format(
                    self.name,
                    user.name, 
                    active_group.name,
                    active_group.type.name)
                )
            self.az_identities.add_group_member(active_group.name, user_oid)
        else:
            logging.info("{} EXISTS: {} already exists in {} ({})".format(
                    self.name,
                    user.name, 
                    active_group.name,
                    active_group.type.name)
                )

    def is_filtered(self):
        filtered = False
        if len(self.groups) > 1:
            types = [x.type for x in self.groups]
            if GroupType.internal_group not in types or GroupType.external_group not in types:
                raise Exception("Multiple groups on role {} but missing a group type".format(self.name))
            filtered = True
        return filtered
    
    def __str__(self):
        groups = ""
        for group in self.groups:
            groups += str(group) + "\n"

        return """
role_name : {}
external_filter : {}
groups: {}
            """.format(self.name, self.external_filter, groups)
    
class GroupConfiguration:
    def __init__(self, az_identities:AzIdentities, config_file:str):
        self.az_identities = az_identities
        self.config_file = config_file
        self.subscription = None
        self.settings = {}
        self.roles: typing.List[Role] = []

        if not os.path.exists(self.config_file):
            raise Exception("Config file {} does not exist".format(self.config_file))
        
        configuration = None
        with open(self.config_file, "r") as c_file:
            configuration = "\n".join(c_file.readlines())
            configuration = json.loads(configuration)

        self.subscription = configuration["subscription"]
        self.settings = configuration["settings"]

        for role in configuration["groups"]:
            if configuration["groups"][role] is not None:
                self.roles.append(
                        Role(
                            az_identities,
                            role, 
                            self.settings["external_filter"],
                            configuration["groups"][role]["scopes"],
                            configuration["groups"][role]["groups"]
                            )
                        )

                # test
                self.roles[-1].is_filtered()

    