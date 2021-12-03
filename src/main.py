import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import styles
from projector.projector import ProjectorTab
from helicam.helicam import HelicamTab
from cmoscamera.cmoscamera import CMOSCameraTab
from analysis.analysis import AnalysisTab
from signalgenerator.signalgenerator import SignalGeneratorTab
from grainsfinder.grainsfinder import GrainsFinderTab


class App(styles.QCustomTabWidget):

    def __init__(self):
        super().__init__()
        self.title = 'TEMPLAB P-SDTR Sensor'
        self.InitUI()

    def InitUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon('icons/psdtr-sensor-icon.png'))
        # self.setGeometry(self.left, self.top, self.width, self.height)

        self.projector_tab = ProjectorTab()
        self.addTab(self.projector_tab, QIcon(
            "icons/projector-icon.png"), "DMD Projector")

        self.helicam_tab = HelicamTab()
        self.addTab(self.helicam_tab, QIcon(
            "icons/camera-icon.png"), "Heliotis Camera")

        self.cmoscamera_tab = CMOSCameraTab()
        self.addTab(self.cmoscamera_tab, QIcon(
            "icons/camera-icon.png"), "CMOS Camera")

        self.analysis_tab = AnalysisTab()
        self.addTab(self.analysis_tab, QIcon(
            "icons/analysis-icon.png"), "Data Analysis")

        self.signal_generator_tab = SignalGeneratorTab()
        self.addTab(self.signal_generator_tab, QIcon(
            "icons/signal-generator-icon.png"), "Signal Generator")

        self.grains_finder_tab = GrainsFinderTab()
        self.addTab(self.grains_finder_tab, QIcon(
            "icons/grains-finder-icon.png"), "Grains Finder")

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setStyle(styles.QCustomProxyStyle())
    app.setStyle("Fusion")
    ex = App()
    sys.exit(app.exec_())
