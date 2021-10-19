# -------------------------------------------------------------------------------
# Name:        intensity-isualizer
# Purpose:     graph intensity in a 2d graph
# Author:      Santiago Gomez Paz
# Project:     2021 - TEMP lab
# -------------------------------------------------------------------------------

from __future__ import division, print_function
from libHeLIC import *
from matplotlib.widgets import TextBox, Slider
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import sys
import ctypes as ct
from datetime import datetime
import matplotlib as mpl
mpl.use('WxAgg')
sys.path.append(os.path.abspath('../wrapper'))


# ========= Get registers ========= #

def test1():
    heSys = LibHeLIC()
    print('GetVersion SrCam : ', LibHeLIC.GetVersion())

    heSys.Open(0, sys='c3cam_sl70')
    rd = heSys.GetRegDesc()
    sd = heSys.GetSysDesc()

    print('\n'+20*'-', 'Registers:', rd.contents.numReg, 20*'-')
    for idx in range(rd.contents.numReg):
        r = rd.contents.regs[idx]
        print('{:<3} {:18} {:30} \n'.format(r.num, r.id.decode(
            'windows-1252'), r.cmt.decode('windows-1252')))

    print('\n'+20*'-', 'Mappings:', rd.contents.numMap, 20*'-')
    for idx in range(rd.contents.numMap):
        m = rd.contents.maps[idx]
        print('{:22} {} - lvl:cammode {}:{} \t def:min:max {}:{}:{}'.format(m.id.decode('windows-1252'),
              m.group.decode('windows-1252'), str(m.level), str(m.level), str(m.defValue), str(m.minValue), str(m.maxValue)))
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
            setattr(heSys.map, k, v)  # heSys.map.k=v
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

    # Save data to a npy file
    date = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
    path = os.path.join('logs', 'intensity_img_' + date + '.npy')
    np.save(path, data)

    # Convert I, Q --> Amplitude and Phase
    def IQtoAmplitudeAndPhase(data):
        I = data[:, :, :, 0]
        Q = data[:, :, :, 1]
        newData[:, :, :, 0] = np.sqrt(np.power(I, 2) + np.power(Q, 2))
        newData[:, :, :, 1] = np.arctan2(I, Q)
        return newData

    # print(data)
    # print(IQtoAmplitudeAndPhase(data))

    # Start by showing frame 0 and I parameter
    frameNum = 0
    IQProperty = 0

    # Initialize plot
    fig, ax = plt.subplots()
    graph = ax.imshow(data[frameNum, :, :, IQProperty])

    # Update frame selection
    def selectFrame(val):
        if type(val) is int:
            frameNum = val
        else:
            frameNum = val.astype(int)
        ax.imshow(data[frameNum, :, :, IQProperty])
        fig.canvas.draw_idle()

    # Slider for frames
    ax_slider = plt.axes([0.20, 0.01, 0.65, 0.03])
    slider = Slider(ax_slider, 'Frames ', 0, 49,
                    valinit=0, valfmt='%d', valstep=1)
    slider.on_changed(selectFrame)

    # Update IQ property selection
    def selectIQProperty(val):
        if type(val) is int:
            IQProperty = val
        else:
            IQProperty = val.astype(int)
        ax.imshow(data[frameNum, :, :, IQProperty])
        fig.canvas.draw_idle()

    # Slider for IQ properties
    ax_slider_2 = plt.axes([0.20, 0.05, 0.65, 0.03])
    slider_2 = Slider(ax_slider_2, 'I:0, Q:1 ', 0, 1,
                      valinit=0, valfmt='%d', valstep=1)
    slider_2.on_changed(selectIQProperty)

    # Show graph + sliders
    plt.show()

    # Shut down camera
    heSys.Close()

# ========= Visualize Intensity (from npy file) ========= #


def test3():
    # Import data
    print("Enter path of the .npy file to visualize: ")
    path = input()
    data = np.load(path)

    # Start by showing frame 0 and I parameter
    frameNum = 0
    IQProperty = 0

    # Initialize plot
    fig, ax = plt.subplots()
    graph = ax.imshow(data[frameNum, :, :, IQProperty])

    # Update frame selection
    def selectFrame(val):
        if type(val) is int:
            frameNum = val
        else:
            frameNum = val.astype(int)
        ax.imshow(data[frameNum, :, :, IQProperty])
        fig.canvas.draw_idle()

    # Slider for frames
    ax_slider = plt.axes([0.20, 0.01, 0.65, 0.03])
    slider = Slider(ax_slider, 'Frames ', 0, 49,
                    valinit=0, valfmt='%d', valstep=1)
    slider.on_changed(selectFrame)

    # Update IQ property selection
    def selectIQProperty(val):
        if type(val) is int:
            IQProperty = val
        else:
            IQProperty = val.astype(int)
        ax.imshow(data[frameNum, :, :, IQProperty])
        fig.canvas.draw_idle()

    # Slider for IQ properties
    ax_slider_2 = plt.axes([0.20, 0.05, 0.65, 0.03])
    slider_2 = Slider(ax_slider_2, 'I:0, Q:1 ', 0, 1,
                      valinit=0, valfmt='%d', valstep=1)
    slider_2.on_changed(selectIQProperty)

    # Show graph + sliders
    plt.show()

# ========= Surface adquisition ========= #


def test4():
    # Init library and open camera
    heSys = LibHeLIC()
    heSys.Open(0, sys='c3cam_sl70')

    # Set parameters
    frames = 50
    hwin = 10
    settings = (
        ('CamMode',       5),         # surface adquisition
        ('SensTqp',       69989),     # measure 500 Hz
        ('SensDeltaExp',  0),
        ('SensNavM2',     2),
        ('SensNFrames',   frames),
        ('ExSimpMaxHwin', hwin),
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
            setattr(heSys.map, k, v)  # heSys.map.k=v
        except RuntimeError:
            error('Could not set map property %s to %s', k, v)

    # Allocate place for data in IQ format
    heSys.AllocCamData(1, LibHeLIC.CamDataFmt['DF_Z16A16P16'], 0, 0, 0)

    # Get raw data from the camera
    cnt = 0
    res = heSys.Acquire()
    print("Acquire", cnt, "returned", res)

    # Process data
    cd = heSys.ProcessCamData(1, 0, 0)
    print("ProcessCamData", cnt, "returned", cd.contents.data)

    # Get data and put it in an array
    data = heSys.GetCamArr(0)
    cd = heSys.ProcessCamData(1, 0, 0)
    data = heSys.GetCamArr(1)

    # Start by showing frame 0 and I parameter
    frameNum = 0
    property = 0

    # Initialize plot
    fig, ax = plt.subplots()
    graph = ax.imshow(data[:, :, frameNum, property])

    # Update frame selection
    def selectFrame(val):
        if type(val) is int:
            frameNum = val
        else:
            frameNum = val.astype(int)
        ax.imshow(data[:, :, frameNum, property])
        fig.canvas.draw_idle()

    # Slider for frames
    ax_slider = plt.axes([0.20, 0.01, 0.65, 0.03])
    slider = Slider(ax_slider, 'Slide ->', 0, 20,
                    valinit=0, valfmt='%d', valstep=1)
    slider.on_changed(selectFrame)

    # Update IQ property selection
    def selectProperty(val):
        if type(val) is int:
            property = val
        else:
            property = val.astype(int)
        ax.imshow(data[:, :, frameNum, property])
        fig.canvas.draw_idle()

    # Slider for properties
    ax_slider_2 = plt.axes([0.20, 0.05, 0.65, 0.03])
    slider_2 = Slider(ax_slider_2, '0: Z, 1: A, 2: P', 0,
                      2, valinit=0, valfmt='%d', valstep=1)
    slider_2.on_changed(selectProperty)

    # Show graph + sliders
    plt.show()

    # Shut down camera
    heSys.Close()

# ========= Visualize Intensity (average)========= #


def test5():
    # Init library and open camera
    heSys = LibHeLIC()
    heSys.Open(0, sys='c3cam_sl70')

    # Set parameters
    frames = 50
    settings = (
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
            setattr(heSys.map, k, v)  # heSys.map.k=v
        except RuntimeError:
            error('Could not set map property %s to %s', k, v)

    # Allocate place for data in IQ format
    heSys.AllocCamData(1, LibHeLIC.CamDataFmt['DF_I16Q16'], 0, 0, 0)

    for i in range(10):
        # Get raw data from the camera
        res = heSys.Acquire()
        print("Acquire", i, "returned", res)

        # Process data
        cd = heSys.ProcessCamData(1, 0, 0)
        print("ProcessCamData", i, "returned", cd.contents.data)

        # Get data and put it in an array
        # Array shape: frames * 300 [width] * 300 [height] * 2 [I and Q]
        img = heSys.GetCamData(1, 0, 0)
        data = img.contents.data
        data = LibHeLIC.Ptr2Arr(data, (frames, 300, 300, 2), ct.c_int16)

        # Sum data from all frames, skip frame 0
        intensity = data[1:, :, :, 0].sum(
            axis=0, dtype=np.int16)

        if(i == 0):
            # Initialize plot
            fig, ax = plt.subplots()
            graph = ax.imshow(intensity)
            fig.colorbar(graph)
            plt.ion()
            plt.show()
        else:
            graph.set_array(intensity)
            plt.draw()
            plt.pause(0.001)

    # Shut down camera
    heSys.Close()

# ========= Visualize Intensity (IQ to Amplitude, phase)========= #


def test6():
    # Init library and open camera
    heSys = LibHeLIC()
    heSys.Open(0, sys='c3cam_sl70')

    # Set parameters
    frames = 50
    settings = (
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
            setattr(heSys.map, k, v)  # heSys.map.k=v
        except RuntimeError:
            error('Could not set map property %s to %s', k, v)

    # Allocate place for data in IQ format
    heSys.AllocCamData(1, LibHeLIC.CamDataFmt['DF_I16Q16'], 0, 0, 0)

    for i in range(10000):
        # Get raw data from the camera
        res = heSys.Acquire()
        print("Acquire", i, "returned", res)

        # Process data
        cd = heSys.ProcessCamData(1, 0, 0)
        print("ProcessCamData", i, "returned", cd.contents.data)

        # Get data and put it in an array
        # Array shape: frames * 300 [width] * 300 [height] * 2 [I and Q]
        img = heSys.GetCamData(1, 0, 0)
        data = img.contents.data
        data = LibHeLIC.Ptr2Arr(data, (frames, 300, 300, 2), ct.c_int16)

        # Get I
        intensity_i = data[1:, :, :, 0].sum(
            axis=0, dtype=np.int64)

        # Get Q
        intensity_q = data[1:, :, :, 1].sum(
            axis=0, dtype=np.int64)

        # Calculate amplitude
        intensity_amp = np.sqrt(
            np.power(intensity_i, 2) + np.power(intensity_q, 2))

        # Calculate phase
        intensity_phase = np.arctan2(intensity_i, intensity_q)

        if(i == 0):
            # Initialize plot
            fig, axs = plt.subplots(2, 2)
            i_graph = axs[0, 0].imshow(intensity_i, interpolation='nearest')
            axs[0, 0].title.set_text('I')
            q_graph = axs[0, 1].imshow(intensity_q)
            axs[0, 1].title.set_text('Q')
            amp_graph = axs[1, 0].imshow(intensity_amp)
            axs[1, 0].title.set_text('Amplitude')
            phase_graph = axs[1, 1].imshow(intensity_phase)
            axs[1, 1].title.set_text('Phase')
            plt.ion()
            plt.show()
        else:
            i_graph.set_array(intensity_i)
            q_graph.set_array(intensity_q)
            amp_graph.set_array(intensity_amp)
            phase_graph.set_array(intensity_phase)
            plt.pause(0.001)

    # Turn off interactive mode and stay in graph window
    plt.ioff()
    plt.show()

    # Save data list to a npy file
    date = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
    path = os.path.join('logs', 'intensity_data_list_' + date + '.npy')
    np.save(path, data_list)

    # Shut down camera
    heSys.Close()

# ========= List connected cameras ========= #


def test7():
    print('-'*20)
    heSys = LibHeLIC()
    [count, serials] = LibHeLIC.GetSerials()
    print('No of installed heliCams: ' + str(count))
    for item in serials:
        print(item)


def testz():
    print('-'*20)
    print('Used Python version:')
    print(sys.version)
    print('-'*20)
    print('Search libHeLIC in:')
    for ImportPath in sys.path:
        print(ImportPath)
    print('-'*20)
    print('Numpy version:')
    print(np.version.version)
    print('Matplotlib version:')
    print(mpl.__version__)
    print('libHeLIC version:')
    heSys = LibHeLIC()
    print(str(LibHeLIC.GetVersion()[1][3]) + '.' + str(LibHeLIC.GetVersion()[1][2]) +
          '.' + str(LibHeLIC.GetVersion()[1][1])+'.' + str(LibHeLIC.GetVersion()[1][0]))


if __name__ == '__main__':

    def MenuSelection():
        entry = (
            ('1', test1, 'show registerDescr of sys=c3cam_sl70'),
            ('2', test2, 'intensity image'),
            ('3', test3, 'display saved intensity image'),
            ('4', test4, 'amplitude + phase image'),
            ('5', test5, 'intensity image (averaged)'),
            ('6', test6, 'intensity image (IQ to amplitude, phase)'),
            ('7', test7, 'scan connected heliCams and print the serial numbers'),
            ('z', testz, 'print out vesions from python. print out path.'),
        )
        while True:
            print('-'*20)
            for (key, func, txt) in entry:
                print(key, func.__name__+'()', txt)
            print('x', '', 'exit')
            c = input()  # using from console
            if c == 'x':
                break
            for (key, func, txt) in entry:
                if key == c:
                    try:
                        func()  # run the function
                    except BaseException as err:
                        print(err)

    MenuSelection()

    pass
