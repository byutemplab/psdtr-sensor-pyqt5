import pycrafter6500 as projector
import matplotlib.pyplot as plt
import matplotlib.colors
import numpy as np


# Returns a numpy array of size diameter x diameter with a circle mask
# For example, CreateCircleArray(5) returns:
# [[0 0 1 0 0]
#  [0 1 1 1 0]
#  [1 1 1 1 1]
#  [0 1 1 1 0]
#  [0 0 1 0 0]]


def CreateCircleArray(diameter):
    Y, X = np.ogrid[:diameter, :diameter]
    dist_from_center = np.sqrt((X - int(diameter / 2))**2
                               + (Y - int(diameter / 2))**2)
    mask = dist_from_center <= int(diameter / 2)

    return mask.astype(np.uint8)


def CreatePointsPattern(resolution_x=1920, resolution_y=1080,
                        num_points_x=10,   num_points_y=10,
                        offset_x=0,        offset_y=0,
                        point_diameter=10, point_shape="circle"):

    # Parameters for the pattern
    distance_x = int(resolution_x / num_points_x)
    distance_y = int(resolution_y / num_points_y)
    offbound_points_flag = False

    # Fill with zeros
    pattern = np.zeros((resolution_y, resolution_x)).astype(np.uint8)

    # Mask with points
    for i in range(resolution_y):
        for j in range(resolution_x):
            if (i - offset_y) % distance_y == 0 and (j - offset_x) % distance_x == 0:
                # Create point array
                if point_shape == "square":
                    point = np.ones((point_diameter, point_diameter))
                    point = point.astype(np.uint8)
                elif point_shape == "circle":
                    point = CreateCircleArray(point_diameter)
                # Replace with point array
                try:
                    pattern[i: i + point_diameter,
                            j: j + point_diameter] = point
                except:
                    offbound_points_flag = True

    return pattern


pattern = CreatePointsPattern(1920, 1080, 2, 2, 100, 100, 80, "circle")

# Convert color to rgb
to_rgb = {
    'disabled': '#000000',
    'red':      '#ff0000',
    'green':    '#00ff00',
    'yellow':   '#00ffff',
    'blue':     '#0000ff',
    'magenta':  '#ff00ff',
    'cyan':     '#ffff00',
    'white':    '#000000',
}

# Custom colormap
point_color = "green"
cmap = matplotlib.colors.ListedColormap(['white', to_rgb[point_color]])

# Plot in GUI
fig, ax = plt.subplots()
ax.imshow(pattern, cmap=cmap)


def SetPattern(pattern, color):

    # Inititalize dmd in mode 3 (intentity visualizer)
    dlp = projector.dmd()
    dlp.TryConnection()
    dlp.stopsequence()
    dlp.changemode(3)

    # Append pattern to image array
    images = []
    images.append(CreatePointsPattern(
        1920, 1080, 2, 2, 0, 0, 80, "circle"))
    images.append(CreatePointsPattern(
        1920, 1080, 2, 2, 500, 0, 80, "circle"))

    # Set secondary parameters
    exposure = [1000000, 1000000]
    dark_time = [0]*2
    trigger_in = [0]*2
    trigger_out = [0]*2
    repetitions = 0  # Repeats infinitely

    # Start sequence
    dlp.defsequence(images, color, exposure, trigger_in,
                    dark_time, trigger_out, repetitions)
    dlp.startsequence()


SetPattern(pattern, point_color)
plt.show()
