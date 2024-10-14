#! /bin/bash

echo "##########################################"
echo "# VMNOTIFICATION INSTALL                 #"
echo "##########################################"
echo ""

FILENAME=vmnotification
URL="https://api.github.com/repos/vmware-workloads/vmotion-application-notification/releases/latest"


# Get Latest Release
printf "Getting latest release info from $URL..."
browser_url=$(curl -s "$URL" | awk '/browser_download_url/{print $2}' | cut -d '"' -f2)

if [[ $(echo $?) -eq 0 ]]
        then echo "Done"
else
        echo "ERROR"
        echo
        echo "Ensure curl, awk and cut are installed and you have a stable connection to $URL"
        echo "Aborting"
        exit
fi

# Download and extract
printf "Download & extract $FILENAME..."
directory=$(curl -sL $browser_url | tar zxv |grep -o $FILENAME*| sort -u)
echo $directory
echo "OK"

# Run the installer
pushd "$directory" > /dev/null
printf "\nCalling install.sh... You may need to authenticate\n"
sudo bash "./install.sh"

if [[ $(echo $?) -eq 0 ]]
        then echo "Done"
else
        echo "Error Installing $FILENAME ... Aborting"
        exit
fi


popd > /dev/null
echo

echo "##########################################"
echo "# VMNOTIFICATION INSTALL COMPLETE        #"
echo "##########################################"
