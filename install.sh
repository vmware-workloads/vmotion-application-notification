#! /bin/bash

if [[ "$EUID" -ne 0 ]]; then
    echo "Please re-run using sudo or as root"
    exit 1
fi

echo "Creating folders"
vmnotification_folders=( \
  "/opt/vmnotification"  \
  "/etc/vmnotification"  \
)
for item in ${vmnotification_folders[@]}; do
  echo " Creating folder '$item'"
  mkdir -p $item
done


echo "Copying files to '/opt/vmnotification'"
vmnotification_files=(          \
  "LICENSE"                     \
  "Pipfile"                     \
  "Pipfile.lock"                \
  "README.md"                   \
  "utils.py"                    \
  "vmnotification.py"           \
  "vmnotification_config.py"    \
  "vmnotification_exception.py" \
  "vmnotification_service.py"   \
)
for item in ${vmnotification_files[@]}; do
  echo " Copying file '$item'"
  cp $item /opt/vmnotification
done

echo "Setting file execute permission on '/opt/vmnotification/vmnotification.py'"
chmod a+x /opt/vmnotification/vmnotification.py

echo "Copying 'vmnotification' file to '/etc/default/'"
cp ./vmnotification /etc/default/

echo "Copying service configuration file to '/etc/vmnotification/'"
cp ./vmnotification.conf* /etc/vmnotification/

echo "Copying systemd service to '/etc/systemd/system'"
cp ./vmnotification.service /etc/systemd/system/

echo "Enabling and starting 'vmnotification.service'"
systemctl daemon-reload
systemctl enable vmnotification.service
systemctl restart vmnotification.service

echo ""
echo "MAKE SURE TO EDIT THE CONFIGURATION AND RESTART THE SERVICE!"
echo "'sudo vi /etc/vmnotification/vmnotification.conf; sudo systemctl restart vmnotification'"
echo ""