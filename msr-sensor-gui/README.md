# Molten Salt Reactor Sensor - Graphical Interface v1

## Currently includes:


### Projector pattern creator

Allows the user to set a dot pattern according to the following parameters:

- Array of trajectories, with a feature to select start and end points in the graph
- Number of measurements
- Dot diameter
- Exposure time

NOTE: In order to set the pattern in the dmd projector, drivers need to be installed

- Download Zadig (http://zadig.akeo.ie/)
- Connect the projector
- Go to 'Options' -> 'List All Devices'
- Look for 'DLCP900 (Interface 0)
- Replace WinUSB driver with libusb-win32 driver
- _NOTE: TI GUI will stop working once you replace the driver. If you want to restore the WinUSB driver, go to Device Manager, search for the libusb-win32 driver, uninstall and check 'Delete the driver software for this device'_

| Set trajectories | Preview |
| --- | --- |
| ![Projector Pattern Creator](https://github.com/byutemplab/msr-sensor/blob/main/msr-sensor-gui/src/screenshots/Screenshot_1.png?raw=true) | ![Projector Pattern Creator](https://github.com/byutemplab/msr-sensor/blob/main/msr-sensor-gui/src/screenshots/Screenshot_2.png?raw=true) |
