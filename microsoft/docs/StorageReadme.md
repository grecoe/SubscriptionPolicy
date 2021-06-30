# Storage

Quick script to ensure that whatever Azure Storage Accounts you can get hold of have Blob Public Access disabled. This is a threat in all cloud storage services and by default, and has been for years, this value is set to True (allow it)

Running this script uses configuration.json and the subscripiton list there. Put in 
whatever subscriptions you want to scan for open storage. 

Script also requres storage.storageSummaryDirectory for logging. A log is generated for each subscription with [subid].json in that directory. 

Finally, storage.forceUpdate is a bool. If set true the output in the log is irrelevant because it will force update any storage account it finds regardless of 
what settings are already there. If false, it only updates accounts that have public blob access enabled. 

What it does:
    - Searches for all storage accounts
    - For each
        - Determine if in a managed RG
        - Determine if blob public access is enabled IF forceUpdate is not set
            - If enabled, disabled
        - If the account is open for blob OR forceUpdate is true
            - Disable public blob access
            - Enforce HTTPS only
            - Enable logging 
        - Record status in an overall stat*
    - Print the stat at the end.

*Again, stats if forceUpdate is set to true are sort of irrelevant because it will tag EVERY group as open. 

There are some caveats that an AMA that has a storage account that is NOT set up correctly, you will not be able to update the storage because Managed Applications are protected with deny policies. For that matter so are Databricks instances. 
