#!/bin/bash

# change directory into the data_acquisition_start_scan folder
cd /home/intuitiverobots/Documents/raspberrypi/data_acquisition_start_scan

# install the virtual environment
python3 -m venv data_acquisition_start_scan_env
source data_acquisition_start_scan_env/bin/activate
python3 -m pip install --upgrade bosdyn-client bosdyn-mission bosdyn-choreography-client bosdyn-orbit

# self delete
rm -- "$0"
