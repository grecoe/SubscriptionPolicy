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
    "17a5d300-d2bd-499e-a745-2283e3db9997",
    "1239c657-5bb2-49cd-98d6-6df54bfa88b9",
    "02183bb5-7745-44a2-8c75-359e661cd724",
    "e371bb38-c770-4a68-b15a-8ecd62cabac7",
    "5a46043e-47eb-44d3-a298-69bdc4549c24",
    "1cb82105-bf09-40c9-98d0-b1ba03683f11",
    "8db43ed6-7a2d-46c2-a114-11810c8b65fb",
    "65225074-f84f-4457-86e7-27bcbf85b3ca",
    "e87df9eb-eda0-4458-8c2c-3807cb3c7689",
    "283206e9-2bbf-4635-9c4a-c867a60d7b9f",
    "48e88887-e45c-4ffd-b77c-c6a4aa124acc",
    "f018e32a-65e1-4870-8ee0-beca51bfe0cf",
    "f800ed5a-5a1e-44fe-8e86-bcbb0aac117e",
    "485ee57f-89b1-42a6-b70d-1413380728d2",
    "acb68a86-e9d1-4030-b110-90a77b444685",
    "bb9f67e8-453d-4987-9bbb-0b2d048cdf1d",
    "d76bb707-faf3-43c3-9896-5c0eb86b702d",
    "854d5e65-1be7-4334-a2b1-a1f99237984f",
    "846f0984-b68b-4ff2-b7e4-c94eda17df1b",
    "44031add-4f21-4883-a341-d789d0c9750f",
    "9c145771-b91a-455b-be28-f0dad5029478",
    "d4198501-8ea1-4cd2-ab90-a5b490439f4a",
    "2872ffb5-1f25-480b-9242-107828ab8624",
    "25109ba8-3d42-4ce0-bbfe-89aa3ce32063",
    "a8a5360d-e7f9-455f-b336-a5ec88001b00",
    "a634d3c8-6ddf-4ca1-8f80-e43e73be2353",
    "ce52452e-dc7f-4930-90c7-a0f9de35c000",
    "28c6158e-d416-48cc-b313-a3a88421d80a",
    "0b188d7f-a3f3-4d98-8669-6a784add7011",
    "8d40c2f0-e176-40ee-bf12-8b57662f4543",
    "a39d0155-3784-4d1a-8ab9-4f62e19a776e",
    "e8288ec4-ae84-48ff-920d-68b0786b4fcf",
    "a87eabb4-25f4-46bd-8b15-771b45e599c1",
    "d175aa45-40c0-4e0b-a790-ab933735ef46",
    "36ed9f62-ad1b-451e-9d8e-4dcde8fae758",
    "c0c84496-8a9b-4908-a13d-c3606910a8d4",
    "0e5bc24c-b462-428e-af0c-877e867b367d",
    "063fe7dd-7423-4a3b-83fc-5e6104558c48",
    "237eba0e-71a6-4e99-87ca-49347d1a73cf",
    "612b98d5-b036-41a2-abb3-6d7600800c4a",
    "6145e905-b3d9-4c81-81b2-3c512bf630dd",
    "9b3ec07c-5cd0-4760-b9ae-d6f6cb783b75",
    "df0a9560-2dd6-41d3-ba96-edb5b9f02cac",
    "d5a8eb76-281f-4f85-9c67-053385cd7e19",
    "4a6ff8f9-ab98-4124-899d-c08b5f1aec52",
    "757c8d57-e864-46b1-ba15-be5a6385bb8e",
    "939413a4-fdb2-43a5-8fef-b36472d9dc76",
    "f155299c-b34a-44e5-805c-68a603e83c67",
    "fcafb4b3-c400-4474-b4b3-49082ff8e6be",
    "4a84b109-af1d-48db-bf49-26e7751c907f",
    "ec968761-389c-404a-aee8-2df9722acf72",
    "23c57c36-81e8-40d6-8cf3-b2c0b0bb9412",
    "e4bdc0c8-7a47-4e01-b08d-99e40f4dbadb",
    "a581037e-0516-4124-957d-322a66209e85",
    "45697fde-5201-451c-9279-2c66df1a7a16",
    "c02e7828-9e02-44d1-bfdd-00ea700079c8",
    "c685f9f8-ea4d-4bc9-a7ca-57f9f431eaf3",
    "baa722a8-278b-48e6-b6ea-78de8b2bc126",
    "10d760e8-4299-4a9c-9d5f-0e0896f62d18",
    "6b26817d-10d6-4e1f-9348-d3d01ee35c61",
    "15fe7609-12fc-4eb5-a937-6ec3ad54194f",
    "bb61bd27-7dbb-44bb-a04c-4b3e787850bf",
    "9878eeb0-2826-4c8d-9ad6-30805ce453e3",
    "ded0c9c8-6b68-46a7-b028-064025f5c725",
    "af46b4b4-606a-4eb1-a801-e75cc848538b",
    "3373a089-91ad-4286-ba05-7151d35a0f6f",
    "701ce1b9-90b1-42ca-8b17-60e435c333ea",
    "01fd6d9c-522d-4f29-be57-89199f880cf6",
    "778fdfcf-b711-40b5-b2bb-2af2d5b9e0fc",
    "a0cf6fe4-f4e8-4ce5-98dd-51aa571d9b44",
    "5250494b-87ed-4bac-88c7-60e354715ac4",
    "47ec58ea-6901-4164-936a-f5e37d462513",
    "74b2456a-1284-417e-bf44-fef68d457bc9",
    "c1932b23-42bd-404a-b7a7-49852f27a34a",
    "e90b0664-13bf-4395-b3ef-cee4660e5633",
    "717cfbda-2df5-4822-8621-86329fef8f86",
    "0cc3dee2-5a78-4abf-89a6-314027350bfe",
    "87df0848-5af4-493b-8837-184b8f025c89",
    "ebf4c8d0-50d6-4e10-bdb1-ed4cbe31705c",
    "16b12213-d20a-4213-98ea-c94d0f3c2463",
    "f1e84d5d-8798-4758-8e2a-2610469f290b",
    "90ca72de-c220-41d4-a484-a97614592d76",
    "bea75d71-1da5-439a-a337-1d4fadfb7c29",
    "00b91747-514b-4b2c-88c0-c373b66570bd",
    "1ac4917c-95e8-4f33-8cec-03a71a8ff430",
    "bce4badb-eff0-4e1c-9473-7fd1a818f734",
    "2eb754ee-b372-4841-8480-d26bff56cbc2",
    "b85b0138-0d80-4da2-9c4e-7b6ec919d853",
    "68e1e80a-26f1-470f-a360-048d50d0700c",
    "42077522-22de-49ef-b0ba-f11593fa856e",
    "52035fae-0bd6-463d-b46a-136e69a2a218",
    "54255be0-e76d-4028-bb88-708b0c35cccb",
    "bbd931a3-492a-4052-968e-5efb3d35f129",
    "3e54f4f5-c609-49b4-8317-03040d50a4c8",
    "089d16e9-137f-4a70-aac0-5aa4597c3ddd",
    "8439c7f8-d98d-406f-ad3d-c66fa2fdfc80",
    "507d23e5-f1f5-41ae-b8d5-caae66fad1c8",
    "1c682f85-c27f-4a39-b660-62aaeaa383ca",
    "737a937b-17a0-4c6f-83b9-29db1045bab7",
    "96ed2b83-cc3c-4d78-878f-5b47d056d4cc",
    "a52a3dc9-37b6-4eb8-8f06-dca2674489bb",
    "d8ec8446-77d1-4e37-b6ee-28754e6bb330"
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
for match in map_files:
    for id_to_clean in principals_to_clean:
        for sp in match:
            if sp["principalId"] == id_to_clean:
                if sp["principalId"] not in cleanup_map:
                    cleanup_map[sp["principalId"]] = {}

                if sp["subscription"] not in cleanup_map[sp["principalId"]]:
                    cleanup_map[sp["principalId"]][sp["subscription"]] = []

                if sp["cleanup"] not in cleanup_map[sp["principalId"]][sp["subscription"]]:
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
