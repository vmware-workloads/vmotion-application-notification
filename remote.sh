#! /bin/bash

echo "##########################################"
echo "# VMNOTIFICATION INSTALL                 #"
echo "##########################################"
echo ""
FILENAME="vmnotification.tar.gz"
URL="https://api.github.com/repos/vmware-workloads/vmotion-application-notification/releases/latest"

# Download File
echo "Downloading the latest release from $URL"
curl -s "$URL" | awk -F\" '/browser_download_url.*.tar.gz/{system("curl -OL " $(NF-1))}'
echo ""

# Extract
echo "Extracting $FILENAME"
tar -xzvf "$FILENAME"
echo ""

# Get folder
echo "Setting folder path"
FOLDER=$(ls | grep "vmnotification-" | sort -V | tail -n 1)
echo "Folder is: '$FOLDER'"
echo ""

# Changing into folder
pushd "$FOLDER"
echo "Calling install.sh"
sudo bash "./install.sh"
popd
echo ""

echo "##########################################"
echo "# VMNOTIFICATION INSTALL COMPLETE        #"
echo "##########################################"