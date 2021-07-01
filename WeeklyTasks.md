# AG CI AI Weekly Tasks

As of June 18, 2021 a series of tasks are run on Saturday at 0200 UTC time. 

The group of tasks run can be found in autocleanup.py in this directory. 

The tasks are all configured through the configuration.json also found in this directory. Details of setting can be found in each of the task_* scripts and also described in the [Readme.md](./README.md) master document. 

## Tasks run in order

> To ensure that all tasks will run in unattended mode AND perform actual work, modifiy configuration.json :<br><br>"automation" : true<br><br>"subscriptions" contains a list of subscriptions.<br><br>credentials.json has a valid Service Principal identified with access to the list of subscriptions above. 

|Order|Script|Description|
|----|----|----------------------|
|1|task_rg_compliance.py|Delete resource groups that do not follow the compliance rules as defined by the team:<br>- Is not a managed group<br>- Is not a default Azure Resource Group<br>- Is not tagged with required tags.|
|2|task_identity.py|1. Remove all User level role assignments on the set of subscriptions at the subscription level to enforce AAD group access.<br><br>2. Clear Service Principals that have an assignment in the subscription but are not found in AAD.|
|3|task_compute.py|Deallocate (shut down) personal virtual machines which are VM's not contained in a managed resource group.|
|4|task_storage.py|For all Azure Storage accounts found in the subscripiton FORCE the following:<br><br>- Disable public blob access<br>- Enforce HTTPS only access<br>- Enforce logging|
|5|task_keyvaults.py|For all Azure Key Vaults found in the subscription verify that it has Soft Delete enabled. If not enable it.|

