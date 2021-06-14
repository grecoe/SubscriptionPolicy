"""
When running p4_clean_principals.py run in a new cmd window.

Select all the output and put it in a text file then run this
script against that output.
"""

output = "./cleanupoutput.txt"

file_content = None
with open(output, "r") as cleanup:
    file_content = cleanup.readlines()

attempts = 0
failures = 0
for line in file_content:
    if line.startswith("Removing principal"):
        attempts += 1    
    if line.startswith("ERROR:"):
        failures += 1

print(attempts, failures)        