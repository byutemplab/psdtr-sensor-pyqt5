#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        callback example
#
# Last update: 06.10.2016 sm
# Copyright:   (c) Heliotis 2016
#
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

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

  

# ###
# my_callback
# This is a custom callback function for the heliCam API written in Python...  
# Return value: must be a integer (e.g. 0)
# Parameters:
# hdl:      Low-Level Camera handle. Not used in the Python function (should be 0 in Python)
# msg:      Message type
#           0x0001: CM_MSG_DISPLAY : display a message (default is a pop-up windows)
#           0x0020: CM_PROGRESS : not used...
# param:    Data type from the message (But only the first 8 bit...)
#           0x00: MK_DEBUG_STRING : debug information
#           0x01: MK_BOX_INFO : informations
#           0x02: MK_BOX_WARN : warning (e.g. no camer connected, firmware download failed, acquire fauled, ...)
#           0x03: MK_BOX_ERR : error (e.g. illegal camera handle)
# data:     Datas from the message, for the normal case its a string...
def my_callback(hdl, msg, param, data):
    print('my_callback function is called\n')
    # mask MSBs from param (use only 8bit)
    param = param & 0xFF
    # check the msg and param value:
    if (msg == 0x01) or (msg == 0x20):
        if (param == 0x00) or (param == 0x01) or (param == 0x02) or (param == 0x03):
            # in this case, the data is a string... do the typecast
            data_str = ct.cast(data, ct.c_char_p).value
            print('msg: ' + str(msg) + ' param: ' + str(param) + ' data:\n' + data_str)
            return 0
    # if the msg type and parameter not listed, print only this type informations:
    print('Unknown callback information: [msg: ' + str(msg) + ' param: ' + str(param) + ']')
    return 0

if __name__ == '__main__':
  print("Start script...? (y)")  
  if getch() == 'y':
    print('load library')
    heSys=LibHeLIC()
    
    print ('define and set callback function')
    cb_func = heSys.funcCBType(my_callback)
    heSys.SetCallback(cb_func)
    
    print ('callback function is set...')
    heSys.Open(0,sys='c3cam_sl70')
  pass
  