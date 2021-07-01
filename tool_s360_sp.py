"""
S360 reports overprivileged service principals that have been given role
assignments to your subscriptions. 

This generally means that they have been assigned but not used for some time. 

The report in s360 for this brings you to Lens. From lens with the report you 
export the contents using the upper right hand corner

Actions > Export > CSV All Columns

This creates a JSON on your machine with the entries. Put in the file path below
and the tool will remove the specific role assignments from your subscription. 

YOU MUST BE LOGGED IN WITH RIGHTS TO THE SUBS OR HAVE AN SP TO DO SO

Output is to the command line only and dumps out number of entries recieved, roles
removed and for each sub how many roles were removed. If the total vs removed differ
it is because the assignment has been cleared before running the tool. 
"""
import json
from microsoft.submaintenance import AzIdentities
from microsoft.submaintenance.utils import AzLoginUtils


CREDENTIALS_FILE = "./credentials.json"
CONFIGURATION_FILE = "./configuration.json"

# Ensure a login and switch to SP if requested
try:
    AzLoginUtils.validate_login(CREDENTIALS_FILE)
except Exception as ex:
    print(str(ex))
    quit()




az_id = AzIdentities()
s360report = "C:\\gitrepogrecoe\\SubscriptionPolicy\\__dump\\src\\principals\\June29.csv"
res = az_id.clear_s360_principals(s360report)
print(json.dumps(res, indent=4))