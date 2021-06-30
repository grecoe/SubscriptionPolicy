import os
import typing
from .utils.csvloader import S360Reader
from .utils.roles import (
    AzRolesUtils,
    AzRole
)


class SubscriptionDetails:
    """Internal class used in identites to store out the information
    about role assignments on the subscription"""
    def __init__(self, id:str):
        self.id:str = id
        self.users:typing.List[AzRole] = []
        self.groups:typing.List[AzRole] = []
        self.sps:typing.List[AzRole] = []

class AzIdentities:
    """Class used to provide actual functionality to role assignments and 
    AAD principals."""
    ROLE_TYPE_SUBSCRIPTION = "Subscription"
    ROLE_TYPE_RESOURCE_GROUP = "ResourceGroup"
    ROLE_TYPE_GLOBAL = "Global"
    TYPE_SERVICE_PRINCIPAL = "ServicePrincipal"
    TYPE_GROUP = "Group"
    TYPE_USER = "User"

    def __init__(self):
        self.data:typing.Dict[str,SubscriptionDetails] = {}

    def get_users_sub_scope(self, sub_id: str) -> typing.List[AzRole]:
        """Get a list of users that have role assignments at the subscription
        scope.
        
        Params:
        sub_id : Subscritpion to get users at
        
        Returns:
        List of AzRole objects
        """
        self._load_sub_details(sub_id)

        return_users = []
        if sub_id in self.data:
            return_users.extend(
                [x for x in self.data[sub_id].users if x.scope_type == AzIdentities.ROLE_TYPE_SUBSCRIPTION]
            )
        
        return return_users

    def clear_invalid_principals(self, sub_id:str) -> int:
        """An invalid service principal cannot be found in AAD. Even user
        defined identities are found there. 
        
        Params:
        sub_id : Subscritpion to clear bad SP's from
        
        Returns:
        Number of removed roles
        """
        return_count = 0

        seen_list = {}
        sp_list = self._get_service_principals(sub_id)
        for sp_role in sp_list:
            print("Verifying ", sp_role.principalId)

            if sp_role.principalId not in seen_list: 
                seen_list[sp_role.principalId] = True # It's valid
            else:
                print("Duplicate SP check skipped")
                if seen_list[sp_role.principalId] == False:
                    return_count += 1
                    sp_role.delete()
                continue
            
            # Try and get it, None means it's not there
            actual_sp = AzRolesUtils.get_aad_sp_info(sp_role.principalId)
            if actual_sp is None:
                print("Principal not found in AAD....")
                return_count += 1
                seen_list[sp_role.principalId] = False
                sp_role.delete()

        return  return_count

    def get_role_summary(self, sub_id:str) -> typing.Dict[str,typing.Dict[str,str]]:
        """Gets the full summary of assignments for the sub 
        
        Params:
        sub_id : Subscritpion to clear bad SP's from
        
        Returns:
        Serializable dict to dump out
        """
        return_collection = {}
        self._load_sub_details(sub_id)
        if sub_id in self.data:
            sub_details = self.data[sub_id]
            scans = [sub_details.users, sub_details.groups, sub_details.sps]

            for scan in scans:
                for role in scan:
                    identity_name = role.principalName if role.principalName else role.principalId

                    if identity_name not in return_collection:
                        return_collection[identity_name] = []
                    
                    return_collection[identity_name].append(
                        {
                            "principalType" : role.principalType,
                            "roleDefinitionName" : role.roleDefinitionName,
                            "id" : role.id
                        }
                    )

        return return_collection

    def clear_s360_principals(self, s360_csv:str) -> typing.Dict[str, int]:
        """Periodically you will need to clear out unused service principals as
        identified by s360. You use that tool and export the results for overprivileged
        service principals. Pass that file which will contain principal ID's and 
        the sub it's affecting
        
        Parameters:
        s360_csv : Full path to the exported s360 overprivileged service principals.

        Returns:
        Dict -> key=sub, value=count of assignments removed
        """
        if not os.path.exists(s360_csv):
            raise Exception("S360 output is invalid")
        
        return_collection = {}
        """S360 fields of interest
        subscription - sub ID
        principalId - entity id
        roleScope - Scope to ensure we have the right one.
        """
        s360Entities = S360Reader.read_file(s360_csv)
        return_collection["S360Entries"] = len(s360Entities)
        return_collection["ActiveRolesRemoved"] = 0

        for entity in s360Entities:
            if not entity.subscription:
                print("Missing subscription")
                continue
            
            self._load_sub_details(entity.subscription)
            if entity.subscription in self.data:
                sub_data = self.data[entity.subscription]

                # Scan service principals (not users or groups)
                found_principals = [x for x in sub_data.sps if x.principalId == entity.principalId]
                found_scopes = [x for x in found_principals if x.scope == entity.roleScope]

                if entity.subscription not in return_collection:
                    return_collection[entity.subscription] = 0
                
                return_collection[entity.subscription] += len(found_scopes)
                for azrole in found_scopes:
                    return_collection["ActiveRolesRemoved"] += 1
                    azrole.delete()

        return return_collection


    # Private Methods Below
    def _get_service_principals(self, sub_id: str) -> typing.List[AzRole]:
        """Get a list of service principals that have role assignments within
        a specified subscription.
        
        Params:
        sub_id : Subscritpion to get users at
        
        Returns:
        List of AzRole objects
        """
        self._load_sub_details(sub_id)

        return_principals = []
        if sub_id in self.data:
            return_principals = self.data[sub_id].sps

        return return_principals

    def _load_sub_details(self, sub_id: str) -> None:
        """Check to see if the subscription information has been loaded.
        If not load it.
        
        Params:
        sub_id : Subscritpion to verify
        
        Returns:
        None
        """
        if sub_id not in self.data:
            print("Loading subscription assignments for ", sub_id)

            sub_roles = AzRolesUtils.get_all_roles(sub_id, False)
            if isinstance(sub_roles, list):
            
                sub_details = SubscriptionDetails(sub_id)
                for role in sub_roles:
                    if sub_id not in role.scope:
                        continue
                    
                    role.scope_type = AzIdentities._get_role_type(role.scope)

                    if role.principalType == AzIdentities.TYPE_SERVICE_PRINCIPAL:
                        sub_details.sps.append(role)
                    if role.principalType == AzIdentities.TYPE_GROUP:
                        sub_details.groups.append(role)
                    if role.principalType == AzIdentities.TYPE_USER:
                        sub_details.users.append(role)

                self.data[sub_id] = sub_details

    @staticmethod
    def _get_role_type(scope:str) -> str:
        # /subscriptions/1b365fe2-5882-4935-bd81-8027e0816b45/resourceGroups/daden1/providers/Microsoft.Storage/storageAccounts/daden1exp2ws2677378701
        parts = scope.split('/')
        if len(parts) == 3:
            return AzIdentities.ROLE_TYPE_SUBSCRIPTION
        if len(parts) == 5:
            return AzIdentities.ROLE_TYPE_RESOURCE_GROUP
    
        if len(parts) >= 7:
            return parts[6].lower()
        else:
            return AzIdentities.ROLE_TYPE_GLOBAL                    

