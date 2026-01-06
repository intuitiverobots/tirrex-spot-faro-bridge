#!/bin/bash

# upgrade apt
apt update && apt upgrade

# scanner_api
cd /home/intuitiverobots/Documents/raspberrypi/scanner_api
chmod +x startup.sh
./startup.sh

# data_acquisition_start_scan
cd /home/intuitiverobots/Documents/raspberrypi/data_acquisition_start_scan
chmod +x startup.sh
./startup.sh

# change directory into the startup folder
cd /home/intuitiverobots/Documents/raspberrypi/startup

# autostart
mkdir -p /home/intuitiverobots/.config/autostart
mv -f scandog.desktop /home/intuitiverobots/.config/autostart/scandog.desktop
chmod +x scandog.sh

# nmcli
nmcli connection delete $(nmcli -t -f UUID connection show)

# ethernet
nmcli con add type ethernet ifname eth0 con-name eth0 ipv4.addresses 192.168.50.100/24 ipv4.method manual

# wifi
nmcli con add type  wifi ifname wlan0 con-name wlan0 ssid "router_spot_network" wifi-sec.key-mgmt wpa-psk wifi-sec.psk "password" ipv4.method auto
nmcli con add type wifi ifname wlan1 con-name wlan1 ssid "LLS082119893" wifi-sec.key-mgmt wpa-psk wifi-sec.psk "0123456789" ipv4.method auto

# config
config="[all]"
# hdmi screen
config="${config}\n# Automatically detect HDMI\nhdmi_force_hotplug=1\nhdmi_group=2\nhdmi_mode=82"
# write config in /boot/firmware/config.txt
echo -e "${config}" >> /boot/firmware/config.txt

# self delete
rm -- "$0"

# reboot the RaspberryPi to apply changes
reboot
