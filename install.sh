#! /bin/bash


cp ./vmnotification /etc/default/

mkdir -p /etc/vmnotification
cp ./vmnotification.conf* /etc/vmnotification/

cp ./vmnotification.service /etc/systemd/system/
systemctl enable vmnotification.service
systemctl start vmnotification.service