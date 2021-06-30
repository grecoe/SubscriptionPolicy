import json
import subprocess

class CmdUtils:

    @staticmethod
    def get_command_output(command_list, as_json=True):
        result = subprocess.run(command_list, stdout=subprocess.PIPE, shell=True)

        try:
            result = result.stdout.decode("utf-8")
        except UnicodeDecodeError as err:
            print("Unicode error, try again")
            print("Command was: ", " ".join(command_list))
            try:
                result = result.stdout.decode("utf-16")
            except Exception as ex:
                print("Re-attempt failed with ", str(ex))
                result = None

        if as_json and result is not None and len(result):
            return json.loads(result)

        return result