#!/bin/bash

# scanner api
lxterminal --title="Scanner API" --command="bash -c 'cd /home/intuitiverobots/Documents/raspberrypi/scanner_api && source scanner_api_env/bin/activate && python3 main.py'"

# data acquisition start scan
lxterminal --title="Data Acquisition Start Scan" --command="bash -c 'cd /home/intuitiverobots/Documents/raspberrypi/data_acquisition_start_scan && source data_acquisition_start_scan_env/bin/activate && python3 main.py'"
