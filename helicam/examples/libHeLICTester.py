#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        libHeLICTester
# Purpose:     testing libHeLIC functionality.
#              With graphical output
#
# Last update: 23.06.2015 sm
# Copyright:   (c) Heliotis 2015
#
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python
from __future__ import division,print_function

import numpy as np
import matplotlib as mpl
mpl.use('WxAgg')
import matplotlib.pyplot as plt
import os, sys

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

def test(str,res):
  print(str,':',res)

def test1():
  heSys=LibHeLIC()
  test('GetVersion SrCam',LibHeLIC.GetVersion())

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
    print('{:22} {} \n'.format('', m.cmt.decode('windows-1252')))
  
  heSys.Close()

def test2():
  heSys=LibHeLIC()
  heSys.Open(0,sys='c3cam_sl70')

  frames=150
  settings = (
    ('SensTqp',540),
    ('SensNavM2',2),
    ('SensNFrames',frames),
    ('BSEnable',1),
    ('DdsGain',2),
    ('TrigFreeExtN',1),
    ('TrigExtSrcSel',0),
    ('CamMode',4), #simple max
    ('AcqStop',0)
  );

  for k,v in settings:
    try:
      setattr(heSys.map,k,v)#heSys.map.k=v
    except RuntimeError:
      error('Could not set map property %s to %s',k,v)
  
  heSys.AllocCamData(1,LibHeLIC.CamDataFmt['DF_A16Z16'],0,0,0);

  def on_idle(event):
    if on_idle.cnt<0:
      print("on_idle.stop")
      return False
    res=on_idle.heSys.Acquire()
    print("Acquire",on_idle.cnt,"returned",res)

    img=heSys.GetCamData(0,0,0)
    data=img.contents.data+1024*2
    data=LibHeLIC.Ptr2Arr(data,(292,280,2),ct.c_ushort)

    if on_idle.cnt==0:
      on_idle.f.suptitle('GetCamData');
      plt.subplot(1,2,1)
      on_idle.imHdl1=plt.imshow(data[:,:,1],interpolation='nearest') # plot Z-Values
      plt.colorbar()
      plt.subplot(1,2,2)
      on_idle.imHdl2=plt.imshow(data[:,:,0],interpolation='nearest') # plot S-values
      plt.colorbar()
    else:
      on_idle.imHdl1.set_array(data[:,:,1]) # plot Z-Values
      on_idle.imHdl2.set_array(data[:,:,0]) # plot S-values
    event.canvas.draw()
    event.guiEvent.RequestMore()
    on_idle.cnt=on_idle.cnt+1
    return True

  def on_close(event):
    on_idle.cnt=-1

  f=plt.figure();
  on_idle.f=f
  on_idle.heSys=heSys
  on_idle.cnt=0

  f.canvas.mpl_connect('close_event', on_close)
  f.canvas.mpl_connect('idle_event', on_idle)
  plt.show()
  heSys.Close()

def test3():
  heSys=LibHeLIC()
  heSys.Open(0,sys='c3cam_sl70')
  frames=150
  settings = (
    ('SensTqp',540),
    ('SensNavM2',2),
    ('SensNFrames',frames),
    ('BSEnable',1),
    ('DdsGain',2),
    ('TrigFreeExtN',1),
    ('TrigExtSrcSel',0),
    ('CamMode',1),#amplitude
    ('Comp11to8',0),
    ('AcqStop',0)
  );

  for k,v in settings:
    try:
      setattr(heSys.map,k,v)#heSys.map.k=v
    except RuntimeError:
      error('Could not set map property %s to %s',k,v)

  heSys.AllocCamData(1,LibHeLIC.CamDataFmt['DF_A16'],0,0,0);

  def on_idle(event):
    if on_idle.cnt<0:
      print("on_idle.stop")
      return False
    res=heSys.Acquire()
    print("Acquire",on_idle.cnt,"returned",res)
    cd=heSys.ProcessCamData(1,0,0);
    print("ProcessCamData",on_idle.cnt,"returned",cd.contents.data)
    img=heSys.GetCamData(1,0,0)
    data=img.contents.data
    data=LibHeLIC.Ptr2Arr(data,(frames,292,282),ct.c_ushort)

    if on_idle.cnt==0:
      on_idle.f.suptitle('GetCamData');
      plt.subplot(1,2,1)
      on_idle.imHdl1=plt.imshow(data[:,:,141])
      plt.colorbar()
      f.show()
      plt.subplot(1,2,2)
      on_idle.imHdl2=plt.imshow(data[40,:,:])
      plt.colorbar()
    else:
      on_idle.imHdl1.set_array(data[:,:,141])
      on_idle.imHdl2.set_array(data[40,:,:])
    event.canvas.draw()
    event.guiEvent.RequestMore()
    on_idle.cnt=on_idle.cnt+1
    return True

  def on_close(event):
    on_idle.cnt=-1

  f=plt.figure();
  on_idle.f=f
  on_idle.cnt=0

  f.canvas.mpl_connect('close_event', on_close)
  f.canvas.mpl_connect('idle_event', on_idle)
  plt.show()
  heSys.Close()

def test4():
  heSys=LibHeLIC()
  heSys.Open(0,sys='c3cam_sl70')

  frames=150
  settings = (
    ('SensTqp',699),
    ('SensNavM2',2),
    ('SensNFrames',frames),
    ('BSEnable',1),
    ('DdsGain',2),
    ('TrigFreeExtN',1),
    ('TrigExtSrcSel',0),
    ('CamMode',1),#amplitude
    ('Comp11to8',1),
    ('AcqStop',0)
  );

  for k,v in settings:
    try:
      setattr(heSys.map,k,v)#heSys.map.k=v
    except RuntimeError:
      error('Could not set map property %s to %s',k,v)

  heSys.AllocCamData(1,LibHeLIC.CamDataFmt['DF_A8'],0,0,0);

#   test
  res=heSys.Acquire()
  print("Acquire returned",res)
  cd=heSys.ProcessCamData(1,0,0);
  print("ProcessCamData returned",cd.contents.data)
  img=heSys.GetCamData(1,0,0)
  data=img.contents.data
  data=LibHeLIC.Ptr2Arr(data,(frames,292,282),ct.c_uint8)
  print(data)
#   test

  def on_idle(event):
    if on_idle.cnt<0:
      print("on_idle.stop")
      return False
    res=heSys.Acquire()
    print("Acquire",on_idle.cnt,"returned",res)
    cd=heSys.ProcessCamData(1,0,0);
    print("ProcessCamData",on_idle.cnt,"returned",cd.contents.data)
    img=heSys.GetCamData(1,0,0)
    data=img.contents.data
    data=LibHeLIC.Ptr2Arr(data,(frames,292,282),ct.c_uint8)

    if on_idle.cnt==0:
      on_idle.f.suptitle('GetCamData');
      plt.subplot(1,2,1)
      on_idle.imHdl1=plt.imshow(data[:,:,141])
      plt.colorbar()
      f.show()
      plt.subplot(1,2,2)
      on_idle.imHdl2=plt.imshow(data[40,:,:])
      plt.colorbar()
    else:
      on_idle.imHdl1.set_array(data[:,:,141])
      on_idle.imHdl2.set_array(data[40,:,:])
    event.canvas.draw()
    event.guiEvent.RequestMore()
    on_idle.cnt=on_idle.cnt+1
    return True

  def on_close(event):
    on_idle.cnt=-1

  f=plt.figure();
  on_idle.f=f
  on_idle.cnt=0

  f.canvas.mpl_connect('close_event', on_close)
  f.canvas.mpl_connect('idle_event', on_idle)
  plt.show()
  heSys.Close()

def test5():
  heSys=LibHeLIC()
  heSys.Open(0,sys='c3cam_sl70')

  frames=200
  settings = (
    ('SensTqp',540),
    ('SensNavM2',2),
    ('SensNFrames',frames),
    ('BSEnable',1),
    ('DdsGain',2),
    ('TrigFreeExtN',1),
    ('TrigExtSrcSel',0),
    ('CamMode',0),#raw IQ
    ('AcqStop',0)
  );

  for k,v in settings:
    try:
      setattr(heSys.map,k,v)#heSys.map.k=v
    except RuntimeError:
      error('Could not set map property %s to %s',k,v)

  heSys.AllocCamData(1,LibHeLIC.CamDataFmt['DF_I16Q16'],0,0,0);

  def on_idle(event):
    if on_idle.cnt<0:
      print("on_idle.stop")
      return False
    res=heSys.Acquire()
    print("Acquire",on_idle.cnt,"returned",res)
    cd=heSys.ProcessCamData(1,0,0);
    print("ProcessCamData",on_idle.cnt,"returned",cd.contents.data)
    meta = heSys.CamDataMeta()
    img=heSys.GetCamData(1,0,ct.byref(meta))
    data=img.contents.data
    #print(tuple(meta.dimSz[meta.numDim-1::-1]))
    #print(dir(img.contents))
    #print("size = " + str(img.contents.size))
    #print("format = " + str(img.contents.format))
    #print("prop = " + str(img.contents.prop))
    data=LibHeLIC.Ptr2Arr(data,(frames, 300, 300, 2),ct.c_ushort)
    #print("data.shape = " + str(data.shape))
    #data = data[:,:,:,0]
    
    if on_idle.cnt==0:
      on_idle.f.suptitle('GetCamData');
      plt.subplot(1,2,1)
      #on_idle.imHdl1=plt.imshow(data[:,:,0,0])
      on_idle.imHdl1=plt.imshow(data[:,45,:,0])
      plt.colorbar()
      f.show()
      plt.subplot(1,2,2)
      on_idle.imHdl2=plt.imshow(data[25,:,:,1])
      plt.colorbar()
    else:
      #on_idle.imHdl1.set_array(data[:,:,0,0])
      on_idle.imHdl1.set_array(data[:,45,:,0])
      on_idle.imHdl2.set_array(data[25,:,:,1])
    event.canvas.draw()
    event.guiEvent.RequestMore()
    on_idle.cnt=on_idle.cnt+1
    return True

  def on_close(event):
    on_idle.cnt=-1

  f=plt.figure();
  on_idle.f=f
  on_idle.cnt=0

  f.canvas.mpl_connect('close_event', on_close)
  f.canvas.mpl_connect('idle_event', on_idle)
  plt.show()
  heSys.Close()
  
def test6():
  heSys=LibHeLIC()
  heSys.Open(0,sys='c3cam_sl70')
  frames=50
  settings = (
    ('SensTqp',69989),
    ('SensNavM2',20),
    ('SensNFrames',frames),
    ('BSEnable',0),
    ('DdsGain',2),
    ('TrigFreeExtN',1),
    ('TrigExtSrcSel',0),
    ('CamMode',3),#intensity
    ('AcqStop',0)
  );

  for k,v in settings:
    try:
      setattr(heSys.map,k,v)#heSys.map.k=v
    except RuntimeError:
      error('Could not set map property %s to %s',k,v)

  heSys.AllocCamData(1,LibHeLIC.CamDataFmt['DF_I16Q16'],0,0,0);

  def on_idle():
    if on_idle.cnt<0:
      print("on_idle.stop")
      return False
    res=heSys.Acquire()
    print("Acquire",on_idle.cnt,"returned",res)
    cd=heSys.ProcessCamData(1,0,0);
    print("ProcessCamData",on_idle.cnt,"returned",cd.contents.data)
    img=heSys.GetCamData(1,0,0)
    data=img.contents.data
    data=LibHeLIC.Ptr2Arr(data,(frames,300,300,2),ct.c_int16)

    intensity=data[1:,:,:,:].sum(axis=0,dtype=np.int16).sum(axis=2,dtype=np.int16)
    print(intensity)
    if on_idle.cnt<5:
      print("ignore image")
      pass
    elif on_idle.cnt==5:
      print("make fixpattern image")
      on_idle.fixPtrn=intensity
      intensity=np.uint8((intensity-on_idle.fixPtrn)+128)
      on_idle.f.suptitle('GetCamData');
      plt.subplot(1,2,1)
      on_idle.imHdl1=plt.imshow(data[:,:,150,0])
      plt.colorbar()
      f.show()
      plt.subplot(1,2,2)
      on_idle.imHdl2=plt.imshow(intensity,vmin=0, vmax=255,cmap='gray')
      plt.colorbar()
    else:
      intensity=np.uint8((intensity-on_idle.fixPtrn)+128)
      print(intensity.mean(),intensity.std())
      #intensity=np.uint8(((intensity-intensity.mean())/intensity.std()*255/3)+127)
      on_idle.imHdl1.set_array(data[:,:,150,0])
      on_idle.imHdl2.set_array(intensity)
    # event.canvas.draw()
    # event.guiEvent.RequestMore()
    on_idle.cnt=on_idle.cnt+1
    return True

  def on_close(event):
    on_idle.cnt=-1

  f=plt.figure();
  on_idle.f=f
  on_idle.cnt=0

  f.canvas.mpl_connect('close_event', on_close)
  on_idle()
  plt.show()
  heSys.Close()

def test7():
  heSys=LibHeLIC()
  heSys.Open(0,sys='c3cam_sl70')
  
  frames=150
  settings = (
    ('SensTqp',712),
    ('SensNavM2',2),
    ('SensNFrames',frames),
    ('BSEnable',1),
    ('DdsGain',2),
    ('TrigFreeExtN',1),
    ('TrigExtSrcSel',0),
    ('CamMode',4),
    ('AcqStop',0)
  );

  for k,v in settings:
    try:
      setattr(heSys.map,k,v)#heSys.map.k=v
    except RuntimeError:
      error('Could not set map property %s to %s',k,v)

  heSys.AllocCamData(1,LibHeLIC.CamDataFmt['DF_A16Z16'],LibHeLIC.CamDataProperty['DP_INTERP_CROSS'],0,0);

  def on_idle(event):
    if on_idle.cnt<0:
      print("on_idle.stop")
      return False
    res=on_idle.heSys.Acquire()
    print("Acquire",on_idle.cnt,"returned",res)
    print(ct.sizeof(ct.c_ushort))
    data=heSys.GetCamArr(0)

    cd=heSys.ProcessCamData(1,0,0);
    #print("ProcessCamData",on_idle.cnt,"returned",cd.contents.data)
    #img=heSys.GetCamData(1,0,0)
    data=heSys.GetCamArr(1)

    if on_idle.cnt==0:
      on_idle.f.suptitle('GetCamData');
      plt.subplot(1,2,1)
      on_idle.imHdl1=plt.imshow(data[:,:,1],interpolation='nearest') # plot Z-Values
      plt.colorbar()
      plt.subplot(1,2,2)
      on_idle.imHdl2=plt.imshow(data[:,:,0],interpolation='nearest') # plot S-values
      plt.colorbar()
    else:
      on_idle.imHdl1.set_array(data[:,:,1]) # plot Z-Values
      on_idle.imHdl2.set_array(data[:,:,0]) # plot S-values
    print("Z- Value",data[10,10,1]/32)
    event.canvas.draw()
    event.guiEvent.RequestMore()
    on_idle.cnt=on_idle.cnt+1
    return True

  def on_close(event):
    on_idle.cnt=-1

  f=plt.figure();
  on_idle.f=f
  on_idle.heSys=heSys
  on_idle.cnt=0

  f.canvas.mpl_connect('close_event', on_close)
  f.canvas.mpl_connect('idle_event', on_idle)
  plt.show()
  heSys.Close()

def test8():
  heSys=LibHeLIC()
  heSys.Open(0,sys='c3cam_sl70')
  heSys.SetTimeout(0)
  
  frames=150
  hwin=10
  settings = (
    ('SensTqp',699),
    ('SensNavM2',2),
    ('SensNFrames',frames),
    ('BSEnable',1),
    ('DdsGain',2),
    ('TrigFreeExtN',1),
    ('TrigExtSrcSel',0),
    ('ExSimpMaxHwin',hwin),
    ('CamMode',5),
    ('AcqStop',0)
  );

  for k,v in settings:
    try:
      setattr(heSys.map,k,v)#heSys.map.k=v
    except RuntimeError:
      error('Could not set map property %s to %s',k,v)
  #heSys.OpenDlgRegDesc(0)
  heSys.AllocCamData(1,LibHeLIC.CamDataFmt['DF_Z16A16P16'],0,0,0);

  def on_idle(event):
    if on_idle.cnt<0:
      print("on_idle.stop")
      return False
    res=on_idle.heSys.Acquire()
    print("Acquire",on_idle.cnt,"returned",res)

    data=heSys.GetCamArr(0)

    cd=heSys.ProcessCamData(1,0,0);
    data=heSys.GetCamArr(1)

    if on_idle.cnt==0:
      on_idle.f.suptitle('GetCamData');
      plt.subplot(2,3,1)
      on_idle.imHdl1=plt.imshow(data[:,:,hwin+1,0],interpolation='nearest') # plot Z-Values
      plt.colorbar()
      plt.title('Z - values')
      plt.subplot(2,3,2)
      on_idle.imHdl2=plt.imshow(data[:,:,hwin+1,1],interpolation='nearest') # plot A-values
      plt.colorbar()
      plt.title('A - values')
      plt.subplot(2,3,3)
      on_idle.imHdl3=plt.imshow(data[:,:,hwin+1,2],interpolation='nearest') # plot P-values
      plt.colorbar()
      plt.title('Phi - values')
      plt.subplot(2,3,4)
      on_idle.imHdl4=plt.plot(data[10,10,:,2]/(8192.0)) # plot P-values of Ascan
      plt.colorbar()
      plt.title('Pixel')
      plt.subplot(2,3,5)
      on_idle.imHdl5=plt.plot(data[10,10,:,1]) # plot A-values of Ascan
      plt.colorbar()
      plt.title('Ascan')
      print("Zvalue: ",data[10,10,hwin+1,0]/32)
      #plt.subplot(2,3,6)
      #on_idle.imHdl6=plt.plot(data[10,10,hwin+1,0]) # 
      #plt.colorbar()
      #plt.title('ZVal')
    else:
      on_idle.imHdl1.set_array(data[:,:,hwin+1,0]) # plot Z-Values
      on_idle.imHdl2.set_array(data[:,:,hwin+1,1]) # plot A-values
      on_idle.imHdl3.set_array(data[:,:,hwin+1,2]) # plot P-values
      plt.subplot(2,3,4)
      on_idle.imHdl4=plt.cla()
      on_idle.imHdl4=plt.plot(data[10,10,:,2]/(8192.0)) # plot P-values
      plt.subplot(2,3,5)
      on_idle.imHdl5=plt.cla()
      on_idle.imHdl5=plt.plot(data[10,10,:,1]) # plot A-values
      print("Zvalue: ",data[10,10,hwin+1,0]/32)
      #plt.subplot(2,3,6)
      #on_idle.imHdl6=plt.plot(data[10,10,hwin+1,0]) # plot P-values
      #on_idle.imHdl4.set_data(data[10,10,:,2]) # plot S-values
    event.canvas.draw()
    event.guiEvent.RequestMore()
    on_idle.cnt=on_idle.cnt+1
    return True

  def on_close(event):
    on_idle.cnt=-1

  f=plt.figure();
  on_idle.f=f
  on_idle.heSys=heSys
  on_idle.cnt=0

  f.canvas.mpl_connect('close_event', on_close)
  f.canvas.mpl_connect('idle_event', on_idle)
  plt.show()
  heSys.Close()

def test9():
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
      ('2', test2 ,'surface acquisition A16Z16 - simple max'),
      ('3', test3 ,'volume acquisition A16'),
      ('4', test4 ,'volume acquisition A8'),
      ('5', test5 ,'raw data acquisition I16Q16'),
      ('6', test6 ,'intensity image'),
      ('7', test7 ,'surface acquisition, cross remove A16Z16'),
      ('8', test8 ,'surface acquisition, extended simple max Z16A16P16'),
      ('9', test9 ,'scan connected heliCams and print the serial numbers'),
      ('z', testz ,'print out vesions from python. print out path.'),
    )
    while True:
      print ('-'*20)
      for (key,func,txt) in entry:
        print (key,func.__name__+'()',txt)
      print ('x','','exit')
      c=getch() #using from console
    #   c = c.decode("utf-8")
      if c=='x':
        break
      for (key,func,txt) in entry:
        if key==c:
          try:
            func() # run the function
          except BaseException as err:
            print(err)

  MenuSelection()

  #test2()

  pass
