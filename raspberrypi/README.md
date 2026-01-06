# Equipments

- Raspberry Pi
- SD card

# Pre-installation
*On a computer*

- format the SD card thanks to the [Raspberry Pi Imager](https://www.raspberrypi.com/software/) to the appropriate version of your Raspberry Pi
    - **id** intuitiverobots
    - **password** password
- copy this project under `rootfs/home/intuitiverobots/Documents`
(for example the path to this `README.md` file will be `rootfs/home/intuitiverobots/Documents/raspberrypi/README.md`)

# Installation
*On the Raspberry Pi*

- connect your Raspberry Pi to Internet
- open a new terminal
- disable the Network Time Protocol `sudo timedatectl set-ntp false`
- set the current date `sudo date --set="YYYY-MM-DD HH:MM:SS"`
- add the execute permission to the `startup.sh` file `chmod +x /home/intuitiverobots/Documents/raspberrypi/startup/startup.sh`
- start the installation `sudo /home/intuitiverobots/Documents/raspberrypi/startup/startup.sh`


# Start the application

You have nothing to do yourself. Once the startup has been completed, both the `scanner_api` and `data_acquisition_start_scan` will automatically launch at the Raspberry Pi's boot.
