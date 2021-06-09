# Tag Compliance

Tag compliance is something we are going to force upon all users in all our subs. It requires that the 'alias' tag be applied to a resource group. 

This process uses the configuration.json in the root of the repo. 

You must fill in "subscriptions" with ID's of subs you want to check. The other settings are under the tagging object.

|Field|Content|
|-----|-------|
|required_tags|List of lower case only string tag names to enforce existence. Currently nly alias is enforced.|
|ignored|List of case sensitive strings for resource groups to ignore. This can ONLY be default created groups by Azure itself.<br><br>Additionally, any resource group that is managed by another (i.e. AKS/Databricks/etc.) will also be ignored. However, it the managing group is deleted the managed group will be as well.|
|delete_on_missing|Boolean flag to indicate if a valid resource group is found with required tags missing, should it be deleted. If True user must validate the option when the script starts.|
|tagDirectory|Already defaulted, but a directory to create/use in the execution path of the cleanup script to log what occured.|

### Execute the tagging compliance script
```
python .\checktagging.py
```
