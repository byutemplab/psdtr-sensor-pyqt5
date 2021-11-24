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
        self.header.move(30, 20)

        # Set font for all small headers
        font = QFont()
        font.setPointSize(8)

        # Number of measurements label
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("Upload image")
        self.header.move(30, 70)

        # Upload an image widget and button
        button = UploadButton("", self)
        button.resize(100, 50)
        button.setIcon(QIcon("icons/upload.png"))
        button.setIconSize(QSize(50, 100))
        button.move(30, 100)

        # Threshold slider label
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("Threshold")
        self.header.move(30 + 133, 70)

        # Canny edges threshold slider
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setGeometry(50, 600, 100, 50)
        self.slider.setMinimum(0)
        self.slider.setMaximum(1000)
        self.slider.setValue(100)
        self.slider.valueChanged.connect(self.UpdateThreshold)
        self.slider.move(30 + 133, 100)

        self.label_raw = QLabel(self)
        self.label_raw.move(30, 200)
        self.label_raw.resize(200, 200)

        self.label_preprocessed = QLabel(self)
        self.label_preprocessed.move(250, 200)
        self.label_preprocessed.resize(200, 200)

        self.label_preprocessed_2 = QLabel(self)
        self.label_preprocessed_2.move(30, 420)
        self.label_preprocessed_2.resize(200, 200)

        # self.label_preprocessed_3 = QLabel(self)
        # self.label_preprocessed_3.move(250, 420)
        # self.label_preprocessed_3.resize(200, 200)

    def UpdateThreshold(self):
        if(self.map is not None):
            self.map.UpdateThreshold(self.slider.value())
            self.label_preprocessed.setPixmap(QPixmap(self.map.edges_path))
            # self.label_preprocessed.setPixmap(
            # QPixmap(self.map.thresholded_path))
            self.label_preprocessed_2.setPixmap(
                QPixmap(self.map.contours_path))
            # self.label_preprocessed_3.setPixmap(
            #     QPixmap(self.map.big_contours_path))
