import json
from .generic import GenericObjectJson


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
