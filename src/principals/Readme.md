# SP Detection

This path to do cleanup requires that you follow each step one after the other to ensure you have the correct data.

## 1. Get Out of SLA Service Principals
- Go to S360 select Over privileged service principals
- Click on the Out of SLA count column
- Click on __Explore with lens__
- In lens, top right corner choose
    - Actions>Export>CSV All Columns 
    - Save this to this current directory (or note the path)

## 2. Get Role Assignments
At the root of this project, open the configuration.json file and provide the subscription ID's of the subscripitons that would be subject to the list from S360.

Execute:
```
python .\get_roles.py
```

This will create a folder in this location from the configuration setting principals.roleDirectory with a file with all role assignments. There is one file per subscription and named [subid].json 

## 3. Pair S360 Principals to given subscriptions
This next script, using the configuration settings for principals.roleDirectory for input and principals.mapDirectory as well as the actual CSV file collected from Lens will map the principals to a given subscription. 

Open the file match_s360_to_subs.py and modify line 35 to the acutal file you downloaded from Lens. 

An example where the file is in the same directory as the script
```
warnings = S360Reader.read_file("./UnusedServicePrincipals.csv")
```

Once all done, run the command 
```
python .\match_s360_to_subs.py
```

This will produce a file [subid].json in the directory noted in the configuration at principals.mapDirectory

- Any SP found on a role assignment for a sub paired with an SP that was taken from teh S360 list.
- Content is
    - principalId
    - applicationId
    - principalName
    - owner (email address if found or an id if not)
    - role
    - subscription
    - cleanup (script that will remove the role assignment)

## 4. Tie owners to a list of SP's they own
This stage creates a new local folder using the configuraiton principals.ownerMap setting. Each file is named with the owner name of the SP's that will be contained within it. 

This mapping is to ensure that we know who owns which SP which needs to have it's role assignment removed. Once done, notify the owner to verify that the SP's are either valid or truly invalid. 

To generate these owner files, just ensure that you've followed the other steps first then:
```
python .\map_owner.py
```

## 5. Clean up role assignments

Once a user has come back with a confirmation that the principals can be removed, copy the contents of their owner map file ino teh clean_principals.py file at line 32. 

Again, this assumes that all other steps have been performed. Once you have modified the file run

```
python .\clean_principals.py
```

When this completes (it will go fase) notify the user that you have cleaned up role assignments and they will have to delete the SP from Azure Active Directory as they are the only one with that right. 

Instructions for the user when done:
```
1. Log into Azure Portal
2. Click on Azure Active Directory
3. Enter a principal id in the search 
4. On the item, select Properties > Delete
```
