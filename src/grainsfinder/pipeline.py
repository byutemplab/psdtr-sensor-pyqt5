import cv2
import numpy as np
from PIL import Image


class GrainBoundariesMap():
    def __init__(self):
        self.threshold = 100
        self.edges_path = ''
        self.contours_path = ''
        self.thresholded_path = ''

    def LoadImage(self, image):
        self.image = image
        self.cv2image = cv2.imread(self.image)
        self.imgrey = cv2.cvtColor(self.cv2image, cv2.COLOR_BGR2GRAY)
        self.PreProcessing()

    def PreProcessing(self):

        # Find edges
        self.edges = cv2.Canny(
            self.imgrey, self.threshold, 200, L2gradient=True)

        # Save edges image
        self.edges_path = 'grainsfinder/logs/edges.png'
        self.Save(self.edges, self.edges_path)

        # Get the contours of the grains
        contours, hierarchy = cv2.findContours(
            self.edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Draw the contours on the image
        self.contours = self.cv2image.copy()
        cv2.drawContours(self.contours, contours, -1, (0, 255, 0), 3)

        # Save contours image
        self.contours_path = 'grainsfinder/logs/contours.png'
        self.Save(self.contours, self.contours_path)

        # Get area of each contour
        areas = [cv2.contourArea(c) for c in contours]
        print(areas)

        # Filter out small contours
        big_contours = [c for c in contours if cv2.contourArea(c) > 100]

        # Draw the contours on the image
        self.big_contours = self.cv2image.copy()
        cv2.drawContours(self.big_contours, big_contours, -1, (0, 255, 0), 3)

        # Save big contours image
        self.big_contours_path = 'grainsfinder/logs/big-contours.png'
        self.Save(self.big_contours, self.big_contours_path)

    def DetectEdges(self):
        # Detect edges
        edges = cv2.Canny(self.imgrey, 100, 200, L2gradient=True)

        # Print list of edges
        print("Edges:")
        print(edges)

        # Save image
        self.imedges_path = 'grainsfinder/logs/edges.png'
        self.Save(edges, self.imedges_path)

        return self.imedges_path

    def Save(self, file, path):
        im = Image.fromarray(file)
        im.save(path)

    def UpdateThreshold(self, threshold):
        self.threshold = threshold
        self.PreProcessing()
