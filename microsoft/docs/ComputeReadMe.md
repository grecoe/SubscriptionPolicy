# Compute Deallocation/Reporting

> NOTE: Actual machine deallocation is currently disabled regardless of flags sent in. Commented code starts on line 17 in src/utils/vm.py

We are all stewards of Azure and the planet. Leaving running machines up 24x7 is not good for either. 

Virtual Machine deallocation is somthing we are going to force upon all users in our subs. Schedule __TBD__

This script will find all VMs accross subscriptions and determine if
- It is in a managed group
- It is running
- If running, should it deallocate it?
    - If the configuration flag for compute.include_managed_compute is true, compute in managed resource groups are included in the run. Otherwise they are not loaded.
    - If the configuration flage for compute.stop_running is true, any compute detected will be deallocated.  


This process uses the configuration.json in the root of the repo. 

You must fill in "subscriptions" with ID's of subs you want to check. The other settings are under the compute object.

|Field|Content|
|-----|-------|
|include_managed_compute|Boolean value indicating whether to include managed (cluster) compute in calculations or not. A managed compute is one that lives in a resource group that is managedBy another<br><br>True means to check the power status of managed compute and if asked, to deallocate the machine.<br><br>False means that any machine in a managed group will not have its power status checked and hence not subject to deallocation.|
|stop_running|Boolean flag that indicates the runner of the script wants running VMs deallocated. If True user must validate the option when the script starts.|
|computeDirectory|Already defaulted, but a directory to create/use in the execution path where an overall report for each subscription will be placed and named [subid].json.|

### Execute the compute compliance script
```
python .\stop_compute.py
```
