# SubscriptionPolicy

### Contents
- [Configurations](#configurations)
    - [configuration.json](#configurationjson)
    - [credentials.json](#credentialsjson)
- [Tasks](#tasks)
    - [Identity Tasks](#task-identitypy)
    - [Azure Virtual Machine Tasks](#task_computepy)
    - [Azure Key Vault Tasks](#task_keyvaultspy)
    - [Azure Storage Security](#task_storagepy)
    - [Azure Resource Group Compliance](#task_rg_compliancepy)


This repo has some utilities useful for managing certain aspects of your Azure Subscriptions. Particularly those that need or want to follow certain policies as we have done internally. 

For example, a proliferation of identities from Azure Active Directory or securing resources are great targets for automation. 

There are several tasks in this repo to do that and more, lets go over those briefly and then get into some of the details, but first lets cover the configuration settings required for the scripts.

# Configurations

## configuration.json
This is the main configuration for all of the task_*.py files that are used to execute functionality. The overview is below, for specifics about the details for each of the tasks open configuration.json.

### Overall Layout

> "automation" is a global boolean for all tasks. If a task has a flag indicating whether it can optionally perform a task or not (scripts in general will ask if those are set to true), automation will override that to run in an unattended mode.

```json
{
    "automation" : false,
    "subscriptions" : [
        "list of specific subscripiton ids to work on",
        "either you or your service principal must have",
        "access to them"
    ],
    "identity" : {},
    "groupCompliance" : {},
    "compute" : {},
    "keyvault" : {},
    "storage" : {}
}
```

### Tasks
automation and subscriptions are used globally in all tasks. These tell the scripts whether to override settings and which subscriptions to work on respectively. 

After that, each other section is broken down for specific tasks. 

```json
    "group_task_identity" : {
        "taskOutputDirectory" : "directory of where to store logging",
        "availableTasks" : { 
            "task_name" : {
                "Descripton" :"individual task description",
                "Parameters" : {
                    "param" : "Describe parameters that MUST be in the active task"
                }
            }
        },
        "active_tasks" : {
            "task_name" : {
                "param" : "actual param value"
            }
        } 
    }
```

## credentials.json
Every task will validate if there is a valid Azure login in effect. This can be overridden using this credentials.json file to supply an Azure Active Directory Service Principal. This is most useful in cases where the script will run in an automated fashion. 

Simply add in the information about your service principal and set the usePrincipal field to true. 



# Tasks

The available tasks are located in the root of this directory. They all derive out of the tools in one way or another out of microsoft.submaintenance (also in this repo)

Each section here briefly explains the tasks, more details can be found under microsoft.docs

## task_identity.py

This task is used to clean up role assignments which can get quite cluttered on an Azure Subscription over time. Some regular maintenance can go a long way to securing your subscription. 

This task should be run periodically.

||Task|Description|
|--|--|---|
|configuration.json<br>task group||identity|
||ReportAssignments|Creates a file for each subscription in configuration.subscriptions listing out all of the role assignments that have been created. Each output file is titled with the subscription ID and located in the path 'taskOutputDirectory'.|
||ClearUserAssignments|Removes any User role assignments on the subscription at the subscription level (ignoring Resource Group and Resource assignments) that helps to enforce a Azure Active Directory Group access policy.<br><br>There is a single parameter 'deleteAssignments' which is a boolean. Regardless of value output is recorded in the 'taskOutputDirectory' path.<br><br>This value can be overriden in an automation environment setting 'automation' global to true.|
||ClearInvalidPrincipals|Scans a sub for all Service Princpal assignments and ensures that the Service Principal still exists in Azure Active Directory. If the principal cannot be found, it's role assignments on the subscription are deleted.|


## task_compute.py

Virtual machines are generally prolific in an Azure Subscription. They can not only eat up your budget but can also eat uneccesary electricity. 

This task will deallocate (fancy word for properly shutting down an Azure virtual machine) virtual machines that are NOT part of a managed group (i.e. part of an AKS or other service cluster)

This task should be run whenever there are lull times in the office - weekend and holidays specifically. However, it's also not a bad thing to run it each night. 

||Task|Description|
|--|--|---|
|configuration.json<br>task group||compute|
||DeallocateUserCompute|Deallocates virtual machines across a subscription that are not in a managed group.<br><br>You can set include_managed_compute to true to include clusters.<br><br>stop_running determines whether you just want a report or a report AND shut down machines. This is overriden when the global automation flag is true.<br><br>All output ends up in taskOutputDirectory|


## task_keyvaults.py

This task has no pareters as of yet, it's sole job is to ensure that Soft Delete is enabled on all Azure Key Vaults. 

||Task|Description|
|--|--|---|
|configuration.json<br>task group||keyvault|
||EnableSoftDelete|Without parameters, scans all Azure Key Vaults in your subscriptions and enforces that Soft Delete functionality is enabled.<br><br>All output ends up in taskOutputDirectory|


## task_storage.py

This task ensures that your Azure Storage account has some basic security settings on it. 

- Disable public blob access
    - Prevents anyone from guessing a URL and downloading sensitive information, a common leak in cloud platforms.
- Enforce HTTPS connections onlyl
- Enable logging on an account
    - Should there be a breach, logging will help you identify the threat. 

This tag should be run periodically, weekly at a minimum. 

||Task|Description|
|--|--|---|
|configuration.json<br>task group||storage|
||EnableSecurity|Will enforce all three settings (public blob, https, logging) on storage accounts.<br><br>forceUpdate when true will go into each storage account and make the appropriate changes. When false, accounts with public blob access allowed are the only ones touched. This is overriden when the global automation flag is true.<br><br>All output ends up in taskOutputDirectory|



## task_rg_compliance.py

This task is used to enforce a specific policy in which all users MUST apply specific tags to their resource groups. A resource group without the associated tag(s) will be deleted from the subscription with all of it's resources. 

> __NOTE__: When enabled to perform the delete, it will first remove any locks configured on the group and any of it's resources. 

Exceptions to this rule:
    - Any resource group that is managed by another resource group (example: AKS Cluster) will not be disturbed in any way. 
    - Any default Azure resource group will also be left undisturbed. These are identified in the configuration.json file. Any group name that starts with a value found in groupCompliance.active_tasks.EnforceCompliance.ignored

Tags required for the scan are located at groupCompliance.active_tasks.EnforceCompliance.required_tags

||Task|Description|
|--|--|---|
|configuration.json<br>task group||groupCompliance|
||DeleteGroups|A non automatable process to removing specific resource groups from a subscription. User must provide the subscription ID and resource group names in configuration.json.|
||EnforceCompliance|Enforces the tagging policy described above.<br><br>delete_on_missing - when true will delete any resource group that fails the basic compliance check. When false, simply outputs a log for each subscription. This is overriden when the global automation flag is true.<br><br>All output whether an action occurs or not ends up in taskOutputDirectory|



