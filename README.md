# vmotion-application-notification 

Since its introduction in 2003, vMotion has been one of the most transformative inventions in the Virtualization and Cloud technologies space. It is inarguably one of the most important features of the VMware vSphere platform. At a high level, vMotion (also sometimes referred to as "Live Migration") enables the movement or relocation a virtualized workload from one Host to another while the application hosted by the Virtual Machine continues to run and provide services.

As virtualization and "The Cloud" become prevalent and more core and latency-sensitive applications began to move from physical incarnations to the vSphere platform, some Administrators became concerned that the brief interruption which happens during the "switch-over" phase of a vMotion operation can negatively interfere with these latency-sensitive applications. The Administrators usually opt to disable vMotion for such workloads.

In vSphere 8.0, VMware introduced an enhancement to vSphere vMotion. This enhancement, called vMotion Application Notification gives an Application Owner or Administrator complete control and flexibility in preparing their applications for a vMotion operation.

vMotion Application Notification operates by sending a notification to a Virtual Machine when a vMotion operation is initiated on that VM. Unlike in the past where a vMotion operation is immediately executed upon invocation, an VM Administrator or Application Owner (working in tandem with the Vi Administration) can now delay a vMotion request for a period long enough to allow them to gracefully prepare the VM and its application for such operation without negatively impacting the services provided by the VM and its application.

The Scripts provided herein are intended to serve as starting samples to demonstrate how to:
Enable vMotion Application Notification on ESXi Hosts
Enable vMotion Application Notification on a VM
Configure the VM to register itself to receive notification when a vMotion operation is invoked on it
Configure the VM to respond to such notifications
Configure the VM to performed administratively-configured pre-vMotion preparation tasks
Configure the VM to inform vMotion Application Notification when the configured Administrative pre-tasks are completed so that the vMotion operation can proceed
Configure the VM to receive notifications of vMotion completion
Configure the VM to perform administratively-preconfigured post-vMotion tasks to re-introduce the hosted application back into service.

Although the examples included in here use a Cockroach DB as the sample workload, the solution presented applies to any Linux-based workloads which requires the improved high-availability capabilities provided by vMotion Application Notification

Note: These Scripts are provided without any implied warranty and are intended only to serve as a starting point for further investigation and improvement by the general public. Although we encourage and welcome your feedback, please be aware that VMware does not offer or provide any support for the use of these scripts.

## Authors
* Charles Lee
* Dharmesh Bhatt
* Deji Akomolafe


## Requirements
* Linux OS using systemd
* Python 3.10


## Installation

### Curl
1. Run the following command on the target system command line.
```bash
# Download and run the installation script to install the latest release.
curl -L https://raw.githubusercontent.com/vmware-workloads/vmotion-application-notification/main/remote.sh | bash
```

### Git Clone
1. Configure the hosts and VM using this article. The scripts are included in the **tools** folder.
https://core.vmware.com/blog/how-enable-and-configure-new-vmotion-application-notification-feature-vm


2. Download and install the files.
```
git clone https://github.com/vmware-workloads/vmotion-application-notification.git
cd ./vmotion-application-notification
chmod a+x install.sh vmnotification.py
sudo ./install.sh
```
<br>

3. Configure the service by editing the vmnotification.conf file.
```ini
# /etc/vmnotification/vmnotification.conf

[DEFAULT]
# Name of the application registered for notifications
app_name = my_app                                      # <<< ---- SET THIS TO YOUR APPLICATION NAME

# Interval in seconds that we check for a notification from the host.
# The default is every 1 second.
check_interval_seconds = 1                             # <<< ---- DEFAULT SHOULD BE FINE

# Command executed to prepare the application for a vMotion.
pre_vmotion_cmd = ping -c 20 8.8.8.8                   # <<< ---- SET THIS TO THE PRE VMOTION COMMAND

# Command executed to resume the application after a vMotion.
post_vmotion_cmd = ping -c 10 8.8.8.8                  # <<< ---- SET THIS TO THE POST VMOTION COMMAND

#
# THE STUFF BELOW SHOULD NOT BE CHANGED UNLESS YOU ARE SOLVING A SPECIFIC ISSUE  
#
[Token]
# Create a token file on a successful registration.
# - If disabled (no), if the service crashes and the token is still registered, the VM will need to number
#   rebooted to clear the existing registration.token_file
# - If enabled (yes), the token is saved to a file upon successful registration. When the program starts we
#   check to see if a token file exists, and try to unregister it. This eliminates the need to reboot if the
#   application terminates uncleanly.
token_file_create = no

# Obfuscate the token in the logfile.
# - If disabled (no), the token is written in the log files.
# - If enabled (yes), we obfuscate the token in the log files.
token_obfuscate_logfile = yes

[Logging]
# Log files
service_logfile_ = /var/log/vmnotification/vmnotification.log
vmotion_logfile = /var/log/vmnotification/vmotion.log
timeout_logfile = /var/log/vmnotification/timeout.log

# Logging verbosity in the service log file
service_logfile_level  = DEBUG

# Logging verbosity in the service console
service_console_level  = WARNING

# Maximum size of the log file in Bytes
service_logfile_maxsize_bytes = 10485760
vmotion_logfile_maxsize_bytes = 10485760
timeout_logfile_maxsize_bytes = 10485760

# Number of log files to keep (.log, .log.1, .log.2, ...). Once this number of log files is reached, the oldest
# file is deleted.
service_logfile_count = 10
vmotion_logfile_count = 3
timeout_logfile_count = 3
```
<br>

4. Restart the service.
```
sudo systemctl restart vmnotification.service
```

## Files and Paths

#### vmnotification.py
* description: Service launcher.
* path: /opt/vmnotification/vmnotification.py

#### vmnotification.service
* description: The systemd service file.
* path: /etc/systemd/system/vmnotification.service

#### vmnotification
* description: The systemd service options file.
* path: /etc/default/vmnotification

#### vmnotification.conf
* description: Service configuration. This file contains the command and options for the service.
* path: /etc/vmnotification/vmnotification.conf
* should edit?: **YES**

#### vmnotification.log
* description: Service log file.
* path: /var/log/vmnotification/vmnotification.log

#### token_file
* description: This file stores the unique notification event token when the service is launched. On a normal service shutdown, this file is deleted. If the service terminates unexpectedly and the file exists, on restart the service will read this file and attempt to unregister the token.
* path: /var/run/vmotion_notifier/token_file
