# -------------------------------------------------------------------------------
# Author:      Santiago Gomez Paz
# Project:     2021 - TEMP lab molten salt reactor sensor
# -------------------------------------------------------------------------------

from __future__ import division, print_function
from libHeLIC import *
from matplotlib.widgets import TextBox, Slider
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import ctypes as ct
import matplotlib as mpl
mpl.use('WxAgg')
sys.path.append(os.path.abspath('../wrapper'))


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


test5()
