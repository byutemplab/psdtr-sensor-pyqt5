import pycrafter6500
import numpy as np

# Array containing 1080 x 1920 images
images = []
pattern_1 = np.random.default_rng(42).random((1080, 1920))
pattern_1 = pattern_1.astype(np.uint8)
images.append(pattern_1)

# Inititalize dmd
dlp = pycrafter6500.dmd()
dlp.TryConnection()
dlp.stopsequence()
dlp.changemode(3)

color = 'blue'
exposure = [0]*30
dark_time = [0]*30
trigger_in = [False]*30
trigger_out = [1]*30

dlp.defsequence(images, color, exposure, trigger_in, dark_time, trigger_out, 0)
dlp.startsequence()
