# Parallel Spatial Domain Thermoreflectance Sensor - GUI v1

Current features:
- Control the DMD rgb and laser projectors, the waveform generator, the helicam lock-in camera, and the CMOS camera
- Analyze input data from the lock-in camera
- Pre-process electron microscope images to find grain boundaries

Complete user manual [here](/resources/user-guide-v1.1.pdf)

| Set trajectories in projectors | Set waveform generator settings |
| --- | --- |
| ![projectors-tab](/resources/dmd-projector-v2.gif) | ![signal-generator-tab](/resources/signal-generator-v1.gif) |

#### Installation instructions
##### Python requirements:
- Run `pip install -r requirements.txt` inside the src folder
##### Projector driver:
- Download Zadig (http://zadig.akeo.ie/)
- Connect the projector
- Go to 'Options' -> 'List All Devices'
- Look for 'DLCP900 (Interface 0)
- Replace WinUSB driver with libusb-win32 driver
- _NOTE: TI GUI will stop working once you replace the driver. If you want to restore the WinUSB driver, go to Device Manager, search for the libusb-win32 driver, uninstall and check 'Delete the driver software for this device'_
##### Helicam sdk:
- Download and install the sdk from (https://github.com/byutemplab/helicam-sdk)
##### CMOS Camera driver:
