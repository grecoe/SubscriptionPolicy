# Open Endpoints

This essentially parses out information from the S360 report for the [C + AI] Network Isolation. 


## Parsing out the errors 
Due to reporting on S360, there is no easy export of the information from Lens and it has to be done by hand. 

1. Go to the S360 Dashboard
2. Click on [C + AI] Network Isolation missed SLA
3. For each entry:
    - Click on the NetIsoActionItems link 
    - This brings up Lens but you cannot export.
    - Highlight all content in the bottom table and paste it to a file in this directory (preferably named *.tsv so you know whats in it)
4. When done, open up plot_items.py and modify line 30 with whatever files you have created from step 3. 
5. Run the script, it will create a file for each subscription denoted in the downloaded TSV files in the open_endpoints local directory.

Each of the generated files is a JSON structure that calls out
1. The resource type causing the alert
2. For each resource it lists out
    - Azure Resource ID
    - Azure Resource Name
    - Azure Resource Group
    - NOTE: Two of the above can be gleaned from the resource ID but they are there anyway. 

## Solutions
This is harder because it's pretty new so this section is mostly TBD. However, the lowest hanging fruit is to determine if the resource identified is really needed or not. If not, delete it, if it is needed - that's the TBD part.
