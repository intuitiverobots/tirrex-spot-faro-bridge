
<div align="center">
  <img src="assets/tirrex.png" alt="Tirrex" width="200"
       style="vertical-align: middle; margin: 0 12px;">
  <img src="assets/logo_france2030.png" alt="France 2030" width="150"
       style="vertical-align: middle; margin: 0 12px;">
  <img src="assets/LOGO_CNRS_BLEU.png" alt="CNRS" width="150"
       style="vertical-align: middle; margin: 0 12px;">
  <img src="assets/LOGO_HORIZONTAL_TR_BLACK.png" alt="CNRS" width="150"
       style="vertical-align: middle; margin: 0 12px;">
</div>

# Tirrex FARO Scanner Bridge



This project is a bridge between Boston Dynamics' Spot robot and FARO scanners. This open-source project enables Spot to control FARO scanning devices, automating data capture and enhancing mobility for 3D scanning applications.


## Context

Tirrex is a project funded under an agreement between the Agence Nationale de la Recherche [ANR] and the Centre Nationale de la Recherche Scientifique [CNRS], the coordinating institution of a consortium, as part of the 'France 2030' program.

**Project Reference:** [ANR France 2030 - ProjetIA-21-ESRE-0015](https://anr.fr/ProjetIA-21-ESRE-0015) - CNRS/ANR Convention

## Hardware Components

- Spot robot
- FARO Scanner
- Compute platform (Raspberry Pi, Core I/O)
- Windows computer (for format conversion)
- Tablet controller

## Quick Start

### Raspberry Pi Setup

Follow the instructions in the [raspberrypi/README.md](raspberrypi/README.md)

### Boston Dynamics Spot

1. Install the [GXP](https://support.bostondynamics.com/s/article/Spot-General-Expansion-Payload-GXP-72066) on the robot's back
2. Connect the compute platform via ethernet cable and power cable (auto-starts on boot)
3. Power on the robot

### FARO Scanner

1. Securely mount the scanner on the robot's back
2. Power on the scanner

### Windows Computer

Follow the instructions in the [converter_api/README.md](converter_api/README.md)

### Start a Scan

Using the tablet controller:

1. Start the android application and connect to the robot
2. Click the red cross (bottom right corner)
3. Select the `start-scan` action
4. Click `start` button
5. Scanning begins automatically


# Scan Data Flow

1. **Initiation:** Tablet triggers `StartScan.start_scan()` via the Spot app
2. **Configuration:** Scanner API reads settings and initializes the FARO Scanner
3. **Acquisition:** FARO Scanner streams data in FLS format to the converter API
4. **Conversion:** Converter API transforms FLS data to LAS format in real-time
5. **Distribution:** Converted LAS data is returned to scanner API and streamed to visualization clients (e.g., Unity)

## ***Coming Soon***

### Core I/O Support

This software is currently designed to run on a Raspberry Pi but will be compatible with the [Spot Core I/O](https://support.bostondynamics.com/s/article/About-Core-I-O), the Spot embedded compute platform, in future releases.
