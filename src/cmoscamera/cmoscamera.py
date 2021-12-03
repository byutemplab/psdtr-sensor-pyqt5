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
        self.header.setContentsMargins(0, 10, 0, 10)

        # Camera Stream Viewer
        self.label = QLabel(self)
        self.label.setFixedSize(500, 375)
        self.camera.changePixmap.connect(self.SetImage)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Start/stop stream
        self.start_stop_btn = QPushButton('Stream', self)
        self.start_stop_btn.setCheckable(True)
        self.start_stop_btn.clicked.connect(self.StartStop)
        self.start_stop_btn.setToolTip(
            'Start streaming data from the CMOS camera')
        self.start_stop_btn.move(30 + 133 * 3, 620)
        self.start_stop_btn.resize(100, 30)

        # Set layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(5, 1)
        self.layout.setRowMinimumHeight(0, 30)
        self.layout.addWidget(self.header, 0, 1, 2, 4, Qt.AlignTop)
        self.layout.addWidget(self.label, 2, 1, 4, 4)
        self.layout.addWidget(self.start_stop_btn, 6, 4, 1, 1)
        self.layout.setRowStretch(7, 1)

        self.show()

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
