"""
Get the S360 report on overpriviledge SP's from Lens, save the file
locally to CSV format then use this script to generate PS1 content
to delete the role assignments. 
"""
import json
import os
from microsoft.submaintenance.utils.csvloader import S360Reader
from microsoft.submaintenance.utils import PathUtils

OUTPUT_DIR = "./logs/360spParsed"
INPUT_FILE = "./your_s360_csv_file"

AAD_REMOV_COMMAND = "az role assignment delete --assignee {} --scope {} --role {} --subscription {}"

# Parse it by sub
s360Entities = S360Reader.read_file(INPUT_FILE)
subs = {}
for entity in s360Entities:
    if entity.subscriptionName not in subs:
        subs[entity.subscriptionName] = []

    rm_command = AAD_REMOV_COMMAND.format(
        entity.principalId,
        entity.roleScope,
        entity.roleId,
        entity.subscription
    )

    subs[entity.subscriptionName].append(rm_command)


# Write it out
output = PathUtils.ensure_path(OUTPUT_DIR)
for sub in subs:
    log = os.path.join(output, "{}.txt".format(sub))
    with open(log, "w") as output_log:
        for rm in subs[sub]:
            output_log.write("{}\n".format(rm))


print("Done", output)
