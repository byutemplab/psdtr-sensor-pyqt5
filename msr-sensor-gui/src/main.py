import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import styles
from projector.projector import ProjectorTab
from camera.camera import CameraTab


class App(styles.QCustomTabWidget):

    def __init__(self):
        super().__init__()
        self.left = 320
        self.top = 40
        self.title = 'TEMPLAB MSR Sensor'
        self.width = 740
        self.height = 680
        self.InitUI()

    def InitUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon('icons/msr-sensor-icon.png'))
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.projector_tab = ProjectorTab()
        self.addTab(self.projector_tab, QIcon(
            "icons/projector-icon.png"), "DMD Projector")

        self.camera_tab = CameraTab()
        self.addTab(self.camera_tab, QIcon(
            "icons/camera-icon.png"), "Heliotis Camera")

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setStyle(styles.QCustomProxyStyle())
    app.setStyle("Fusion")
    ex = App()
    sys.exit(app.exec_())
