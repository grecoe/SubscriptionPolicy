import json

class GenericObjectJson:
    def __init__(self, props):

        for prop in props:
            setattr(self, prop, props[prop])


class JsonFileUtil:
    @staticmethod
    def read_file_as_json(file_name):
        data = None
        with open(file_name, "r") as input:
            data = input.readlines()
            data = "\n".join(data)
            data = json.loads(data)
        return data


    @staticmethod
    def read_file_as_generic_objects(file_name):
        return_value = None
        try:
            return_value= JsonFileUtil._read_file_as_generic_objects(file_name, "utf16")
        except UnicodeError as uex:
            return_value = JsonFileUtil._read_file_as_generic_objects(file_name, "utf8")
        return return_value

    @staticmethod
    def _read_file_as_generic_objects(file_name: str, encoding: str):
        generic_object_return = {}

        with open(file_name,encoding=encoding) as assigned_roles_file:
            roles = assigned_roles_file.readlines()
            roles = "\n".join(roles)
            roles = json.loads(roles)

            count = 0
            for role in roles:
                count += 1
                jgen = GenericObjectJson(role)
                """
                Getting duplicates in particular where the same principal ID
                has been assigned multiple roles like Contrib and Owner on the
                same sub. See bottom of file for example
                if jgen.principalId in generic_object_return:
                    print("Original\n{}".format(json.dumps(generic_object_return[jgen.principalId], indent=4)))
                    print("New\n{}".format(json.dumps(role, indent=4)))
                    quit()
                """
                generic_object_return[jgen.principalId] = jgen

        return generic_object_return
"""
Duplication issues:

{
    "canDelegate": null,
    "condition": null,
    "conditionVersion": null,
    "description": null,
    "id": "/subscriptions/1b365fe2-5882-4935-bd81-8027e0816b45/providers/Microsoft.Authorization/roleAssignments/a2a9351e-3df3-4e7c-ae97-17f4fb755363",
    "name": "a2a9351e-3df3-4e7c-ae97-17f4fb755363",
    "principalId": "019d485c-1675-4ea4-b8a1-a6792b586227",
    "principalName": "prsol@microsoft.com",
    "principalType": "User",
    "roleDefinitionId": "/subscriptions/1b365fe2-5882-4935-bd81-8027e0816b45/providers/Microsoft.Authorization/roleDefinitions/b24988ac-6180-42a0-ab88-20f7382dd24c",
    "roleDefinitionName": "Contributor",
    "scope": "/subscriptions/1b365fe2-5882-4935-bd81-8027e0816b45",
    "type": "Microsoft.Authorization/roleAssignments"
}

{
    "canDelegate": null,
    "condition": null,
    "conditionVersion": null,
    "description": null,
    "id": "/subscriptions/1b365fe2-5882-4935-bd81-8027e0816b45/providers/Microsoft.Authorization/roleAssignments/364a9e67-ba61-4ed3-8b48-4a8f35d83aca",
    "name": "364a9e67-ba61-4ed3-8b48-4a8f35d83aca",
    "principalId": "019d485c-1675-4ea4-b8a1-a6792b586227",
    "principalName": "prsol@microsoft.com",
    "principalType": "User",
    "roleDefinitionId": "/subscriptions/1b365fe2-5882-4935-bd81-8027e0816b45/providers/Microsoft.Authorization/roleDefinitions/8e3af657-a8ff-443c-a75c-2fe8c4bcb635",
    "roleDefinitionName": "Owner",
    "scope": "/subscriptions/1b365fe2-5882-4935-bd81-8027e0816b45",
    "type": "Microsoft.Authorization/roleAssignments"
}
"""