import typing
from .utils.group import AzResourceGroupUtils
from .utils.locks import AzLockUtils
from .utils.generic import GenericObjectJson

class FilteredResults:
    def __init__(self):
        self.totalGroups = 0
        self.managedGroups = 0
        self.ignoredGroups = 0
        self.untaggedGroups = 0
        self.untagged = []

class SubscripitionGroups:
    def __init__(self, sub_id:str):
        self.sub_id:str = sub_id
        self.groups:typing.List[GenericObjectJson] = []

class AzGroupCompliance:
    def __init__(self):
        self.data:typing.Dict[str, SubscripitionGroups] = {}

    def get_group_count(self, sub_id:str) -> int:
        """Gets the total number of resource groups in a sub"""
        return_val = 0
        self._load_sub_details(sub_id)
        if sub_id in self.data:
            return_val = len(self.data[sub_id].groups)
        return return_val


    def get_filtered_groups(self, sub_id:str, ignored:typing.List[str], required_tags:typing.List[str]) -> FilteredResults:
        """Get a list of GenericObjectJson objects in which the group 
        
            1. Does not have a name starting with something from ignored
            2. Does not have the required tag
        """
        return_results = FilteredResults()

        self._load_sub_details(sub_id)

        if sub_id in self.data:
            group_data = self.data[sub_id]
            
            return_results.totalGroups = len(group_data.groups)

            for group in group_data.groups:
                if hasattr(group, "managedBy"):
                    if group.managedBy:
                        return_results.managedGroups += 1
                        continue

                if ignored:
                    continue_on_ignore = False
                    for ignore in ignored:
                        if group.name.lower().startswith(ignore.lower()):
                            return_results.ignoredGroups += 1
                            continue_on_ignore = True
                            break
                    if continue_on_ignore:
                        continue
                
                flag_untagged = False
                if group.tags is None:
                    flag_untagged = True
                elif required_tags:
                    requirements = [x.lower() for x in required_tags]
                    present_tags = [x.lower() for x in list(group.tags.keys())]

                    for required in requirements:
                        if required not in present_tags:
                            flag_untagged = True
                            break

                if flag_untagged:
                    return_results.untaggedGroups += 1
                    return_results.untagged.append(group.name)

        return return_results

    def _load_sub_details(self, sub_id: str) -> None:
        """Check to see if the subscription information has been loaded.
        If not load it.
        
        Params:
        sub_id : Subscritpion to verify
        
        Returns:
        None
        """
        if sub_id not in self.data:
            print("Loading resource groups for for ", sub_id)
            loaded_groups = AzResourceGroupUtils.get_groups(sub_id)

            new_group = SubscripitionGroups(sub_id)
            for group in loaded_groups:
                new_group.groups.append(GenericObjectJson(group))

            self.data[sub_id] = new_group
