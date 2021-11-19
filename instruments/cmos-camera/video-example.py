import zwoasi as asi
import cv2
import threading


class GetFrame(threading.Thread):
    def __init__(self):
        # Init thread
        threading.Thread.__init__(self)

        # Init camera
        env_filename = 'asi-sdk\lib\ASICamera2.dll'
        asi.init(env_filename)
        self.camera = asi.Camera(0)
        self.camera.start_video_capture()

        # Set camera parameters
        self.camera.set_control_value(asi.ASI_GAIN, 50)
        self.camera.set_control_value(asi.ASI_EXPOSURE, 100)
        self.camera.set_control_value(asi.ASI_WB_B, 99)
        self.camera.set_control_value(asi.ASI_WB_R, 75)
        self.camera.set_control_value(asi.ASI_GAMMA, 50)
        self.camera.set_control_value(asi.ASI_BRIGHTNESS, 150)
        self.camera.set_control_value(asi.ASI_FLIP, 0)

    def run(self):
        while True:
            # Get frame and show in cv2 window
            self.frame = self.camera.capture_video_frame()
            cv2.imshow('frame', self.frame)

            # Exit if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


task1 = GetFrame()
task1.start()
