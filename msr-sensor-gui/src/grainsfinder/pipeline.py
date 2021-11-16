import cv2
import numpy as np
from PIL import Image


class GrainBoundariesMap():
    def __init__(self, image):
        self.image = image
        self.cv2image = cv2.imread(self.image)
        self.imgrey = cv2.cvtColor(self.cv2image, cv2.COLOR_BGR2GRAY)

    def GetContours(self):
        # Get the contours of the grains
        ret, thresh = cv2.threshold(
            self.imgrey, 100, 255, cv2.THRESH_BINARY_INV)
        contours, hierarchy = cv2.findContours(
            thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Draw the contours on the image
        self.imcontours = cv2.drawContours(
            self.cv2image, contours, -1, (0, 255, 0), 3)

        # Save image
        path = 'grainsfinder/logs/contours.png'
        self.Save(self.imcontours, path)

        return path

    def DetectEdges(self):
        # Detect edges
        edges = cv2.Canny(self.imgrey, 100, 200, L2gradient=True)

        # Save image
        path = 'grainsfinder/logs/edges.png'
        self.Save(edges, path)

        return path

    def Save(self, file, path):
        im = Image.fromarray(file)
        im.save(path)
