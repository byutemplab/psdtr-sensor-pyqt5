from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

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
            self.parent().label.setPixmap(QPixmap(m.urls()[0].toLocalFile()))


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

        self.label = QLabel(self)
        self.label.setPixmap(QPixmap('icons/upload.png'))
        self.label.move(30, 180)
