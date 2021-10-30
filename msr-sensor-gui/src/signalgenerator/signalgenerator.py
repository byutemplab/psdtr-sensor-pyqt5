from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import numpy as np

from .signal import Signal
from .bk4053b import WaveformGenerator


class SignalGeneratorTab(QWidget):
    def __init__(self):
        super().__init__()
        # Initialize signal parameters and connection with waveform generator
        self.signal = Signal()
        self.device = WaveformGenerator()
        self.InitUI()

    def InitUI(self):
        # Tab header
        font = QFont()
        font.setPointSize(20)
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("Signal Generator Settings")
        self.header.move(30, 20)

        # Pattern preview from matplotlib
        self.plot = PatternPlot(self, width=5, height=3)
        self.plot.move(30, 80)

        # Set shadow behind widget
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(1)
        shadow.setColor(QColor(20, 20, 20, 30))
        self.plot.setGraphicsEffect(shadow)

        # Set font for all small headers
        font = QFont()
        font.setPointSize(8)

        # Waveform type label
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("Waveform")
        self.header.move(30, 410)

        # Waveform type
        self.waveform = QComboBox(self)
        self.waveform.move(30, 430)
        self.waveform.resize(100, 30)
        self.waveform.addItem("Sine")
        self.waveform.addItem("Square")
        self.waveform.addItem("Triangle")
        self.waveform.activated[str].connect(
            self.OnChangeWaveform)

        # Frequency label
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("Frequency (Hz)")
        self.header.move(30 + 133 * 1, 410)

        # Frequency label
        self.frequency = QSpinBox(self)
        self.frequency.move(30 + 133 * 1, 430)
        self.frequency.resize(100, 30)
        self.frequency.setRange(1, 10000)
        self.frequency.setValue(self.signal.frequency)
        self.frequency.valueChanged.connect(self.OnChangeFrequency)

        # Amplitude label
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("Amplitude (V)")
        self.header.move(30 + 133 * 2, 410)

        # Amplitude
        self.amplitude = QDoubleSpinBox(self)
        self.amplitude.move(30 + 133 * 2, 430)
        self.amplitude.resize(100, 30)
        self.amplitude.setRange(0, 10000)
        self.amplitude.setValue(self.signal.amplitude)
        self.amplitude.valueChanged.connect(self.OnChangeAmplitude)

        # Offset label
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("Offset (V)")
        self.header.move(30 + 133 * 3, 410)

        # Offset label
        self.offset = QDoubleSpinBox(self)
        self.offset.move(30 + 133 * 3, 430)
        self.offset.resize(100, 30)
        self.offset.setRange(-10000, 10000)
        self.offset.setValue(self.signal.offset)
        self.offset.valueChanged.connect(self.OnChangeOffset)

        # Phase label
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("Phase (deg)")
        self.header.move(30, 480)

        # Phase
        self.phase = QDoubleSpinBox(self)
        self.phase.move(30, 500)
        self.phase.resize(100, 30)
        self.phase.setRange(0, 360)
        self.phase.setValue(self.signal.phase)
        self.phase.valueChanged.connect(self.OnChangePhase)

        # Send settings to signal generator
        self.set_signal = QPushButton('Set Signal', self)
        self.set_signal.setToolTip('Send settings to signal generator')
        self.set_signal.move(30 + 133 * 3, 500)
        self.set_signal.resize(100, 30)
        self.set_signal.clicked.connect(self.SetSignal)

        self.show()

    def OnChangeFrequency(self, value):
        self.signal.SetFrequency(value)
        self.plot.UpdatePlot()

    def OnChangeAmplitude(self, value):
        self.signal.SetAmplitude(value)
        self.plot.UpdatePlot()

    def OnChangeOffset(self, value):
        self.signal.SetOffset(value)
        self.plot.UpdatePlot()

    def OnChangeWaveform(self, value):
        self.signal.SetWaveform(value)
        self.plot.UpdatePlot()

    def OnChangePhase(self, value):
        self.signal.SetPhase(value)
        self.plot.UpdatePlot()

    def SetSignal(self):
        self.device.Send(self.signal.waveform, self.signal.frequency, self.signal.amplitude,
                         self.signal.offset, self.signal.phase)


class PatternPlot(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        self.parent = parent
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.Plot()

    def Plot(self):
        # Initialize axes
        self.ax = self.figure.add_subplot(111)

        # Initialize plot
        self.UpdatePlot()

        self.figure.tight_layout()
        self.draw()

    def UpdatePlot(self):
        # Clear axes and plot new signal
        self.ax.clear()
        self.ax.plot(self.parent.signal.x, self.parent.signal.y)

        # Set axes labels again
        self.ax.set_xlabel('Time [s]')
        self.ax.set_ylabel('Amplitude [V]')

        self.draw()
