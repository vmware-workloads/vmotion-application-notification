#! /bin/env python
from pyVim.connect import SmartConnect
from pyVmomi import vim, VmomiSupport
from pyVim.task import WaitForTask
import sys

num_args = len(sys.argv) - 1

if num_args == 0 or num_args > 2:
    print("Usage: python enableAppNotificationOnVM.py vm_name [timeout=<value in seconds>]")
    exit()

vm_name = sys.argv[1]

si = SmartConnect(host='localhost', user='root')
container = si.content.viewManager.CreateContainerView(si.content.rootFolder, [vim.VirtualMachine], True)

for vm in container.view:
    if vm.name == vm_name:
        task = vm.Reconfigure(vim.vm.ConfigSpec(vmOpNotificationToAppEnabled=True))
        WaitForTask(task)
        if vm.config.vmOpNotificationToAppEnabled:
            print("vMotion App Notification is now enabled on %s." % vm_name)
        else:
            print("Could not enable vMotion App Notification on %s." % vm_name)
            exit()
        break
else:
    print("No VM with name %s was found." % vm_name)
    exit()

if num_args == 2:
    if sys.argv[2].startswith("timeout="):
        timeout = int(sys.argv[2][8:])
        task = vm.Reconfigure(vim.vm.ConfigSpec(vmOpNotificationTimeout=timeout))
        WaitForTask(task)
        if vm.config.vmOpNotificationTimeout == timeout:
            print("vMotion App Notification Timeout set to %d seconds." % timeout)
        else:
            print("Could not enable vMotion App Notification Timeout on %s.")
            exit()
    else:
        print("Invalid vMotion App Notification Timeout value specified.")
