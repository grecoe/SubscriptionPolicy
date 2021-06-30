# RBAC Roles

With an influx of users given access to the AGCI AI subscriptions, all RBAC access will now occur through Azure Active Directory Groups. 

Each stream is allocated two groups in which to add users:

> AGCI[StreamName]<br>AGCI[StreamName]Guest

> NOTE: Use 

## AGCI[StreamName]
Members of CoreEng are owners of this group as well as the actual stream lead. 

This group should contain ONLY members of the AGCI AI organization.

The lead is responsible for keeping this list up to date. 

## AGCI[StreamName]Guest
Any other internal or external user that a lead want's to provide access to the sub with. 

## Scripts
Uses the master configuration.json in this repository whose section is "roles". There is only a sigle setting currently which is "roleSummaryDirectory" which is used with teh scan_roles.py script.

### scan_roles.py
Ensure that "subscriptions" is filled in for the configuration.json file. 

Generates an all up RBAC roles summary file in the local directory identified by "roleSummaryDirectory" for each subscription. Each subscription gets it's own file called {subid}.json

```
python .\scan_roles.py
```

### clear_user_roles.py
You must put in a valid subscription ID in configuration.json for roles.clearRolesSubId for the subscription to be acted upon. 


The script looks for top level roles assigned to a subscription and deletes any "User" roles if roles.deleteUserRoles in configuration.json is true otherwise it just dumps out what would happen. 

