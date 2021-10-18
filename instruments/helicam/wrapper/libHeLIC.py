#!/usr/bin/python
#-------------------------------------------------------------------------------
# Name:        libHeLIC
# Description: Python wrapper for libHeLIC library
#
# Last update: 07.10.2016 sm
# Copyright:   (c) Heliotis 2016
#
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import ctypes as ct
import numpy as np
import warnings as wrn
import sys,os
import logging
_log=logging.getLogger(__name__)
if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG,format='%(asctime)s  %(levelname)s:%(module)s:%(lineno)d:%(funcName)s:%(message)s ')

class LibHeLIC(object):
  #-----------------------------------
  #static class variables, definitions
  #-----------------------------------
  @staticmethod
  def Ptr2Arr(data,shape,type_):
    """converts pointer data to a numpyarray with shape 'shape' and of type 'type_'"""
    #buf = np.core.multiarray.int_asbuffer(data, np.prod(shape)*ct.sizeof(type_))
    #data = np.frombuffer(buf, type_)
    buf = ct.cast(data, ct.POINTER(type_ * np.prod(shape)))
    data = np.frombuffer(buf.contents, type_)
    #data=data.reshape(shape,order='C')
    data = np.reshape(data,shape,order='C')
    return data

  @classmethod
  def LoadLib(cls):
    pf=sys.platform
    if pf=="win32":
      fn='libHeLIC.dll'
      try:
        cls.lib=ct.cdll.LoadLibrary(fn) #for Windows
      except WindowsError as err:
        _log.debug(fn+' failed')
      else:
        _log.debug(fn+' loaded')
      if not hasattr(cls,'lib'):
        raise WindowsError('failed to load libHeLIC.dll')
    elif (pf=='linux') or (pf=='linux2'):
        try:
            fn='libhelic.so'
            cls.lib=ct.cdll.LoadLibrary(fn) #for Linux
        except IOError as err:
            _log.critical(fn+' failed')
        else:
            _log.debug(fn+' loaded')
    elif pf=='darwin': #MacOS
        try:
            fn='/usr/local/lib/libhelic.dylib'
            #fn='../../MacOS/build/libhelic.dylib'
            cls.lib=ct.cdll.LoadLibrary(fn) #for Linux
        except IOError as err:
            _log.critical(fn+' failed')
        else:
            _log.debug(fn+' loaded')
    else:
      raise IOError('unsupported platform '+str(pf))

    cls.lib.HE_SetCallback.restype=cls.funcCBType
    cls.lib.HE_GetDefaultCallback.restype=cls.funcCBType
    cls.lib.HE_GetReg.restype=ct.c_uint8
    cls.lib.HE_GetRegDesc.restype= ct.POINTER(cls.RegDesc)
    cls.lib.HE_GetSysDesc.restype= ct.POINTER(cls.SysDesc)
    cls.lib.HE_GetCamData.restype= ct.POINTER(cls.CamData)
    cls.lib.HE_ProcessCamData.restype= ct.POINTER(cls.CamData)

  #------------------------------
  #member functions and variables
  #------------------------------
  def __init__ (self):
    if not hasattr(LibHeLIC,'lib'):
      LibHeLIC.LoadLib()

    if (sys.maxsize > 2**32):
      self.handle = ct.c_longlong(0)
    else:
      self.handle = ct.c_long(0)

  funcCBType = ct.CFUNCTYPE(ct.c_int, ct.c_long, ct.c_int, ct.c_int, ct.c_void_p)

 # most of the following code is generated with: c2py.py
 # if the libHeLIC.h header changes, please execute c2py.py and make a diff of the output
 # to update this file
#-------------------------------- GENERATED c2py.py ----------------------------
  class Reg(ct.Structure):
    pass
  Reg._fields_ = [
    ('num', ct.c_uint8),
    ('id', ct.c_char_p),
    ('cmt', ct.c_char_p),
  ]
  class EnumEntry(ct.Structure):
    pass
  EnumEntry._fields_ = [
    ('num', ct.c_uint),
    ('id', ct.c_char_p),
    ('next', ct.POINTER(EnumEntry)),
  ]
  class RegEntry(ct.Structure):
    pass
  RegEntry._fields_ = [
    ('shift', ct.c_int8),
    ('mask', ct.c_uint8),
    ('reg', ct.POINTER(Reg)),
    ('next', ct.POINTER(RegEntry)),
  ]
  MapMode={
    'MM_volatile':0x1,
    'MM_readonly':0x2,
    'MM_affectDataSize':0x4,
    'MM_hidden':0x8,
    'MM_LAST':0x9,
  }
  CamModeFlags={
    'CM_0':0x1,
    'CM_1':0x2,
    'CM_2':0x4,
    'CM_3':0x8,
    'CM_4':0x10,
    'CM_5':0x20,
    'CM_6':0x40,
    'CM_7':0x80,
    'CM_LAST':0x81,
  }
  class Map(ct.Structure):
    pass
  Map._fields_ = [
    ('id', ct.c_char_p),
    ('cmt', ct.c_char_p),
    ('mode', ct.c_uint8),
    ('regs', ct.POINTER(RegEntry)),
    ('enums', ct.POINTER(EnumEntry)),
    ('group', ct.c_char_p),
    ('level', ct.c_uint8),
    ('minValue', ct.c_ulong),
    ('maxValue', ct.c_ulong),
    ('defValue', ct.c_ulong),
    ('cammode', ct.c_uint8),
  ]
  class RegDesc(ct.Structure):
    pass
  RegDesc._fields_ = [
    ('numReg', ct.c_ushort),
    ('regs', ct.POINTER(Reg)),
    ('numMap', ct.c_ushort),
    ('maps', ct.POINTER(Map)),
  ]
  FeatureFPGA={
    'FF_allow_blind_cycles':0x0,
    'FF_amp_mode_high_z_bug':0x1,
    'FF_amp_mode_high_z_bug_neg':0x2,
    'FF_ascan_first':0x3,
    'FF_bcd_revision_regs':0x4,
    'FF_compression11to8':0x5,
    'FF_datacompression':0x6,
    'FF_dummy_frame_marker':0x7,
    'FF_dynamic_frames':0x8,
    'FF_extended_header':0x9,
    'FF_firmware_ver_regs':0xa,
    'FF_hasI2Cintf':0xb,
    'FF_hasScanHeader':0xc,
    'FF_i2c_registers':0xd,
    'FF_interleaved_quarters':0xe,
    'FF_iq_ascan_first_frame_blocks':0xf,
    'FF_iqdata_in_ribbons':0x10,
    'FF_manual_offset_selector':0x11,
    'FF_mhtheader':0x12,
    'FF_mhtheader_suppress':0x13,
    'FF_mode_amplitude':0x14,
    'FF_need_AcqStop':0x15,
    'FF_needs_fpga_fw_load':0x16,
    'FF_LAST':0x17,
  }
  FeatureUSB={
    'FU_ADC_DAC_via_command':0x0,
    'FU_command_interface':0x1,
    'FU_ends_packets':0x2,
    'FU_hasCmdInterface':0x3,
    'FU_must_load_fx2_fw':0x4,
    'FU_LAST':0x5,
  }
  class Driver(ct.Structure):
    pass
  Driver._fields_ = [
    ('p', ct.c_void_p),
  ]
  class FPGA(ct.Structure):
    pass
  FPGA._fields_ = [
    ('id', ct.c_char_p),
    ('regDesc', ct.c_char_p),
    ('fpgaCfg', ct.c_char_p),
    ('verStr', ct.c_char_p),
    ('variant', ct.c_char_p),
    ('numRegs', ct.c_ushort),
    ('verReg', ct.c_ushort),
    ('verRegBCD', ct.c_uint),
    ('feature', ct.c_uint),
    ('frmMrk', ct.c_ushort),
    ('maxFrm', ct.c_ushort),
    ('maxFrmModeA', ct.c_ushort),
    ('mhtHdrSz', ct.c_ushort),
    ('zFrmBlkSz', ct.c_ushort),
  ]
  class Sensor(ct.Structure):
    pass
  Sensor._fields_ = [
    ('id', ct.c_char_p),
    ('verStr', ct.c_char_p),
    ('pixPitch', ct.c_float*2),
    ('size', ct.c_ushort*2),
    ('orientation', ct.c_uint8),
  ]
  class USB(ct.Structure):
    pass
  USB._fields_ = [
    ('id', ct.c_char_p),
    ('fx2FW', ct.c_char_p),
    ('variant', ct.c_char_p),
    ('verStr', ct.c_char_p),
    ('productID', ct.c_ushort),
    ('vendorID', ct.c_ushort),
    ('feature', ct.c_uint),
    ('protocol', ct.c_uint),
    ('verFx2', ct.c_uint),
    ('config', ct.c_uint8),
    ('iface', ct.c_uint8),
    ('epCmdRead', ct.c_uint8),
    ('epCmdWrite', ct.c_uint8),
    ('epRead', ct.c_uint8),
    ('epWrite', ct.c_uint8),
    ('dataBlockSize', ct.c_ushort),
  ]
  class ETH(ct.Structure):
    pass
  ETH._fields_ = [
    ('id', ct.c_char_p),
    ('port', ct.c_ushort),
    ('protocol', ct.c_uint8),
  ]
  class Motion(ct.Structure):
    pass
  Motion._fields_ = [
    ('id', ct.c_char_p),
  ]
  class SysDesc(ct.Structure):
    pass
  SysDesc._fields_ = [
    ('id', ct.c_char_p),
    ('featStrFPGA', ct.POINTER(ct.c_char_p)),
    ('featStrUSB', ct.POINTER(ct.c_char_p)),
    ('fpga', ct.POINTER(FPGA)),
    ('sensor', ct.POINTER(Sensor)),
    ('usb', ct.POINTER(USB)),
    ('eth', ct.POINTER(ETH)),
    ('motion', ct.POINTER(Motion)),
  ]
  CamDataFmt={
    'DF_UNKNOWN':0x0,
    'DF_I16Q16':0x1,
    'DF_A16P16':0x2,
    'DF_A16':0x3,
    'DF_A8':0x4,
    'DF_A16Z16':0x5,
    'DF_Z16A16P16':0x6,
    'DF_Hf':0x07,
    'DF_AfPf':0x8,
    'DF_IfQf':0x9,
    'DF_LAST':0xa,
  }
  CamDataProperty={
    'DP_PROCESSED':0x1,
    'DP_DATA_EXTERN':0x2,
    'DP_ALIGN512':0x4,
    'DP_ENCODER':0x8,
    'DP_ORDER_3STRIP':0x10,
    'DP_INTERP_CROSS':0x20,
  }
  class CamData(ct.Structure):
    pass
  CamData._fields_ = [
    ('size', ct.c_uint),
    ('format', ct.c_uint),
    ('prop', ct.c_ushort),
    ('refCount', ct.c_ushort),
    ('data', ct.c_void_p),
  ]
  class CamDataMeta(ct.Structure):
    pass
  CamDataMeta._fields_ = [
    ('numDim', ct.c_uint8),
    ('dimSz', ct.c_uint*5),
  ]
  CamInfoSel={
    'IS_MODE':0x1,
    'IS_SCAN':0x1,
    'IS_SIZE':0x2,
    'IS_PITCH':0x4,
    'IS_POS':0x8,
  }
  class CamInfo(ct.Structure):
    pass
  CamInfo._fields_ = [
    ('mode', ct.c_uint),
    ('scanSpeed', ct.c_float),
    ('sizeX', ct.c_uint),
    ('sizeY', ct.c_uint),
    ('sizeZ', ct.c_uint),
    ('voxPitchX', ct.c_float),
    ('voxPitchY', ct.c_float),
    ('voxPitchZ', ct.c_float),
    ('posX', ct.c_float),
    ('posY', ct.c_float),
    ('posZ', ct.c_float),
    ('nPeriodPerSlice', ct.c_uint),
    ('mag', ct.c_float),
    ('wavelength', ct.c_float),
    ('coherenceLen', ct.c_float),
  ]
  FSCmd={
    'FS_CREATE':0x0,
    'FS_CLOSE':0x1,
    'FS_JMP_FRAME_REL':0x2,
    'FS_JMP_FRAME_BEGIN':0x3,
    'FS_JMP_FRAME_END':0x4,
    'FS_GET_NUM_FRAME':0x5,
    'FS_WRITE_OBJ':0x6,
    'FS_PEEK_OBJ':0x7,
    'FS_READ_OBJ':0x8,
    'FS_SKIP_OBJ':0x9,
    'FS_GET_READ_HANDLE':0xa,
    'FS_GET_WRITE_HANDLE':0xb,
  }
  class FSRead(ct.Structure):
    pass
  FSRead._fields_ = [
    ('objID', ct.c_uint),
    ('objSize', ct.c_uint),
    ('data', ct.c_void_p),
  ]
  class FSWrite(ct.Structure):
    pass
  FSWrite._fields_ = [
    ('objID', ct.c_uint),
    ('objSize', ct.c_uint),
    ('data', ct.c_void_p),
  ]
  AcquTimingMode={
    'AT_SET':0x1,
    'AT_GET':0x2,
  }
  class AcquTiming(ct.Structure):
    pass
  AcquTiming._fields_ = [
    ('demodPeriod', ct.c_uint),
    ('delay', ct.c_uint),
    ('framePeriod', ct.c_uint),
  ]
  class CamDataHdr(ct.Structure):
    pass
  CamDataHdr._fields_ = [
    ('dummy0', ct.c_ushort),
    ('syncWord', ct.c_ushort),
    ('dummy1', ct.c_ushort*0xe),
    ('zTags', ct.c_ushort*0x200),
    ('dummy2', ct.c_ushort*0x1e0),
    ('tmpOptics', ct.c_ushort),
    ('tmpLaser', ct.c_ushort),
    ('frmDur', ct.c_uint),
    ('scanDur', ct.c_uint*2),
    ('timeStamp', ct.c_uint*2),
    ('nFrames', ct.c_ushort),
    ('dummy3', ct.c_ushort),
    ('nVolume', ct.c_uint),
  ]
  def FuncCB(self, msg, param, data):
    res=self.lib.HE_FuncCB(self.handle, msg, param, data)
    return res
  SRMsgKind={
    'MK_DEBUG_STRING':0x0,
    'MK_BOX_INFO':0x1,
    'MK_BOX_WARN':0x2,
    'MK_BOX_ERR':0x3,
  }
  SRMsgCategory={
    'MC_GENERAL':0x0,
    'MC_CAM':0x100,
    'MC_MOTION':0x200,
    'MC_USB':0x300,
    'MC_ETH':0x400,
    'MC_SYSTEM':0x500,
    'MC_FIRMWARE':0x600,
    'MC_FILEIO':0x700,
    'MC_XML':0x800,
    'MC_DLG':0x900,
  }
  InternalFuncID={
    'IF_WriteFX2_RAM':0x0,
    'IF_ReadFX2_EEPROM':0x1,
    'IF_WriteFX2_EEPROM':0x2,
    'IF_WriteFX2_SERIAL':0x3,
    'IF_ReadUSB_SERIAL':0x4,
    'IF_BulkReadUSB':0x5,
    'IF_BulkWriteUSB':0x6,
  }
  def SetCallback(self, cb):
    res=self.lib.HE_SetCallback(cb)
    return res
  def GetDefaultCallback(self):
    res=self.lib.HE_GetDefaultCallback()
    return res
  def CheckForNewDllVersion(mode):
    res=self.lib.HE_CheckForNewDllVersion(self.handle, mode)
    return res
  def OpenFile(self, filename):
    res=self.lib.HE_OpenFile(self.handle, filename)
    return res
  def OpenDlgRegDesc(self, parent):
    res=self.lib.HE_OpenDlgRegDesc(self.handle, parent)
    return res
  def CreateStreamFile(self, filename):
    res=self.lib.HE_CreateStreamFile(self.handle, filename)
    return res
  def FileStreamCmd(self, cmd, data, ptr):
    res=self.lib.HE_FileStreamCmd(self.handle, cmd, data, ptr)
    return res
  def Close(self):
    res=self.lib.HE_Close(self.handle)
    return res
  def Read(self, dst, size, address):
    res=self.lib.HE_Read(self.handle, dst, size, address)
    return res
  def Write(self, src, size, address):
    res=self.lib.HE_Write(self.handle, src, size, address)
    return res
  def SetReg(self, reg, val):
    res=self.lib.HE_SetReg(self.handle, reg, val)
    return res
  def GetReg(self, reg):
    res=self.lib.HE_GetReg(self.handle, reg)
    return res
  def GetRegDesc(self):
    res=self.lib.HE_GetRegDesc(self.handle)
    return res
  def GetSysDesc(self):
    res=self.lib.HE_GetSysDesc(self.handle)
    return res
  def SetMap(self, map, val):
    res=self.lib.HE_SetMap(self.handle, map, val)
    return res
  def GetMap(self, map):
    res=self.lib.HE_GetMap(self.handle, map)
    return res
  def SetCamInfo(self, ci, select):
    res=self.lib.HE_SetCamInfo(self.handle, ci, select)
    return res
  def GetCamInfo(self, ci, select):
    res=self.lib.HE_GetCamInfo(self.handle, ci, select)
    return res
  def GetCamData(self, idx, addRef, meta):
    res=self.lib.HE_GetCamData(self.handle, idx, addRef, meta)
    return res
  def SetCamData(self, idx, cd):
    res=self.lib.HE_SetCamData(self.handle, idx, cd)
    return res
  def AllocCamData(self, idx, format, prop, extData, extDataSz):
    res=self.lib.HE_AllocCamData(self.handle, idx, format, prop, extData, extDataSz)
    return res
  def ProcessCamData(self, idx, mode, param):
    res=self.lib.HE_ProcessCamData(self.handle, idx, mode, param)
    return res
  def FreeCamData(self, idx):
    res=self.lib.HE_FreeCamData(self.handle, idx)
    return res
  def SetTimeout(self, ms):
    res=self.lib.HE_SetTimeout(self.handle, ms)
    return res
  def Acquire(self):
    res=self.lib.HE_Acquire(self.handle)
    return res
  def UpdateAcquTiming(self, at, mode):
    res=self.lib.HE_UpdateAcquTiming(self.handle, at, mode)
    return res
 #-------------------------------- GENERATED END --------------------------------
  def GetCamArr(self,idx):
    cdm=LibHeLIC.CamDataMeta()
    cd=self.GetCamData(idx,0,ct.byref(cdm))
    data=cd.contents.data
    if cd.contents.prop&LibHeLIC.CamDataProperty['DP_ENCODER']:
      data+=1024*2 #skip 2k header

    shape=tuple(cdm.dimSz[cdm.numDim-1::-1])
    arr=LibHeLIC.Ptr2Arr(data,shape,ct.c_ushort)
    return arr

  class RegByName(object):
      def __init__ (self,regDesc,libHeLIC):
        self.regDesc = regDesc
        self.libHeLIC = libHeLIC
      def __getattr__(self,name):
        if name=='regDesc' or name=='libHeLIC':
          return object.__getattribute__(self, name)
        rd=self.regDesc.contents
        for idx in range(rd.numReg):
          if rd.regs[idx].id.decode("utf-8")==name:
            return self.libHeLIC.GetReg(rd.regs[idx].num)
        raise AttributeError(str(name)+' is not a valid reg attribute of '+str(self))
      def __setattr__(self,name,value):
        if name=='regDesc' or name=='libHeLIC':
          return object.__getattribute__(self, name)
        rd=self.regDesc.contents
        for idx in range(rd.numReg):
          if rd.regs[idx].id.decode("utf-8")==name:
            return self.libHeLIC.SetReg(rd.regs[idx].num,int(value))
        raise AttributeError(str(name)+' is not a valid reg attribute of '+str(self))
      def __dir__(self):
        l=dir(object)
        rd=self.regDesc.contents
        for idx in range(rd.numReg):
          l.append(rd.regs[idx].id)
        l=set(l)
        l=list(l)
        return l
  class MapByName(object):
      def __init__ (self,regDesc,libHeLIC):
        self.regDesc = regDesc
        self.libHeLIC = libHeLIC

      def __getattr__(self,name):
        if name=='regDesc' or name=='libHeLIC':
          return object.__getattribute__(self, name)
        rd=self.regDesc.contents
        for idx in range(rd.numMap):
          if rd.maps[idx].id.decode("utf-8")==name:
            return self.libHeLIC.GetMap(ct.pointer(rd.maps[idx]))
        raise AttributeError(str(name)+' is not a valid map attribute of '+str(self))

      def __setattr__(self,name,value):
        if name=='regDesc' or name=='libHeLIC':
          return object.__setattr__(self, name,value)
        rd=self.regDesc.contents
        for idx in range(rd.numMap):
          if rd.maps[idx].id.decode("utf-8")==name:
            return self.libHeLIC.SetMap(ct.pointer(rd.maps[idx]),int(value))
        raise AttributeError(str(name)+' is not a valid map attribute of '+str(self))

      def as_dict(self):
          rd=self.regDesc.contents
          d = dict()
          for idx in range(rd.numMap):
            d[rd.maps[idx].id] = self.libHeLIC.GetMap(ct.pointer(rd.maps[idx]))
          return d

      def __dir__(self):
        l=dir(object)
        rd=self.regDesc.contents
        for idx in range(rd.numMap):
          l.append(rd.maps[idx].id)
        l=set(l)
        l=list(l)
        return l

  def __getattr__(self,name):
    if name=='map':
      rd=self.GetRegDesc()
      mapByName=LibHeLIC.MapByName(rd,self)
      return mapByName
    elif name=='reg':
      rd=self.GetRegDesc()
      regByName=LibHeLIC.RegByName(rd,self)
      return regByName
    else:
      return object.__getattribute__(self, name)
  def __setattr__(self,name,value):
    if name=='map':
      print('my__setattr__',name,value)
      return 0
    elif name=='reg':
      print('my__setattr__',name,value)
      return 0
    else:
      return object.__setattr__(self, name,value)
  def __dir__(self):
    l=dir(object)
    l.extend(self.__class__.__dict__.keys())
    l.extend(self.__dict__.keys())
    l.extend(['map','reg'])
    l=set(l)
    l=list(l)
    return l

  def Open(self, mode, *args, **kwargs): #kwargs=keyword arguments
    _log.debug('mode = ' + str(mode))
    _log.debug('args = ' + str(args))
    _log.debug('kwargs = ' + str(kwargs))
    if mode==0:
      s = ''
      if sys.version_info.major < 3:
        items = kwargs.iteritems()
      else:
        items = kwargs.items()
      for k, v in items:
        if s:
          s += ' '
        s = s + k + '=' + v
      try:
        res = self.lib.HE_Open(ct.byref(self.handle), mode, s.encode('utf-8'))
        print('res = ' + str(res))
      except Exception as e:
        print('Exception : ' + str(e))
        #print(e.message)
        res = -1
    elif mode == 1:
      res = self.lib.HE_Open(ct.byref(self.handle), mode, args[0])
    else:
      res = -1
    return res

  @staticmethod
  def InternalFunc(mode, *args):
    res=LibHeLIC.lib.HE_InternalFunc(mode, *args)
    return res

  @staticmethod
  def GetSerials():
    nv=np.ndarray(127*17,dtype=np.uint8) #127 is maximum number of devices
    v=ct.cast(nv.ctypes, ct.POINTER(ct.c_char))
    res=LibHeLIC.lib.HE_GetSerials(v)
    nv = np.reshape(nv,(127,17),order='C')
    serials = []
    for i in range(0, res):
      serialUint = nv[i]
      serialStr = ''
      for c in serialUint:
        serialStr = serialStr + ''.join(chr(c))
        if chr(c) == '\0':
          break
      serialStr = serialStr.strip('\0')
      serials.append(serialStr)
    return res,serials
    
  @staticmethod
  def GetVersion():
    #ver = (ct.c_ushort * 4)()
    #v=ct.cast(ver, ct.POINTER(ct.c_ushort))
    nv=np.ndarray(4,dtype=np.uint16)
    v=ct.cast(nv.ctypes, ct.POINTER(ct.c_ushort))
    res=LibHeLIC.lib.HE_GetVersion(v)
    return res,nv
if __name__ == '__main__':
  def test(str,res):
    pass
    print(str,':',res)

  heSys=LibHeLIC()
  test('GetVersion SrCam',LibHeLIC.GetVersion())
  raw_input('Press Key')

  heSys.Open(0,sys='c3cam')
  rd=heSys.GetRegDesc()
  sd=heSys.GetSysDesc()

  print('\n'+20*'-','Registers:',rd.contents.numReg,20*'-')
  for idx in range(rd.contents.numReg):
    r=rd.contents.regs[idx]
    print(r.num,r.id+'\t'+r.cmt)
  print('\n'+20*'-','Mappings:',rd.contents.numMap,20*'-')
  for idx in range(rd.contents.numMap):
    m=rd.contents.maps[idx]
    print(m.id+'\t',m.cmt)

  #heSys.SetReg(5,3)
  #heSys.GetReg(5)
  #print(heSys.reg.TqpReg_1)
  #heSys.reg.TqpReg_1=5
  #print(heSys.map.bcd_revision)
  #heSys.map.bcd_revision=5
  raw_input('Press Key')
  pass

