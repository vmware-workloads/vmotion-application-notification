#! /bin/bash

echo "##########################################"
echo "# VMNOTIFICATION INSTALL                 #"
echo "##########################################"
echo ""

FILENAME=vmnotification
URL="https://api.github.com/repos/vmware-workloads/vmotion-application-notification/releases/latest"


# Get Latest Release
printf "Getting latest release info from $URL..."
browser_url=$(curl -s "$URL" | grep browser_download_url)

if [[ $(echo $?) -eq 0 ]]
	then echo "Done"
else 
    	echo "ERROR"
    	echo
    	echo "Ensure curl is installed and you have a stable connection to $URL"
    	echo "Aborting"
    	exit	
fi    	

# Download and extract
printf "Download & extract $FILENAME..."
directory=$(awk '{print $NF}' <<< $browser_url | xargs curl -sL | tar zxv 2> >(grep -o $FILENAME*)| sort -u)
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


fi 	
popd > /dev/null 
echo

echo "##########################################"
echo "# VMNOTIFICATION INSTALL COMPLETE        #"
echo "##########################################"
