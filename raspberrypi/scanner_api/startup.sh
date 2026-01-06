#!/bin/bash

# change directory into the scanner_api folder
cd /home/intuitiverobots/Documents/raspberrypi/scanner_api

# install the virtual environment
python3 -m venv scanner_api_env
source scanner_api_env/bin/activate
python3 -m pip install requests "fastapi[standard]"

# self delete
rm -- "$0"
