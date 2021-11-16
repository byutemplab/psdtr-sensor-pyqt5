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
            map = GrainBoundariesMap(image)
            self.parent().label_raw.setPixmap(QPixmap(map.image))
            self.parent().label_preprocessed.setPixmap(QPixmap(map.GetContours()))
            self.parent().label_preprocessed_2.setPixmap(QPixmap(map.DetectEdges()))


class GrainsFinderTab(QWidget):
    def __init__(self):
        super().__init__()
        self.InitUI()

    def InitUI(self):
        # Tab header
        font = QFont()
        font.setPointSize(20)
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("Grains Finder")
        self.header.move(30, 20)

        # Upload an image widget and button
        button = UploadButton("", self)
        button.resize(100, 100)
        button.setIcon(QIcon("icons/upload.png"))
        button.setIconSize(QSize(100, 100))
        button.move(30, 70)

        self.label_raw = QLabel(self)
        self.label_raw.move(30, 200)
        self.label_raw.resize(200, 200)

        self.label_preprocessed = QLabel(self)
        self.label_preprocessed.move(250, 200)
        self.label_preprocessed.resize(200, 200)

        self.label_preprocessed_2 = QLabel(self)
        self.label_preprocessed_2.move(30, 420)
        self.label_preprocessed_2.resize(200, 200)
