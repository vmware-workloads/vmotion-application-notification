# systemd-vmotion-notification

This project implements a simple systemd service that provides a method to automatically run predetermined commands before and after a vSphere vMotion event. 

Running commands before and after a vMotion is beneficial because it allows a given application owner the ability to proactively set their application in a paused state that will ensure the


## Requirements
* systemd based Linux OS
* Python 3.10

## Installation
### Git Clone
1. Download and install the files.
```
cd /opt
git clone https://github.coml/vmware-workloads/vmnotification.git
cd 
chmod a+x install.sh vmnotification.py
sudo ./install.sh
```
<br>

2. Configure the service by editing the vmnotification.conf file.
```ini
# /etc/vmnotification/vmnotification.conf

[DEFAULT]
# Name of the application registered for notifications
app_name = my_app

# Interval in seconds that we check for a notification from the host. Do no change unless you 
# know what you are doing.
check_interval_seconds = 1

# Command executed to prepare the application for a vMotion.
pre_vmotion_cmd = echo "I am about to be migrated!"  # <<< ---- SET THIS TO THE PRE VMOTION COMMAND

# Command executed to resume the application after a vMotion.
post_vmotion_cmd = echo "Migration is complete!"     # <<< ---- SET THIS TO THE POST VMOTION COMMAND

# File where the notification token is stored
token_file = /var/run/vmotion_notifier/token_file


[Logging]
# Log file
logfile = /var/log/vmnotification/vmnotification.log

# Logging verbosity in the log file
log_level = DEBUG

# Logging verbosity in the console
console_level = WARNING

# Maximum size of the log file in Bytes
logfile_maxsize_bytes = 10485760 # 10MB

# Number of log files to keep (.log, .log.1, .log.2, ...). Once this number of log files is reached, the oldest
# file is deleted.
logfile_count = 10
```
<br>

3. Restart the service.
```
sudo systemctl restart vmnotification.service
```

## Files and Paths

#### vmnotification.py
* description: Service launcher.
* installation path: /opt/vmnotification/vmnotification.py

#### vmnotification.service
* description: The systemd service file.
* installation path: /etc/systemd/system/vmnotification.service

#### vmnotification
* description: The systemd service options file.
* installation path: /etc/default/vmnotification

#### vmnotification.conf
* description: Service configuration. This file contains the command and options for the service.
* installation path: /etc/vmnotification/vmnotification.conf
* should edit?: **YES**

#### token_file
* description: This file stores the unique notification event token when the service is launched. On a normal service shutdown, this file is deleted. If the service terminates unexpectedly and the file exists, on restart the service will read this file and attempt to unregister the token.
