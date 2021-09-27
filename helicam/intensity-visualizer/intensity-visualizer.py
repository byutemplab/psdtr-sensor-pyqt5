#-------------------------------------------------------------------------------
# Name:        intensity-isualizer
# Purpose:     graph intensity in a 2d graph
# Author:      Santiago Gomez Paz
# Project:     2021 - TEMP lab
#-------------------------------------------------------------------------------

from __future__ import division, print_function
import numpy as np
import pandas as pd
import os, sys
import ctypes as ct
import time
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Slider
from mpl_toolkits.mplot3d import Axes3D
mpl.use('WxAgg')

# ========= IMPORT libHeLIC wrapper ========= #

if sys.platform == "win32":
    from msvcrt import getch
else: # linux
    from getch import getch

try:
    if sys.platform == "win32":
        prgPath=os.environ["PROGRAMFILES"]
        sys.path.insert(0,prgPath+r'\Heliotis\heliCam\Python\wrapper')
    else: # "linux"
        sys.path.insert(0,r'/usr/share/libhelic/python/wrapper')
except BaseException  as err:
    print('Path Error'+str(err))

try:
    from libHeLIC import *
except ImportError as exc:
    print ('-'*30)
    print("Error: failed to import libHeLIC module ({})".format(exc))
    print("Pleas check if the path to Python wrapper correct.")
    print("(libHeLICTester.py Line 18-25)")
    print("For more details look at the documentation from the heliSDK in python folder.")
    print ('-'*30)
    print("Press a key to exit...")
    getch()
    sys.exit()

# ========= Get registers ========= #

def test1():
  heSys=LibHeLIC()
  print('GetVersion SrCam : ',LibHeLIC.GetVersion())

  heSys.Open(0,sys='c3cam_sl70')
  rd=heSys.GetRegDesc()
  sd=heSys.GetSysDesc()

  print('\n'+20*'-','Registers:',rd.contents.numReg,20*'-')
  for idx in range(rd.contents.numReg):
    r=rd.contents.regs[idx]
    print('{:<3} {:18} {:30} \n'.format(r.num, r.id.decode('windows-1252'), r.cmt.decode('windows-1252')))

  print('\n'+20*'-','Mappings:',rd.contents.numMap,20*'-')
  for idx in range(rd.contents.numMap):
    m=rd.contents.maps[idx]
    print('{:22} {} - lvl:cammode {}:{} \t def:min:max {}:{}:{}'.format(m.id.decode('windows-1252'), m.group.decode('windows-1252'), str(m.level), str(m.level), str(m.defValue), str(m.minValue), str(m.maxValue)))
    print('{:22} {} \n'.format('', m.cmt))
  
  heSys.Close()

# ========= Visualize Intensity ========= #
  
def test2():
  # Init library and open camera
  heSys = LibHeLIC()
  heSys.Open(0, sys='c3cam_sl70')

  # Set parameters
  frames = 50
  settings = (
    ('AcqStop',       1),
    ('CamMode',       3),         # intensity
    ('SensTqp',       69989),     # measure 500 Hz
    ('SensDeltaExp',  0),
    ('SensNavM2',     2),
    ('SensNFrames',   frames),
    ('BSEnable',      1),
    ('DdsGain',       2),
    ('TrigFreeExtN',  1),
    ('InvEncCnt',     0),
    ('FWHMnFrame',    1),
    ('IterMaxFrac',   2),
    ('MinEnergWin',   16),
    ('OffsetMethod',  1),
    ('UseLastFrame',  1),
    ('NFrmAvg',       3),
    ('AcqStop',       0),
  )
  for k, v in settings:
    try:
      setattr(heSys.map, k, v) # heSys.map.k=v
    except RuntimeError:
      error('Could not set map property %s to %s', k, v)

  # Allocate place for data in IQ format
  heSys.AllocCamData(1, LibHeLIC.CamDataFmt['DF_I16Q16'], 0, 0, 0)

  # Get raw data from the camera
  cnt = 0
  res = heSys.Acquire()
  print("Acquire", cnt, "returned", res)

  # Process data
  cd = heSys.ProcessCamData(1, 0, 0)
  print("ProcessCamData", cnt, "returned", cd.contents.data)

  # Get data and put it in an array
  # Array shape: frames * 300 [width] * 300 [height] * 2 [I and Q]
  img = heSys.GetCamData(1, 0, 0)
  data = img.contents.data
  data = LibHeLIC.Ptr2Arr(data, (frames, 300, 300, 2), ct.c_int16)

  # Start by showing frame 0 and I parameter
  frameNum = 0
  IQProperty = 0
  
  # Initialize plot
  plt.ion() # make the plot interactive
  fig = plt.figure()
  ax = fig.add_subplot(111, projection='3d')
  ax.plot_wireframe(300, 300, data[frameNum, :, :, IQProperty])

  # Slider for frames
  ax_slider = plt.axes([0.20, 0.01, 0.65, 0.03])
  slider = Slider(ax_slider, 'Slide ->', 0, 49, valinit=0, valfmt='%d', valstep=1)
  slider.on_changed(selectFrame)

  # Update frame selection
  def selectFrame(val):
    if type(val) is int:
      frameNum = val
    else:
      frameNum = val.astype(int)
    ax.imshow(data[frameNum, :, :, IQProperty])
    fig.canvas.draw_idle()

  # Slider for IQ properties
  ax_slider_2 = plt.axes([0.20, 0.05, 0.65, 0.03])
  slider_2 = Slider(ax_slider_2, 'Slide ->', 0, 1, valinit=0, valfmt='%d', valstep=1)
  slider_2.on_changed(selectIQProperty)

  # Update IQ property selection
  def selectIQProperty(val):
    if type(val) is int:
      IQProperty = val
    else:
      IQProperty = val.astype(int)
    ax.imshow(data[frameNum, :, :, IQProperty])
    fig.canvas.draw_idle()

  # Shut down camera
  heSys.Close()

# ========= List connected cameras ========= #

def test3():
  print ('-'*20)
  heSys=LibHeLIC()
  [count,serials] = LibHeLIC.GetSerials()
  print ('No of installed heliCams: ' + str(count))
  for item in serials:
    print(item)

def testz():
  print ('-'*20)
  print ('Used Python version:')
  print (sys.version)
  print ('-'*20)
  print ('Search libHeLIC in:')
  for ImportPath in sys.path:
      print (ImportPath)
  print ('-'*20)
  print ('Numpy version:')
  print (np.version.version)
  print ('Matplotlib version:')
  print (mpl.__version__)
  print ('libHeLIC version:')
  heSys=LibHeLIC()
  print(str(LibHeLIC.GetVersion()[1][3]) +'.'+ str(LibHeLIC.GetVersion()[1][2])+'.'+ str(LibHeLIC.GetVersion()[1][1])+'.'+ str(LibHeLIC.GetVersion()[1][0]))
  
if __name__ == '__main__':

  def MenuSelection():
    entry=(
      ('1', test1 ,'show registerDescr of sys=c3cam_sl70'),
      ('2', test2 ,'intensity image'),
      ('3', test3 ,'scan connected heliCams and print the serial numbers'),
      ('z', testz ,'print out vesions from python. print out path.'),
    )
    while True:
      print ('-'*20)
      for (key,func,txt) in entry:
        print (key,func.__name__+'()',txt)
      print ('x','','exit')
      c=getch() # using from console
      if c=='x':
        break
      for (key,func,txt) in entry:
        if key==c:
          try:
            func() # run the function
          except BaseException as err:
            print(err)

  MenuSelection()

  pass
