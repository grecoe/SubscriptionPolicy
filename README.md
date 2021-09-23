# SubscriptionPolicy
<sub>Dan Grecoe is a Microsoft Employee</sub>

### Contents
- [Configurations](#configurations)
    - [configuration.json](#configurationjson)
    - [credentials.json](#credentialsjson)
- [Tasks](#tasks)
    - [Identity Tasks](#task_identitypy)
    - [Azure Virtual Machine Tasks](#task_computepy)
    - [Azure Key Vault Tasks](#task_keyvaultspy)
    - [Azure Storage Security](#task_storagepy)
    - [Azure Resource Group Compliance](#task_rg_compliancepy)
- [Automation Tasks](./WeeklyTasks.md)
- [Tools](#tools)
    - [S360 Overprivileged Service Principals](#tool_s360_sppy)
    - [Generate PS1 for Overprivileged Service Principals](#tools_parse_s360sppy)
    - [S360 Open Endpoints](#tool_s360_endpointspy)
    - [Flush Subscription](#tool_flushsubpy)
    - [Purge Deleted Azure Key Vaults](#tool_purge_sd_vaultspy)


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

[Return to top](#contents)

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

[Return to top](#contents)

## task_compute.py

Virtual machines are generally prolific in an Azure Subscription. They can not only eat up your budget but can also eat uneccesary electricity. 

This task will deallocate (fancy word for properly shutting down an Azure virtual machine) virtual machines that are NOT part of a managed group (i.e. part of an AKS or other service cluster)

This task should be run whenever there are lull times in the office - weekend and holidays specifically. However, it's also not a bad thing to run it each night. 

||Task|Description|
|--|--|---|
|configuration.json<br>task group||compute|
||DeallocateUserCompute|Deallocates virtual machines across a subscription that are not in a managed group.<br><br>You can set include_managed_compute to true to include clusters.<br><br>stop_running determines whether you just want a report or a report AND shut down machines. This is overriden when the global automation flag is true.<br><br>All output ends up in taskOutputDirectory|

[Return to top](#contents)

## task_keyvaults.py

This task has no pareters as of yet, it's sole job is to ensure that Soft Delete is enabled on all Azure Key Vaults. 

||Task|Description|
|--|--|---|
|configuration.json<br>task group||keyvault|
||EnableSoftDelete|Without parameters, scans all Azure Key Vaults in your subscriptions and enforces that Soft Delete functionality is enabled.<br><br>All output ends up in taskOutputDirectory|

[Return to top](#contents)


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

[Return to top](#contents)


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

[Return to top](#contents)

# Tools

This section contains a few tools to be used to help with S360 compliance after items have gone out of SLA whereas the task_* scripts try to prevent them becoming an issue in the first place. 

Read the descriptions below, more detailed instructions are located in each script file. 

## tool_s360_sp.py
> This tool cannot be automated.

One of the biggest issues faced when a subscription is put under the security lens of a production system is Overprileged Service Principals. 

This happens as teams are relying on SP's to provide functionality/access from one system to the other but generally don't clean them up. 

Using the output from S360, this tool will clear out the reported assignments that are not in compliance with the security standard. 

Read the doc string at the top of the file for more instructions. 


[Return to top](#contents)

## tool_s360_endpoints.py

> This tool cannot be automated.

Another significant issue with S360 reporting is Network Isolation. This generally shows up in the form of service having open endpoints that are not allowed with the production level security requirements. 

This tool doesn't neccesarily solve the issue for you but it does whittle down lists of non compliant resources to a focused list of what needs to be worked on. The reason for this?

1. The reports can be out of date, so the tool verifies that the resource group in which the resource resides in still exists. We experienced several items being reported on days after they no longer existed in the Subscription. 
2. The report can also contain duplicates which effectively are noise and get filtered out of the net result. 

See the script file for details on how to collect the information to filter. 

[Return to top](#contents)

## tools_parse_s360sp.py
> This tool cannot be automated.

[Return to top](#contents)

This tool is used for generating files to send to other teams to remove their over privileged service principals. 

This happens because you can see the S360 report but do not have physical access to the subscription. 

You run this tool to produce a .txt file with all of the PS1 commands neccesary to resolve the principal problem. Since you cannot mail .ps1 files tell the recipient to rename it to .ps1

On line 12 for the value of INPUT_FILE put in the local file you retrieved from Lens Explorer containing all of the service principals to remove. 

## tool_flushsub.py

> This tool cannot be automated.

There are times you are going to need to drop an entire sub. 

On line 15 of the script, put in the subscription ID of the subscription you want to clear.

When executed the script will

- Obtain a list of all resource groups in the subscription
- For every resource group that is not managed (i.e. AKS clusters/etc)
    - Remove any locks that may be present
    - Delete the resource group


Wait at least an hour before reviewing the subscripiton that was targeted. If there are still any resources/resource groups you will likely have to remove them by hand. 

[Return to top](#contents)

tool_purge_sd_vaults.py

## tool_purge_sd_vaults.py

Delete key vaults can linger for some time. This tool is part of the autocleanup.py script so it can be automated, but it can also be run standalone. 

Any deleted key vault that does not have purge protection enabled will be permanantly deleted. 

[Return to top](#contents)
