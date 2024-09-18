#! /bin/bash

echo "##########################################"
echo "# VMNOTIFICATION INSTALL                 #"
echo "##########################################"
echo

FILENAME='vmnotification-v'
URL="https://api.github.com/repos/vmware-workloads/vmotion-application-notification/releases/latest"

browser_url=$(curl -s "$URL" | grep browser_download_url)
[[ $(echo $?) -eq 0 ]] && echo \>\>Obtained URL || echo "error obtaining URL"

#directory=$(echo $browser_url | awk '{print $NF}' | xargs curl -sL | tar zxv 2> >(grep -o vmnotif*) | sort -u)
echo $browser_url | awk '{print $NF}' | xargs curl -sL | tar zxv


pushd "$directory"
echo "Calling install.sh"
sudo bash "./install.sh"
popd
echo

echo "##########################################"
echo "# VMNOTIFICATION INSTALL COMPLETE        #"
echo "##########################################"
