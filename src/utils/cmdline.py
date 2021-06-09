import json
import subprocess


class CmdUtils:

    @staticmethod
    def get_command_output(command_list, as_json=True):
        result = subprocess.run(command_list, stdout=subprocess.PIPE, shell=True)
        result = result.stdout.decode("utf-8")

        if as_json and result and len(result):
            return json.loads(result)

        return result