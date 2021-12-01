import skimage.draw
import numpy as np

RES_Y = 1920
RES_X = 1080


class DotsPattern:
    def __init__(self):
        # Set initial parameters
        self.num_measurements = 10
        self.point_diameter = 20
        self.exposure = 50  # in milliseconds
        self.frames_array = []
        self.color = 'green'

    def UpdatePattern(self, trajectories_list, type):
        # Init empty array
        frames_array = []
        for frame in range(self.num_measurements):
            frames_array.append(np.zeros((RES_X, RES_Y)).astype(np.uint8))

        if type == 'rgb':
            # Draw each green dot trajectory in the frames array
            for trajectory in trajectories_list:
                # Get every point in the line
                rr, cc = skimage.draw.line(trajectory['start'][0], trajectory['start'][1],
                                           trajectory['end'][0], trajectory['end'][1])

                # Calculate distance between dots
                dot_step = (len(rr) - 1) / (self.num_measurements - 1)

                # Go through each frame, draw corresponding points
                for frame_idx, frame in enumerate(frames_array):
                    # Get point in the line for this frame
                    dot_idx = round(frame_idx * dot_step)

                    # Draw point in current frame
                    rr_disk, cc_disk = skimage.draw.disk(
                        (rr[dot_idx], cc[dot_idx]), self.point_diameter)
                    frame[rr_disk, cc_disk] = 1

        if type == 'laser':
            # Draw the middle point of each trajectory for the laser beam
            for trajectory in trajectories_list:
                # Get the middle point of the trajectory
                middle_point = (int((trajectory['start'][0] + trajectory['end'][0]) / 2),
                                int((trajectory['start'][1] + trajectory['end'][1]) / 2))

                # Draw the middle point
                rr_disk, cc_disk = skimage.draw.disk(
                    middle_point, self.point_diameter)

                # Draw point in each frame
                for frame in frames_array:
                    frame[rr_disk, cc_disk] = 1

        self.frames_array = frames_array

    def Send(self, dlp):

        # If not connected, try to connect
        if (dlp.connected == False):
            dlp.TryConnection()

        try:
            dlp.stopsequence()
            dlp.changemode(3)

            # Set secondary parameters
            exposure = [self.exposure * 1000]*len(self.frames_array)
            dark_time = [0]*len(self.frames_array)
            trigger_in = [0]*len(self.frames_array)
            trigger_out = [0]*len(self.frames_array)
            repetitions = 0  # infinite loop

            # Start sequence
            dlp.defsequence(self.frames_array, self.color, exposure, trigger_in,
                            dark_time, trigger_out, repetitions)
            dlp.startsequence()
        except:
            dlp.connected = False
            print("Projector not connected")
