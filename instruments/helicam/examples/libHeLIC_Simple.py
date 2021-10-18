#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        libHeLIC_Simple
# Purpose:     Simple example with program sequence to use heliCam and Xenax motor.
#              With graphical output
#
# Last update: 23.06.2015 sm
# Copyright:   (c) Heliotis 2015
#
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python
from __future__ import division,print_function

import socket
import time
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import os, sys

if sys.platform == "win32":
    from msvcrt import getch
else: # linux
    from getch import getch

# add path from libHeLIC wrapper
try:
    if sys.platform == "win32":
        prgPath=os.environ["PROGRAMFILES"]
        sys.path.insert(0,prgPath+r'\Heliotis\heliCam\Python\wrapper')
    else: # "linux"
        sys.path.insert(0,r'/usr/share/libhelic/python/wrapper')
except BaseException  as err:
    print('Path Error'+str(err))

# import libHeLIC wrapper
try:
  from libHeLIC import *
except ImportError as exc:
  print ('-'*30)
  print("Error: failed to import libHeLIC module ({})".format(exc))
  print("Pleas check if the path to Python wrapper correct.")
  print("(libHeLIC_Simple.py Line 27)")
  print ('-'*30)
  print("Press a key to exit...")
  getch()
  sys.exit()

  
# ##############################################################################
# define default parameters
# ##############################################################################
# ToDo: define motor parameter and measurement position!!
IP = '192.168.2.100'
Port = 10001
ticksPerMM = 1000
startPositionMM = 89.2
endPositionMM = 91.7
tguPositionMM = 89.7
tgdPositionMM = 0.0
driveSpeed = 10.0
measurementSpeed = 5.0

# camera settings for minimize Energy
SensNavM2 = 2
cameraSettings = (
('SensNavM2',SensNavM2),
('SensTqp',539),
('SensNFrames',500),
('BSEnable',1),
('DdsGain',1),
('CamMode',7),
('TrigFreeExtN',0),
('AcqStop',0)
);

# calculate frame thickness
Lambda = 650 # default wavelength 650nm
frameThickness = 0.5 * (2 * SensNavM2 + 3) * Lambda * 0.000001;
    
# define functions used for xenax    
def sendCmd(sock,cmd):
  sock.sendall(cmd+'\r')
  echo = sock.recv(255) # wait for receiving acknowledge
  return((((repr(echo))[1:-1]).split('\\r\\n'))[:-1])

def goToPos(sock, ticksPerMM, positionMM):
  posTarget = int(positionMM * ticksPerMM)
  sendCmd(sock, 'g'+str(posTarget))
  return()
    
def goToPosWait(sock, ticksPerMM, positionMM):
  goToPos(sock, ticksPerMM, positionMM)
  pos = int(sendCmd(sock,'tp')[1]) / ticksPerMM
  while (abs(positionMM-pos)>0.01):
    time.sleep(0.05)
    pos = int(sendCmd(sock,'tp')[1]) / ticksPerMM
  return()

def setTrigger(sock, ticksPerMM, tguPositionMM, tgdPositionMM):
  posTGU = int(tguPositionMM * ticksPerMM)
  posTGD = int(tgdPositionMM * ticksPerMM)
  sendCmd(sock, 'tgu'+str(posTGU))
  sendCmd(sock, 'tgd'+str(posTGD))
  return()

def setSpeed(sock, ticksPerMM, speedMM_S):
  speed = int(speedMM_S * ticksPerMM)
  sendCmd(sock, 'sp'+str(speed))
  return()

def initXenax(IP, Port):
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # open/create a socket (streaming/tcp mode)
  sock.connect((IP, Port)) # connect the socket to Jenny Controller
  sendCmd(sock, 'evt0') # event mode (0:disabled, 1:enabled)
  sendCmd(sock,'ref')
  time.sleep(1.5)
  inMotion=True
  while inMotion:
    time.sleep(0.1)
    status = int(sendCmd(sock,'ts')[1])
    if status != 2:
      inMotion=False
  return(sock)
  
def sequence_simple():
  # initialize motor 
  zAxis = initXenax(IP, Port)
  
  # go to start position
  setSpeed(zAxis, ticksPerMM, driveSpeed)
  goToPosWait(zAxis, ticksPerMM, startPositionMM)
  setTrigger(zAxis, ticksPerMM, tguPositionMM, tgdPositionMM)

  # initialize and open camera
  heSys=LibHeLIC()
  heSys.Open(0,sys='c3cam_sl70') # open camera type SL70 (default)
  heSys.AllocCamData(1,LibHeLIC.CamDataFmt['DF_A16Z16'],0,0,0); # allocate memory for minimize energy mode
  heSys.SetTimeout(2000) # set timeout to 2000ms
  
  # set default camera parameters
  for k,v in cameraSettings:
    try:
      setattr(heSys.map,k,v)
    except RuntimeError:
      print('Could not set map property %s to %s',k,v)
  
  # turn on light
  setattr(heSys.map,'OutEnDrv',1)
  
  # clear buffer
  res = 1
  while (res > 0):
    res = heSys.Acquire()
  
  # ready for measurement
  for x in range(0, 3):
    print("measurement loop no. " + str(x))
    # set measurement speed and drive to the end position
    setSpeed(zAxis, ticksPerMM, measurementSpeed)
    goToPos(zAxis, ticksPerMM, endPositionMM)
    
    # acquire new camera data
    res = heSys.Acquire()
    
    # process camera data
    cd=heSys.ProcessCamData(1,0,0)
    img=heSys.GetCamData(1,0,0)
    data=img.contents.data
    data=LibHeLIC.Ptr2Arr(data,(292,280,2),ct.c_ushort) # convert data for python
    surface=data[:,:,0]/32. * frameThickness
    amplitude=data[:,:,1]/16.
    
    # drive back to start position
    setSpeed(zAxis, ticksPerMM, driveSpeed)
    goToPosWait(zAxis, ticksPerMM, startPositionMM)
    
    if x==0:
      plt.ion()
      plt.subplot(1,2,1)
      surfHandle = plt.imshow(surface)
      plt.colorbar()
      plt.subplot(1,2,2)
      amplHandle = plt.imshow(amplitude)
      plt.colorbar()
      plt.draw()
      time.sleep(0.5)
    else:
      surfHandle.set_array(surface)
      amplHandle.set_array(amplitude)
      plt.draw()
      time.sleep(0.5)

  setattr(heSys.map,'OutEnDrv',0)
  heSys.Close()
  zAxis.close()
  print("Press a key to exit...")
  getch()
  plt.close()

if __name__ == '__main__':
  print("motor configuration from line 48")
  print("")
  print("IP: " + IP)
  print("Port: " + str(Port))
  print("Ticks per mm: " + str(ticksPerMM))
  print("Start position in mm: " + str(startPositionMM))
  print("End position in mm: " + str(endPositionMM))
  print("tgu position in mm: " + str(tguPositionMM))  
  print("tgd position in mm: " + str(tgdPositionMM))
  print("drive speed in mm/s: " + str(driveSpeed))
  print("measurement speed in mm/s: " + str(measurementSpeed))
  print("")
  print("If this true?")
  print("y: start measurement, else: exit script")
  
  if getch() == 'y':
    sequence_simple()
  pass

