"""
This file assumes you have created all the mapping files you need
to map service princpals to.

You need to provide the output directory of the match_s360_to_subs.py
which if unchanged is raw_matched.
"""
import os
import sys
sys.path.insert(0, "..")
from utils.jsonloader import JsonFileUtil
from utils.cmdline import CmdUtils
from utils.pathutils import PathUtils
from utils.config import Configuration

# Load configuration
cfg = Configuration("../../configuration.json")

# This setting must be there AND we must be able to load them
if "mapDirectory" not in cfg.principals:
    raise Exception("Missing mapDirectory from principals")

# Load up all the map files
map_path = "./" + cfg.principals["mapDirectory"]
map_files = PathUtils.load_json_files(map_path)

if not len(map_files):
    raise Exception("Ensure you have run match_s360_to_subs.py")


# Principals to clear out
principals_to_clean = [
       "ec88edd0-abc0-417d-b35a-57ff7f423878",
    "987be0f3-3b7f-49e7-afec-d1c895acad7a",
    "3a9d94d4-9807-4a81-92c5-74cc3d33b1b9",
    "2b9b8179-2dff-404b-9f9a-2949c4ec1087",
    "2af39c0d-ff15-48f3-9b99-b4f32e54c5b7",
    "e5df45b9-54eb-4212-ad93-4e02de3bb3d2",
    "cc9d811a-794e-4df7-8265-6995a6fc8d17",
    "0f58065a-f816-47af-81c7-f48f25123ea1",
    "bbecbd18-e56b-46f1-a6f0-c5d45b60f2b8",
    "3564eca9-0373-45af-9467-9d5d53ac37fb",
    "b2cc4a70-bd53-4c6e-a031-616f390ed418",
    "51d06f19-d37c-4e77-8b23-f7622d2b84bd",
    "aab29d54-445c-4d31-8ee5-1a043a55cf3b",
    "eefddcd9-97ba-48f8-9ea4-cc55b00f4191",
    "023bf6bf-ca34-418a-9056-dbbe2a6bca33",
    "0df3b89a-7abd-46d4-87b8-def06a442e81",
    "bdbe32a6-34a0-4897-acee-af8745614567",
    "7995e2c5-0923-407e-8ca5-262488c1f6b9",
    "0e8a9cb4-35d0-44f0-9a88-d5da892923ad",
    "8f7923c0-90d2-4047-bffd-56e8c9b525e8",
    "d42116e5-8331-4b3e-8a3c-229b06a3c0f5",
    "2d1fd971-8ce9-42f1-8635-2df490d73a5b",
    "2da9569b-52b4-4eac-a30f-07af1a4deff0",
    "48b457ff-acb1-4944-ae77-68fb33ce4dcc",
    "f6119aea-1ad3-4bcb-823d-75d4f4be5017",
    "a88ead9e-54ab-409a-b34d-e0dbe82c696b",
    "c4b32f7c-af14-4826-9e5a-2b31954a30d0",
    "20e65fd1-9f2f-4130-8399-f68cdf851664",
    "d9baa00c-05db-4fd3-a7c2-997119e48adc",
    "2cba456f-c1e8-4203-84b3-4b023e6c3b8a",
    "41fc24ba-4468-4ea0-8242-741ef880865a",
    "7f650a94-8e49-41fd-b2fc-8085ee1ee702",
    "6d54dd4a-de24-403a-9352-fe5656713aea",
    "15705409-2b6b-42e5-a9a3-01d9384c8860",
    "122eeaf4-eacc-46ba-a149-1f4b89c45cd5",
    "1de674e0-7338-45f8-ac31-a97ff6727ecc",
    "082f2c9f-32d6-46a1-9db5-2be22fe324ad",
    "a7e02ab6-a50a-43a2-b176-4f629c156936",
    "e2cad943-4ea4-4be7-b9af-21bef5f62d84",
    "fbb47968-4f24-4750-bfee-73e3fbf3c27c",
    "32d35cbf-641f-4358-b8e7-aa07199c29fa",
    "78aa3340-155b-4cb6-a15f-4a6c71111c6a",
    "b1fd574b-6363-4e31-96f7-5ef5cd0ab7ac"]

if not len(principals_to_clean):
    raise Exception("Provide some SP ID's to clear out")

# Walk all the files and for the principals to clean we build
# up a collection in the form
# {
# 	principalId : {
# 		subId :[list of cleanup calls]
# 	}
# }
cleanup_map = {}
cleans = 0
for match in map_files:
    for id_to_clean in principals_to_clean:
        for sp in match:
            if sp["principalId"] == id_to_clean:
                if sp["principalId"] not in cleanup_map:
                    cleanup_map[sp["principalId"]] = {}

                if sp["subscription"] not in cleanup_map[sp["principalId"]]:
                    cleanup_map[sp["principalId"]][sp["subscription"]] = []

                if sp["cleanup"] not in cleanup_map[sp["principalId"]][sp["subscription"]]:
                    cleans += 1
                    cleanup_map[sp["principalId"]][sp["subscription"]].append(sp["cleanup"])

# Now with the map we can start issuing deletion of the assignemnts
for principal in cleanup_map:
    for sub in cleanup_map[principal]:
        for cleanup in cleanup_map[principal][sub]:
            cleanup = cleanup.replace("'", "")
            cleanup = cleanup.replace('"', "")

            deletion_command = "{} --subscription {}".format(
                cleanup,
                sub
            )

            print("Removing principal {} from {}".format(
                principal,
                sub
            ))
            print("\t{}".format(deletion_command))

            commands = deletion_command.split(' ')
            CmdUtils.get_command_output(commands, False)
