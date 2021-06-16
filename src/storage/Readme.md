# Storage

Quick script to ensure that whatever Azure Storage Accounts you can get hold of have Blob Public Access disabled. This is a threat in all cloud storage services and by default, and has been for years, this value is set to True (allow it)

Running this script uses configuration.json and the subscripiton list there. Put in 
whatever subscriptions you want to scan for open storage. 

Script also requres storage.storageSummaryDirectory for logging. A log is generated for each subscription with [subid].json in that directory. 

What it does:
    - Searches for all storage accounts
    - For each
        - Determine if in a managed RG
        - Determine if blob public access is enabled
            - If enabled, disabled
        - Record status in an overall stat
    - Print the stat at the end.

There are some caveats that an AMA that has a storage account that is NOT set up correctly, you will not be able to update the storage because Managed Applications are protected with deny policies. For that matter so are Databricks instances. 
