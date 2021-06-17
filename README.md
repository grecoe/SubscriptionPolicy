# SubscriptionPolicy

This repo has some utilities useful for managing certain aspects of your Azure Subscriptions. 

Code in each section is configured through the configuration.json file. Mainly, you will need to ensure you add in your subscription ID's 

## Login Validation
Each process will validate that there is a valid az login in effect. This can be overridden by using the credentials.json file.

The credentials.json file contains information about a service principal, i.e. 

|Field|Value|
|----|----|
|usePrincipal|Boolean flag. If true the following fields MUST be valid. If false code will only verify there is a valid login or throw if not. |
|application|SP ID required if usePrincipal=True|
|credential|SP Password required if usePrincipal=True|
|tenent|SP Tenent required if usePrincipal=True|

## S360 Issues

### Over Privileged Service Principals
Go to src/principals -> ReadMe.md for more information

This helps identify, detect owners of, and cleanup service principals that are an issue with S360. 


## General Policy Compliance

### Resource Group Tagging
Go to src/tagging -> Readme.md for more information

Untagged resource groups are deleted via a script run at whatever frequency the team determines. 

## Storage - No public blob access.
Go to src/storage -> Readme.md for more information

Scans subscriptions for storage accounts. If an account has public blob access enabled it is disabled.

### Compute Deallocation
Go to src/compute -> ReadMe.md for more information

Scans subscriptions for VMs and optionally deallocates running machines at whatever frequency teh team determines.

## RBAC Access
Go to src/roles -> Readme.md for more information

Scans a subscription for all roles or alternatively, takes sub level user roles and clears them. 