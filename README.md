# SubscriptionPolicy

This repo has some utilities useful for managing certain aspects of your Azure Subscriptions. 

Code in each section is configured through the configuration.json file. Mainly, you will need to ensure you add in your subscription ID's 

## S360 Issues

### Over Privileged Service Principals
Go to src/principals -> ReadMe.md for more information

This helps identify, detect owners of, and cleanup service principals that are an issue with S360. 


## General Policy Compliance

### Resource Group Tagging
Go to src/tagging -> Readme.md for more information

Untagged resource groups are deleted via a script run at whatever frequency the team determines. 

### Compute Deallocation
Go to src/compute -> ReadMe.md for more information

Scans subscriptions for VMs and optionally deallocates running machines at whatever frequency teh team determines.

## RBAC Access
Go to src/roles -> Readme.md for more information

Scans a subscription for all roles or alternatively, takes sub level user roles and clears them. 