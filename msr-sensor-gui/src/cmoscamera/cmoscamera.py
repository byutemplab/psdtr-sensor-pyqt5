import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2
import zwoasi as asi
from .camerastream import CameraThread


class CMOSCameraTab(QWidget):
    def __init__(self):
        super().__init__()
        self.camera = CameraThread(self)
        self.InitUI()

    def SetImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def InitUI(self):
        # Tab header
        font = QFont()
        font.setPointSize(20)
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("CMOS Camera")
        self.header.move(30, 20)

        # Camera Stream Viewer
        self.label = QLabel(self)
        self.label.move(30, 100)
        self.label.resize(640, 480)
        self.camera.changePixmap.connect(self.SetImage)

        # Start video stream
        self.camera.Init()
        if(self.camera.connected):
            self.camera.start()
