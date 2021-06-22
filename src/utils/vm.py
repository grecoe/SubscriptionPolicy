import json
import os
from time import perf_counter
from .cmdline import CmdUtils


class Compute:
    def __init__(self):
        self.name = None
        self.sku = None
        self.location = None
        self.resourceGroup = None
        self.managedGroup = None
        self.subscription = None
        self.powerState = None

    def deallocate(self):
        print("Deallocating {} in sub {}".format(self.name, self.subscription))
        CmdUtils.get_command_output(
            [
                "az",
                "vm",
                "deallocate",
                "--name",
                self.name,
                "--resource-group",
                self.resourceGroup,
                "--subscription",
                self.subscription,
                "--no-wait"
            ]
        )

class ComputeUtil:
    @staticmethod
    def get_running_compute(compute_list):
        return [x for x in compute_list if x.powerState == "PowerState/running"]

    @staticmethod
    def parse_compute_to_report(compute_list):
        managed_compute = [x for x in compute_list if x.managedGroup is not None]
        deallocated_compute = [x for x in compute_list if x.powerState == "PowerState/deallocated"]
        running_compute = [x for x in compute_list if x.powerState == "PowerState/running"]
        stopped_compute = [x for x in compute_list if x.powerState == "PowerState/stopped"]
        running_names_unmanaged = [x.name for x in running_compute if x.managedGroup is None]
        running_names_managed = [x.name for x in running_compute if x.managedGroup is not None]

        regions = {}
        for vm in compute_list:
            if vm.location not in regions:
                regions[vm.location] = 0
            regions[vm.location] += 1


        report = {
            "overall" : {
                "total" : len(compute_list),
                "managed" : len(managed_compute)
            },
            "regions" : regions,
            "states" : {
                "running" : len(running_compute),
                "deallocated" : len(deallocated_compute),
                "stopped" : len(stopped_compute)
            },
            "running" : {
                "unmanaged" : running_names_unmanaged,
                "managed" : running_names_managed
            }
        }

        return report

    @staticmethod
    def get_compute(sub_id:str, get_power_for_managed=False):
        return_computes = []
        group_states = {}

        print("Getting computes for ", sub_id)
        compute_vm = CmdUtils.get_command_output(
            [
                "az",
                "vm",
                "list",
                "--subscription",
                sub_id
            ]
        )

        for vm in compute_vm:
            print("Collecting VM ", vm["name"])

            current_comp = Compute()
            for key in vm:
                setattr(current_comp, key, vm[key])

            current_comp.name = vm["name"]
            current_comp.location = vm["location"]
            current_comp.resourceGroup = vm["resourceGroup"]
            current_comp.subscription = sub_id
            current_comp.sku = vm["hardwareProfile"]["vmSize"]

            # If group is managed it doesn't matter if it's running
            # because we can't stop it anyway
            if current_comp.resourceGroup not in group_states:
                group_states[current_comp.resourceGroup] = ComputeUtil.__get_group_managed_state(
                    current_comp.resourceGroup,
                    sub_id
                )

            current_comp.managedGroup = group_states[current_comp.resourceGroup]

            if current_comp.managedGroup is None or get_power_for_managed:
                print("Power state of {} - {}".format(
                    "managed" if current_comp.managedGroup is not None else "unmanaged",
                    current_comp.name
                    )
                )

                instance = CmdUtils.get_command_output(
                    [
                        "az",
                        "vm",
                        "get-instance-view",
                        "--name",
                        current_comp.name,
                        "--resource-group",
                        current_comp.resourceGroup,
                        "--subscription",
                        current_comp.subscription
                    ]
                )

                current_comp.powerState = instance["instanceView"]["statuses"][1]["code"]
            
            return_computes.append(current_comp)

        return return_computes

    @staticmethod
    def __get_group_managed_state(group:str, subid:str):
        group_state = CmdUtils.get_command_output(
            [
                "az",
                "group",
                "show",
                "--name",
                group,
                "--subscription",
                subid
            ]
        )

        return group_state["managedBy"]

    @staticmethod
    def deallocate_vms(logging_path: str, subscriptions: list, include_managed:bool, deallocate_running:bool):
        stats = {
            "total" : 0,
            "running" : 0
        }

        for subid in subscriptions:
            start = perf_counter()
            computes = ComputeUtil.get_compute(subid, include_managed)
            stop = perf_counter()

            print("Took {} to get {}".format(
                stop-start,
                len(computes)
            ))

            report = ComputeUtil.parse_compute_to_report(computes)
            stats["total"] += report["overall"]["total"]
            stats["running"] += report["states"]["running"]

            file_name = os.path.join(logging_path, "{}.txt".format(subid))
            with open(file_name, "w") as output_file:
                output_file.writelines(json.dumps(report, indent=4))

            # If it has a powerState then it was included managed or not. Check
            # shutdown flag and if set, turn it off (deallocated)
            if deallocate_running:
                running_vms = ComputeUtil.get_running_compute(computes)
                for rvm in running_vms:
                    # Check for CoreEng special flag
                    tags = getattr(rvm, "tags", None)
                    if not tags or "coreeng" not in tags:
                        rvm.deallocate()

        return stats
         