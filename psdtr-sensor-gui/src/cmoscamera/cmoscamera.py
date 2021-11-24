from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
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
        self.label.move(30, 80)
        self.label.resize(500, 375)
        self.camera.changePixmap.connect(self.SetImage)

        # Start/stop stream
        self.start_stop_btn = QPushButton('Stream', self)
        self.start_stop_btn.setCheckable(True)
        self.start_stop_btn.clicked.connect(self.StartStop)
        self.start_stop_btn.setToolTip(
            'Start streaming data from the CMOS camera')
        self.start_stop_btn.move(30 + 133 * 3, 620)
        self.start_stop_btn.resize(100, 30)

    def StartStop(self):
        if(self.start_stop_btn.isChecked() == True):
            # Try to init camera
            self.camera.Init()
            if(self.camera.connected):
                # If camera is connected, start streaming
                self.camera.start()
            else:
                # If camera is not connected, keep button unchecked
                self.start_stop_btn.toggle()
        else:
            if(self.camera.connected):
                self.camera.Stop()
