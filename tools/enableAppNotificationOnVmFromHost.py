#!/usr/bin/env python3
from pyVim.connect import SmartConnect
from pyVmomi import vim, VmomiSupport
from pyVim.task import WaitForTask
import sys

num_args = len(sys.argv) - 1

if num_args == 0 or num_args > 2:
    print("Usage: python enableAppNotificationOnVM.py vm_name [timeout=<value in seconds>]")
    exit(1)

vm_name = sys.argv[1]

si = SmartConnect(host='localhost', user='root')
container = si.content.viewManager.CreateContainerView(si.content.rootFolder, [vim.VirtualMachine], True)

for vm in container.view:
    if vm.name == vm_name:
        task = vm.Reconfigure(vim.vm.ConfigSpec(vmOpNotificationToAppEnabled=True))
        WaitForTask(task)
        if vm.config.vmOpNotificationToAppEnabled:
            print(f"vMotion App Notification is now enabled on {vm_name}.")
        else:
            print(f"Could not enable vMotion App Notification on {vm_name}.")
            exit(1)
        break
else:
    print(f"No VM with name {vm_name} was found.")
    exit(1)

if num_args == 2:
    if sys.argv[2].startswith("timeout="):
        try:
            timeout = int(sys.argv[2][8:])
        except ValueError:
            print("Invalid timeout value. Must be an integer.")
            exit(1)
        task = vm.Reconfigure(vim.vm.ConfigSpec(vmOpNotificationTimeout=timeout))
        WaitForTask(task)
        if vm.config.vmOpNotificationTimeout == timeout:
            print(f"vMotion App Notification Timeout set to {timeout} seconds.")
        else:
            print(f"Could not enable vMotion App Notification Timeout on {vm_name}.")
            exit(1)
    else:
        print("Invalid vMotion App Notification Timeout value specified.")
        exit(1)
