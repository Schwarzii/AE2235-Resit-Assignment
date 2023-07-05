import matplotlib.pyplot as plt
import numpy as np

pie_wedges = {'edgecolor': 'w', 'linewidth': 2}
percentage = '%1.2f%%'


def color(data_array, cmap='Set2'):
    color_map = plt.get_cmap(cmap)
    return color_map(np.arange(len(data_array)))
