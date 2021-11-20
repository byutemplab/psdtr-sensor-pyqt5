from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2
import zwoasi as asi
import time


class CameraThread(QThread):
    changePixmap = pyqtSignal(QImage)
    fps = 0
    frames_counter = 0
    connected = False
    run = False
    first_time_connected = True

    # Init asi library
    env_filename = 'cmoscamera/asi-sdk/lib/ASICamera2.dll'
    asi.init(env_filename)

    def Init(self):
        # Look for connected cameras
        num_cameras = asi.get_num_cameras()

        # If no camera is connected, exit
        if num_cameras == 0:
            self.connected = False
            print("CMOS Camera not connected")
        # If camera is connected, initialize it
        else:
            self.connected = True

            # Init camera object
            if self.first_time_connected:
                self.first_time_connected = False
                camera_id = 0
                self.camera = asi.Camera(camera_id)

            # Start video capture
            self.camera.start_video_capture()

            # Set camera parameters
            self.camera.set_control_value(asi.ASI_GAIN, 50)
            self.camera.set_control_value(asi.ASI_EXPOSURE, 2000)
            self.camera.set_control_value(asi.ASI_BRIGHTNESS, 100)
            self.camera.set_control_value(asi.ASI_FLIP, 0)
            self.camera.set_control_value(asi.ASI_HIGH_SPEED_MODE, 1)
            self.camera.set_roi_format(640, 480, 1, 0)
            # self.camera.set_control_value(asi.ASI_WB_B, 99)
            # self.camera.set_control_value(asi.ASI_WB_R, 75)
            # self.camera.set_control_value(asi.ASI_GAMMA, 50)

    def run(self):
        self.time_start = time.time()
        self.run = True
        while True:
            # Get frame and show in cv2 window
            self.frame = self.camera.capture_video_frame()

            # Convert frame to QImage
            rgbImage = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgbImage.shape
            bytesPerLine = ch * w
            convertToQtFormat = QImage(
                rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
            p = convertToQtFormat.scaled(500, 375, Qt.KeepAspectRatio)

            # Send QImage to GUI
            self.changePixmap.emit(p)

            # Calculate FPS
            self.frames_counter += 1
            if time.time() - self.time_start > 1:
                self.fps = self.frames_counter
                self.frames_counter = 0
                self.time_start = time.time()
                print("fps: ", self.fps)

            # If stop button is pressed, stop thread
            if not self.run:
                break

    def Stop(self):
        self.run = False
        # self.camera.stop_video_capture()
