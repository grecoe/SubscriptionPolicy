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
"43bf2882-086c-4b4b-91fa-37a19a0ab137",
    "7a9beb15-80d7-4369-b2cc-cc95818958ec",
    "a7588308-b951-44e8-a8d3-f70a9861db69",
    "bdac4055-9240-43dd-acdb-6ab372480c0e",
    "765df3af-5ece-44db-84cb-2b6c54396032",
    "682f110a-f2f1-4c19-90f7-ad61b7f4d409",
    "cdae5f9e-437b-4360-b562-5b1c389b44d7",
    "02400500-e727-484a-820e-110871f61f39",
    "b42170cd-d3f9-41ba-8393-d93ef0869328",
    "0bb40ab3-925b-4d2c-9d5f-75ed1429d09f",
    "1edc35aa-59ea-47f1-b4a4-3b064da4434e",
    "0195188a-2e0e-4ab2-a3db-199fa30a73c0",
    "dc3d7d49-ff97-4306-83ed-86f01fd0060b",
    "b9dd930b-72bf-4678-babe-a1155e13a34d",
    "e630b2d2-62d5-46d6-9176-018a7d3a9649",
    "a0310088-50d6-4e51-8dce-a4996c03c1bd",
    "36c235e5-8e07-470e-8d43-207b826190b5",
    "93cadefa-77ba-4406-97f4-ca3532e0e51a",
    "de93cb9d-0f62-4bc3-8830-3fe877f85a31",
    "bd632a7c-7c52-41f1-8fc6-d5f3e07cc5bb",
    "05e320af-6b76-4a13-8284-e102222f04fa",
    "12169187-fa9f-4c82-a374-7f80bd4f4633",
    "804adf50-a5a2-4054-88e1-ae9461bcf645",
    "0026a227-eae6-4720-91c9-f0a443f2aab5",
    "5e472e15-3dc2-4095-8bb8-702f308b923e",
    "2182d92d-07b3-4b0a-8776-3d0973d5b4b7",
    "748aeade-018f-4fe9-baeb-bdfb921c308a",
    "c98b6e57-070e-4836-9250-adaaf13392ca",
    "967fe313-e4b3-41db-b090-88b396a000bb",
    "33fc06ec-61b1-450d-94f0-353824389ca2",
    "d60f55f9-4cb3-4c7d-84ee-b7fc27af47b9",
    "9c1f9133-d7eb-4dad-9aed-dc7b0df2d4ef",
    "1d98b877-b599-4656-a392-9aeee61caa6f",
    "87b999de-ab75-4d17-8838-af1bceb153f5",
    "7b14d4ee-dc03-4db9-a48a-252e6c0c0d17",
    "e2221837-b5de-4ff5-9f31-50cc97448cbf",
    "a84b5e99-f81b-4ec2-aa2d-00c565d90efd",
    "92016eaa-3e44-48b9-8e90-29d45f70b2b5",
    "b994c5d1-605a-461e-b560-871c49518b25",
    "01979862-438e-43b6-bebe-82fab581df29",
    "c307744f-9c28-4243-ab09-991dbcc4ee08",
    "33fc06ec-61b1-450d-94f0-353824389ca2",
    "0d302973-73ae-4634-b6b8-f6f711544ed8",
    "98ceb1f5-fc12-48cc-b528-26569c858c64",
    "23c4680b-27cd-408c-8332-79267aff5f3b",
    "33fc06ec-61b1-450d-94f0-353824389ca2"
]

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
