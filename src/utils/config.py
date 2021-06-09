import os
import json

class Configuration:
    def __init__(self, config_path: str):
        if not os.path.exists(config_path):
            raise Exception("Config file not found: ", config_path)

        config = None
        with open(config_path, "r") as input:
            config = input.readlines()
            config = "\n".join(config)
            config = json.loads(config)
        
        if config:
            for key in config:
                setattr(self, key, config[key])