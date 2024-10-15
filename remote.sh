#! /bin/bash

echo -e "\033[33m╔════════════════════════════════════════╗\033[0m"
echo -e "\033[33m║                                        ║\033[0m"
echo -e "\033[33m║     \033[34m  VMNOTIFICATION INSTALLER  \033[33m       ║\033[0m"
echo -e "\033[33m║                                        ║\033[0m"
echo -e "\033[33m╚════════════════════════════════════════╝\033[0m"


FILENAME=vmnotification
URL="https://api.github.com/repos/vmware-workloads/vmotion-application-notification/releases/latest"

# Check for awk and curl

for cmd in awk curl; do
	if ! command -v $cmd &>/dev/null; then
        	echo -e "\033[0;31m[✘]\033[0m $cmd is not installed."
          	exit 1
        fi
done


# Check URL resolves

if ! curl --output /dev/null --silent --head --fail "$URL"; then
  echo -e "\033[0;31m[✘]\033[0m Can't Resolve $URL"
  exit 1
fi


# Get Latest Release

printf "Getting latest release info from \033[40m$URL\033[0m..."
browser_url=$(curl -s "$URL" | awk -F'"' '/"browser_download_url"/ {print $(NF-1)}')

if [[ $(echo $?) -eq 0 ]]
        then echo -e "\033[32mDone\033[0m"
else
        echo -e "\033[0;31mERROR\033[0m"
        echo
        echo "Ensure you have a stable connection to $URL"
        echo "Aborting"
        exit
fi


# Download and extract

printf "Download & extract $FILENAME..."
directory=$(curl -sL $browser_url | tar zxv 2>/dev/null |grep -o $FILENAME*| sort -u)
echo -e "\033[32mOK\033[0m"


# Run the installer

pushd "$directory" > /dev/null
printf "\nCalling install.sh... \033[0;33mYou may need to authenticate\033[0m\n\n"
sudo bash "./install.sh"

if [[ $(echo $?) -eq 0 ]]
        then echo -e "\033[32mDone\033[0m"
else
        echo -e "\033[0;31mError Installing $FILENAME ... Aborting\033[0m"
        exit
fi


popd > /dev/null
echo
echo -e "\033[33m╔════════════════════════════════════════╗\033[0m"
echo -e "\033[33m║                                        ║\033[0m"
echo -e "\033[33m║  \033[32m  VMNOTIFICATION INSTALL COMPLETE  \033[33m   ║\033[0m"
echo -e "\033[33m║                                        ║\033[0m"
echo -e "\033[33m╚════════════════════════════════════════╝\033[0m"
