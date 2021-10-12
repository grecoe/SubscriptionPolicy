"""
Task using configuration to get the subscriptions then

- Does not collect groups with no alias as they will be deleted
- Collect groups that have an alias not found in AAD
- Collect groups by age that meet certain thresh holds
    - 30 days old - initial warning
    - 60 days old - second warning
    - 90 days old - final warning before delete

NOTE: This code will NOT delete any groups at this time

NOTE: All groups, regardless of alias tag are also tagged
with a lifetime object to tell us when it was first/last seen
and it's age (for the warnings listed above)
"""


import os
from datetime import datetime
import typing
import json
from microsoft.submaintenance.utils import(
    Configuration,
    AzLoginUtils,
    PathUtils,
    AzResourceGroupUtils,
    AzRolesUtils
)

CONFIGURATION_FILE = "./configuration.json"

class Lifetime:
    LIFETIME_TAG = "lifetime"
    
    def __init__(self, existing:str = None):
        self.first_seen = None
        self.last_seen = None
        self.scans = 0
        self.age = 0

        if existing:
            existing = existing.replace("'", '"')
            props = json.loads(existing)
        
            if props:
                for prop in props:
                    setattr(self, prop, props[prop])

    def get_updated_tag_content(self):
        return json.dumps(self.__dict__).replace('"', "'")

    def get_lifetime_tag_update_text(self):
        return "tags.{}=\"{}\"".format(Lifetime.LIFETIME_TAG, lifetime_obj.get_updated_tag_content())

    @staticmethod
    def update_group_lifetime_tag(lifetime_data:str) -> typing.Any: # Lifetime object
        """return the value of the lifetime tag to udpate"""
        lifetime_obj = (Lifetime() if not lifetime else Lifetime(lifetime))

        utc_now = datetime.utcnow()
        current_date = "{}-{}-{}".format(utc_now.year, utc_now.month, utc_now.day)

        lifetime_obj.scans += 1
        lifetime_obj.last_seen = current_date
        if not lifetime_obj.first_seen:
            lifetime_obj.first_seen = current_date
        else:
            first = datetime.strptime(lifetime_obj.first_seen, "%Y-%m-%d")
            last = datetime.strptime(lifetime_obj.last_seen, "%Y-%m-%d")
            
            lifetime_obj.age = (last-first).days
        
        return lifetime_obj

class ScanResult:
    AGE_NO_WARNING = -1
    AGE_WARNING_DAYS = 30
    AGE_WARNING_2_DAYS = 60
    AGE_DELETE_DAYS = 90

    def __init__(self):
        self.untagged_groups:typing.List[str] = []
        self.unknown_alias:typing.List[typing.Dict[str,str]] = []
        self.aged_groups:typing.Dict[int, typing.List[typing.Dict[str,str]]] = {}

    def add_aged_group_data(self, age_warning:int,  group_data:dict):
        if age_warning == ScanResult.AGE_NO_WARNING:
            return

        if age_warning not in self.aged_groups:
            self.aged_groups[age_warning] = []

        self.aged_groups[age_warning].append(group_data) 
    
    @staticmethod
    def get_age_warning(age:int) -> int:
        if age >= ScanResult.AGE_WARNING_DAYS and age < ScanResult.AGE_WARNING_2_DAYS:
            return ScanResult.AGE_WARNING_DAYS
        if age >= ScanResult.AGE_WARNING_2_DAYS and age < ScanResult.AGE_DELETE_DAYS:
            return ScanResult.AGE_WARNING_2_DAYS
        if age >= ScanResult.AGE_DELETE_DAYS:
            return ScanResult.AGE_DELETE_DAYS

        return ScanResult.AGE_NO_WARNING

# Ensure a login and switch to SP if requested
try:
    # SP doesn't have rights to AAD don't use one
    AzLoginUtils.validate_login(None)
except Exception as ex:
    print(str(ex))
    quit()

# Get and validate the minimum on the configuration
configuration = Configuration(CONFIGURATION_FILE)
if not hasattr(configuration, "subscriptions") or len(configuration.subscriptions) == 0:
    raise Exception("Update configuration.json with sub ids")

# Perform scan here
complete_results:typing.Dict[str, ScanResult] = {}

for subid in configuration.subscriptions:
    print("Processing", subid)

    scan_result = ScanResult()
    complete_results[subid] = scan_result
    
    groups = AzResourceGroupUtils.get_groups(subid)
    for group in groups:

        aliases = AzResourceGroupUtils.get_tag_content(group, "alias")
        lifetime = AzResourceGroupUtils.get_tag_content(group, Lifetime.LIFETIME_TAG)

        # Update/create a lifetime tag content object
        lifetime_obj = Lifetime.update_group_lifetime_tag(lifetime)
        AzResourceGroupUtils.update_group_tags(subid, group["name"], lifetime_obj.get_lifetime_tag_update_text())

        # Update age warnings
        age_warning = ScanResult.get_age_warning(lifetime_obj.age)
        scan_result.add_aged_group_data(age_warning, { "group" : group["name"], "alias" : aliases})

        # Action based on presence of alias tag
        if not aliases:
            scan_result.untagged_groups.append(group["name"])
        else:
            # A couple of them have multiple alias' in them so make
            # sure we account for all of them (and not flag as unknown)
            aliases = aliases.split(' ')

            for alias in aliases:
                # If the alias is NOT in AD then flag it
                object_ret = AzRolesUtils.get_aad_user_info("{}@microsoft.com".format(alias))

                if not object_ret:
                    scan_result.unknown_alias.append({ "group" : group["name"], "alias" : alias})



print("Dumping results....")
# Dump out results....probably to a disk
usable_path = PathUtils.ensure_path("./logs/aged_groups")
for sub_id in complete_results:
    outputs = {}
    # No need to report on untagged groups as they get deleted.
    # if len(complete_results[sub_id].untagged_groups):
    #     outputs["Untagged Groups"] = complete_results[sub_id].untagged_groups
    if len(complete_results[sub_id].unknown_alias):
        outputs["Unknown Alias"] = complete_results[sub_id].unknown_alias
    if len(complete_results[sub_id].aged_groups):
        outputs["Age Warnings"] = complete_results[sub_id].aged_groups
    
    file_path = os.path.join(usable_path, "{}.json".format(sub_id))
    with open(file_path, "w") as output_file:
        output_file.writelines(json.dumps(outputs, indent=4))
