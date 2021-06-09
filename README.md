# SubscriptionPolicy

This repo has some utilities useful for managing certain aspects of your Azure Subscriptions. 

Code in each section is configured through the configuration.json file. Mainly, you will need to ensure you add in your subscription ID's 

## S360 Issues

### Over Privileged Service Principals
Go to src/principals and the ReadMe.md

This helps identify, detect owners of, and cleanup service principals that are an issue with S360. 


## General Policy Compliance

### Resource Group Tagging
Go to src/tagging and teh Readme.md

Untagged resource groups are deleted via a script run at whatever frequency the team determines. 