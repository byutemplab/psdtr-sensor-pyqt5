import numpy as np
from scipy import signal as sg


class Signal:
    def __init__(self):
        self.waveform = "Sine"
        self.frequency = 1
        self.amplitude = 1
        self.offset = 0
        self.phase = 0
        self.x = 0
        self.y = 0
        self.Update()

    def Update(self):
        start = 0
        stop = 1 / self.frequency               # Only show one period
        step = 0.001 / self.frequency
        self.x = np.arange(start, stop, step)

        if self.waveform == "Sine":
            self.y = np.sin(2 * np.pi * self.frequency *
                            self.x + np.deg2rad(self.phase))
            self.y = self.y * self.amplitude + self.offset
        elif self.waveform == "Square":
            self.y = np.sign(
                np.sin(2 * np.pi * self.frequency * self.x + np.deg2rad(self.phase)))
            self.y = self.y * self.amplitude + self.offset
        elif self.waveform == "Triangle":
            self.y = sg.sawtooth(
                2 * np.pi * self.frequency * self.x + np.deg2rad(90 + self.phase), width=0.5)  # 0.5 makes the sawtooth look like a triangle
            self.y = self.y * self.amplitude + self.offset

    def SetWaveform(self, waveform):
        self.waveform = waveform
        self.Update()

    def SetAmplitude(self, amplitude):
        self.amplitude = amplitude
        self.Update()

    def SetOffset(self, offset):
        self.offset = offset
        self.Update()

    def SetFrequency(self, frequency):
        self.frequency = frequency
        self.Update()

    def SetPhase(self, phase):
        self.phase = phase
        self.Update()
