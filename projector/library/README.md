# Pycrafter 6500

Pycrafter 6500 is a native Python controller for Texas Instruments' dlplcr6500evm evaluation module for DLP displays.
Initial contribution by csi-dcsc (repo: https://github.com/csi-dcsc/Pycrafter6500), edits and extra features by Santiago Gomez Paz.

Compatible with Python 2 and Python 3. Tested in Windows 10.

## Required modules:

- Pyusb
- Numpy
- libusb

## Driver installation:

- Download Zadig (http://zadig.akeo.ie/)
- Connect the projector
- Go to 'Options' -> 'List All Devices'
- Look for 'DLCP900 (Interface 0)
- Replace WinUSB driver with libusb-win32 driver
- _NOTE: TI GUI will stop working once you replace the driver. If you want to restore the WinUSB driver, go to Device Manager, search for the libusb-win32 driver, uninstall and check 'Delete the driver software for this device'_

## Features list:

- Basic control of the evaluation module (modes selection, idle toggle, start/pause/stop sequences)
- Upload of a sequence of EXCLUSIVELY BINARY images for "patterns on the fly" mode, with independent control of exposure times, dark times, triggers and repetitions number. RGB binary color selection available (pure red, magenta, etc)

## COMMANDS LIST

### To open a connection with the DMD:

import pycrafter6500
controller=pycrafter6500.dmd()

### To set the DMD to idle mode

controller.idle_on()

### To wake the DMD from idle mode

controller.idle_off()

### To set the DMD to standby

controller.standby()

### To wake the DMD from standby

controller.wakeup()

### To reset the DMD

controller.reset()

### To change the DMD operating mode:

controller.changemode(mode)

##### Available modes:

- mode=0 for normal video mode
- mode=1 for pre stored pattern mode
- mode=2 for video pattern mode
- mode=3 for pattern on the fly mode

### To start, pause or stop a sequence

controller.startsequence()
controller.pausesequence()
controller.stopsequence()

### To define a sequence for pattern on the fly mode

controller.defsequence(images, color, exposures, trigger in, dark time, trigger out, repetitions)

##### Inputs are:

- images: python list of numpy arrays, with size (1080,1920), dtype uint8, and filled with binary values (1 and 0 only)
- color: string for the RGB color --> options: disabled (off), red, green, yellow, blue, magenta, cyan, white.
- exposures: python list or numpy array with the exposure times in microseconds of each image. Length must be equal to the images list.
- trigger in: python list or numpy array of boolean values determing wheter to wait for an external trigger before exposure. Length must be equal to the images list.
- dark time: python list or numpy array with the dark times in microseconds after each image. Length must be equal to the images list.
- trigger out: python list or numpy array of boolean values determing wheter to emit an external trigger after exposure. Length must be equal to the images list.
- repetitions: number of repetitions of the sequence. set to 0 for infinite loop.
