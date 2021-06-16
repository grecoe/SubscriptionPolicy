# Weekly Sub Grooming Tasks

This is the list of tasks that should occur every week. Preferably in an automated way. 

Step 5 for compute is an unknown, but at least run Friday nights. 

1. Verify that configuration.json contains all of the subscription ID's that the scripts are intended to target. 
2. Clean up untagged resource groups
    - Ensure tagging.delete_on_missing is true
    - Run src/tagging/check_tagging.py
3. Enforce storage account settings - but force not needed after first time
    - Ensure storage.forceUpdate is false (unless you want to update all or first time, depending on your sub(s) this could be quite slow.)
    - run src/storage/update_storage.py
4. Enforce group only access to subscriptions by deleting "User" level access at the Subscription level
    - Ensure roles.deleteUserRoles is true (false will just give you a summary)
    - run src/roles/clear_user_roles.py    
5. Turn off user compute
    - Ensure compute.stop_running = true (shut down VM's found)
    - Ensure compute.include_managed_compute = false (won't shut down clusters)
    - run src/compute/stop_compute.py


## s360 Service Principals
Look at src/principals/Readme.md as it's a multi step process that needs data from Lens to proceed. I don't know of any way that really can be automated.     