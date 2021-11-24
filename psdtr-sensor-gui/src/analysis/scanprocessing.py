import numpy as np
import cv2


class Scan:
    def __init__(self, array):
        self.array = array
        self.num_frames = array.shape[0]

    def GetIntensityOverTime(self):
        intensity = []
        for frame in self.array:
            image = Frame(frame)
            intensity.append(image.GetIntensity(box_size=40))
        return intensity


class Frame:
    def __init__(self, array):
        self.image = array
        self.x = array.shape[0]
        self.y = array.shape[1]

    def GetDotCenter(self):
        # Get all contours
        contours, hierarchy = cv2.findContours(
            self.image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Find largest contour
        c = max(contours, key=cv2.contourArea)

        # Find center of contour
        M = cv2.moments(c)
        x = int(M["m10"] / M["m00"])
        y = int(M["m01"] / M["m00"])

        # Return center coordinates
        return (x, y)

    def GetIntensity(self, box_size):
        # Calculate box coordinates
        dot_center = self.GetDotCenter()
        x_start = int(dot_center[0] - box_size / 2)
        x_end = int(dot_center[0] + box_size / 2)
        y_start = int(dot_center[1] - box_size / 2)
        y_end = int(dot_center[1] + box_size / 2)

        # Get average of all pixels inside box
        intensity = np.mean(self.image[y_start:y_end, x_start:x_end])

        return intensity
