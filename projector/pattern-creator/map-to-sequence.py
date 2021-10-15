import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import scipy.misc
from skimage.draw import line, disk


def CreateDotsPatternArray(trajectories_list, num_frames, point_diameter=5, point_shape="circle", rows=100, columns=100):
    # Init empty array
    frames_array = []
    for frame in range(num_frames):
        frames_array.append(np.zeros((rows, columns)).astype(np.uint8))

    # Draw each green dot trajectory in the frames array
    for trajectory in trajectories_list:
        # Get every point in the line
        rr, cc = line(trajectory['start'][0], trajectory['start'][1],
                      trajectory['end'][0], trajectory['end'][1])

        # Calculate distance between dots
        dot_step = (len(rr) - 1) / (num_frames - 1)

        # Go through each frame, draw corresponding points
        for frame_idx, frame in enumerate(frames_array):
            # Get point in the line for this frame
            dot_idx = round(frame_idx * dot_step)

            # Draw point in current frame
            rr_disk, cc_disk = disk((rr[dot_idx], cc[dot_idx]), point_diameter)
            frame[rr_disk, cc_disk] = 1

    return frames_array


trajectories_list = []
trajectories_list.append({'start': (0, 0), 'end': (90, 90)})
trajectories_list.append({'start': (0, 90), 'end': (90, 0)})
trajectories_list.append({'start': (0, 50), 'end': (70, 50)})

frames_array = CreateDotsPatternArray(trajectories_list, 30)

# Plot animation

fig, ax = plt.subplots()
im = ax.imshow(frames_array[0], animated=True)

frame_num = 0


def updatefig(*args):
    global frame_num
    frame_num += 1
    im.set_array(frames_array[frame_num % 30])
    return im,


ani = animation.FuncAnimation(fig, updatefig, interval=10, blit=True)
plt.show()
