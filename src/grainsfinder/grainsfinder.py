from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from .pipeline import GrainBoundariesMap

import numpy as np


class UploadButton(QPushButton):
    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        m = e.mimeData()
        if m.hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        m = e.mimeData()
        if m.hasUrls():
            image = m.urls()[0].toLocalFile()
            self.parent().map.LoadImage(image)
            self.parent().label_raw.setPixmap(QPixmap(self.parent().map.image))
            self.parent().label_preprocessed.setPixmap(
                QPixmap(self.parent().map.edges_path))
            # self.parent().label_preprocessed.setPixmap(
            # QPixmap(self.parent().map.thresholded_path))
            self.parent().label_preprocessed_2.setPixmap(
                QPixmap(self.parent().map.contours_path))
            # self.parent().label_preprocessed_3.setPixmap(
            # QPixmap(self.parent().map.big_contours_path))


class GrainsFinderTab(QWidget):
    def __init__(self):
        super().__init__()
        # Init map object
        self.map = GrainBoundariesMap()
        self.InitUI()

    def InitUI(self):
        # Tab header
        font = QFont()
        font.setPointSize(20)
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("Grains Finder")
        self.header.setContentsMargins(0, 10, 0, 10)

        # Set font for all small headers
        font = QFont()
        font.setPointSize(8)

        # Upload image label
        self.header_upload = QLabel(self)
        self.header_upload.setFont(font)
        self.header_upload.setText("Upload image")
        self.header_upload.move(30, 70)

        # Upload an image widget and button
        self.upload_area = UploadButton("", self)
        self.upload_area.setFixedSize(150, 50)
        self.upload_area.setIcon(QIcon("icons/upload.png"))
        self.upload_area.setIconSize(QSize(100, 50))
        self.upload_area.move(30, 100)

        # Threshold slider label
        self.header_threshold = QLabel(self)
        self.header_threshold.setFont(font)
        self.header_threshold.setText("Threshold")
        self.header_threshold.move(30 + 133, 70)

        # Canny edges threshold slider
        self.threshold_slider = QSlider(Qt.Horizontal, self)
        self.threshold_slider.setGeometry(50, 600, 100, 50)
        self.threshold_slider.setMinimum(0)
        self.threshold_slider.setMaximum(1000)
        self.threshold_slider.setValue(100)
        self.threshold_slider.valueChanged.connect(self.UpdateThreshold)
        self.threshold_slider.move(30 + 133, 100)

        self.label_raw = QLabel(self)
        self.label_raw.setFixedSize(230, 180)

        self.label_preprocessed = QLabel(self)
        self.label_preprocessed.setFixedSize(230, 180)

        self.label_preprocessed_2 = QLabel(self)
        self.label_preprocessed_2.setFixedSize(230, 180)

        # self.label_preprocessed_3 = QLabel(self)
        # self.label_preprocessed_3.setFixedSize(230, 180)

        # Set layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(5, 1)
        self.layout.setRowMinimumHeight(0, 30)
        self.layout.addWidget(self.header, 0, 1, 2, 4, Qt.AlignTop)
        self.layout.addWidget(self.header_upload, 2, 1, 1, 1)
        self.layout.addWidget(self.upload_area, 3, 1, 1, 1)
        self.layout.addWidget(self.header_threshold, 2, 3, 1, 1)
        self.layout.addWidget(self.threshold_slider, 3, 3, 1, 1)
        self.layout.addWidget(self.label_raw, 4, 1, 1, 2)
        self.layout.addWidget(self.label_preprocessed, 4, 3, 1, 2)
        self.layout.addWidget(self.label_preprocessed_2, 5, 1, 1, 2)
        # self.layout.addWidget(self.label_preprocessed_3, 5, 3, 1, 2)
        self.layout.setRowStretch(6, 1)

        self.show()

    def UpdateThreshold(self):
        if(self.map is not None):
            self.map.UpdateThreshold(self.threshold_slider.value())
            self.label_preprocessed.setPixmap(QPixmap(self.map.edges_path))
            # self.label_preprocessed.setPixmap(
            # QPixmap(self.map.thresholded_path))
            self.label_preprocessed_2.setPixmap(
                QPixmap(self.map.contours_path))
            # self.label_preprocessed_3.setPixmap(
            #     QPixmap(self.map.big_contours_path))
