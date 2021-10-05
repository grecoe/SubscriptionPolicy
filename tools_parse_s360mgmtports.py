"""
When machines are tagged with having open management ports you can pull the 
report down from lens and use this to parse out the results into more 
managable chunks. 
"""
import json
import os
from microsoft.submaintenance.utils.csvloader import S360Reader
from microsoft.submaintenance.utils import PathUtils

# Create output path
OUTPUT_DIR = "./logs/ManagementPorts"
usable_path = PathUtils.ensure_path(OUTPUT_DIR)

# Location of the S360 management port lens explorer export
s360_managment_port_export_lens = "C:\\...\\b119de8c-25b8-49ae-84c3-8a76ba064766_data.csv"

# Columns we are interested in, though not really used here
columns = ["ServiceName", "SubscriptionName","AssessmentName", "ResourceId"]
report = S360Reader.read_file(s360_managment_port_export_lens)

# Create the data
breakdown = {} # {service, {sub, {assessment,[resourceId]}}}
for mchn in report:

    if mchn.ServiceName not in breakdown:
        breakdown[mchn.ServiceName] = {}
    
    sub_portion = breakdown[mchn.ServiceName]
    if mchn.SubscriptionName not in sub_portion:
        sub_portion[mchn.SubscriptionName] = {}
    
    assesment_portion = sub_portion[mchn.SubscriptionName]
    if mchn.AssessmentName not in assesment_portion:
        assesment_portion[mchn.AssessmentName] = []

    resource_portion = assesment_portion[mchn.AssessmentName]
    resource_portion.append(mchn.ResourceId)


for service_name in breakdown:
    for sub in breakdown[service_name]:
        filename = os.path.join(usable_path, "{}_{}.json".format(service_name,sub))
        with open(filename, "w") as outputfile:
            outputfile.writelines(json.dumps(breakdown[service_name][sub], indent=4))

print("Done")

"""
for sub in breakdown:
    filename = os.path.join(usable_path, "{}_{}.json".format(sub))
    with open(filename, "w") as outputfile:
        outputfile.writelines(json.dumps(breakdown[sub], indent=4))
"""        
