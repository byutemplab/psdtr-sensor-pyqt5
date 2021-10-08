import numpy as np
import matplotlib.pyplot as plt

# Create map datatipe
# idx: point number (0, 1, 2, ...)
# pos: start of the sequence -> 0
#      end of the sequence -> 1
map_dt = np.dtype([('idx', '<i4'), ('pos', '<i1')])

# Fill empty map
map = np.zeros((5, 5), dtype=map_dt)
map['idx'] = map['idx'] - 1

print(map)
map[0, 0]['idx'] = 0
map[0, 0]['pos'] = 0
map[4, 4]['idx'] = 0
map[4, 4]['pos'] = 1

print(map)


def CreatePointsPatternArray(map, num_measures, point_diameter=20, point_shape="circle"):
    sequence_map_dt = np.dtype([('idx', '<i4'), ('seq', '<i4')])
    sequence_map = np.zeros((2, 2), dtype=sequence_map_dt)

    return 0


def MapToBinary(map):
    binary_map = map['pos']
    print(binary_map)
    plt.imshow(binary_map)
    plt.show()
