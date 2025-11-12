#!/usr/bin/env python3
from pyVim.connect import SmartConnect
from pyVmomi import vim, VmomiSupport
import sys

if len(sys.argv) == 1:
   hostTimeout = 0
else:
   hostTimeout = sys.argv[1]

si = SmartConnect(host='localhost', user='root')
dc = si.content.rootFolder.childEntity[0]
host = dc.hostFolder.childEntity[0].host[0]
optMgr = host.configManager.advancedOption
optMgr.UpdateValues([vim.OptionValue(key="VmOpNotificationToApp.Timeout",
                                     value=VmomiSupport.vmodlTypes['long'](hostTimeout))])
curHostTimeout = optMgr.QueryView("VmOpNotificationToApp.Timeout")[0].value
print(f"\n Host-level notification timeout: {curHostTimeout} \n")
