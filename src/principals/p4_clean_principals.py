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
    "e39abb98-13a0-4f2e-967f-053e18fcdd38",
    "ef29b8e7-4aff-4d93-a9b0-f822a793a57a",
    "3bbe5ff2-813e-45be-880b-399b558f203a",
    "d6933676-4254-40b5-9d28-45bbcdd7ffcb",
    "0f543635-c462-4f7c-95fd-3f9b216d8638",
    "020b5e91-519e-4483-b0c9-97e752701699",
    "fe749a2b-9270-4da7-b31f-326c7e1b9284",
    "24b62a90-940f-42aa-a073-9f5e17902079",
    "78b7f169-5f40-426a-b514-130bb3ed7093",
    "e128e5c5-c386-4728-9bd5-8fd5db5c7701",
    "4d82bb1b-927d-404f-b60e-ae816392455f",
    "b3508050-9019-4dca-bcd4-816ae45c0746",
    "50cb16e8-6201-47e4-bfec-28e5c9f9f0b2",
    "ec4155eb-7a28-4bc7-a966-82da39fa4eab",
    "b26a3d39-0437-49b8-b4e1-66397ef465aa",
    "d3e84ea7-8cc9-407b-874b-54bdca08401c",
    "1ee375fd-d8b7-4235-92d9-de5df0acc15c",
    "cb9c825c-dd9e-4c51-b1f9-792814d534e8",
    "e5548bcb-c5bd-43f9-83a3-38f6ea25590e",
    "4e154e9e-4877-49b9-a8f4-ab67ceec6357",
    "1bad9681-9d6c-457e-8954-85fa5eddeddd",
    "27c47c7c-0bac-4180-94a1-51b317cd05c8",
    "9a2fe3ee-7e09-413e-a7bd-85fca4266d9c",
    "7cb18187-89ff-4073-994c-aac089b70d61",
    "e4facbfd-72cd-4417-a255-0d94b7ae9cf1",
    "d30e4c9f-6498-44b0-89dd-669a112f3a37",
    "f4a14939-f58b-4d2b-9448-9ca9dba737f3",
    "d60f55f9-4cb3-4c7d-84ee-b7fc27af47b9",
    "92016eaa-3e44-48b9-8e90-29d45f70b2b5",
    "b994c5d1-605a-461e-b560-871c49518b25",
    "5ad7113a-e4eb-410d-87e6-ea4a3df24765",
    "9a1ac5e6-b0e3-44bd-a149-f37ffd888d09",
    "782593f6-3a7b-400e-ba25-7c653522f774",
    "5baca217-1c22-488c-b3df-be5323fbc540",
    "cbeadd27-217d-4278-97bb-be726f693ad1",
    "457a2fe0-c57c-41f5-a337-8fc59621a2bd",
    "d1c2ebbb-ec7a-48db-bf32-03837265d1b1",
    "cb1b35d8-f9a4-45b1-8bc8-4d5bd4263171",
    "a57c8373-77dc-4cdb-ab36-ef37a879e912",
    "e85bfa0a-c028-45ef-8240-943f927dc39c",
    "b2cab137-eb79-4184-aaa3-fc1567b79e20"
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
