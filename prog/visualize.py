import matplotlib.pyplot as plt
import numpy as np
from prog.nfp import get_clipping_limits

def plot_bin(abin, bin_size, ax=None):
    """Utility function to plot one bin"""
    if ax is None:
        plt.figure(figsize=(5, 5))
        ax = fig.add_subplot(aspect='equal')
        
    for _, pg, translation in abin:
        translated_pg = pg + translation
        closed_pg = np.append(translated_pg, translated_pg[[0]], axis=0)
        ax.fill(closed_pg[:, 0], closed_pg[:, 1])
    bin_rectangle = get_clipping_limits(bin_size, ((0, 0), ))
    closed_bin_rectangle = np.append(bin_rectangle, bin_rectangle[[0]], axis=0)
    ax.plot(closed_bin_rectangle[:, 0], closed_bin_rectangle[:, 1])
    
    if ax is None:
        plt.show()
    
def plot_packing(packing, size=3):
    """Utility function to plot a packing (see class Packing) made of one or several bins"""
    nrows = len(packing.bins) // 4 + 1
    ncols = min(4, len(packing.bins))
    fig = plt.figure(figsize=(size * ncols, 2 * size * nrows))
    gs = fig.add_gridspec(nrows=nrows, ncols=ncols, wspace=0.1, hspace=0.1)

    for i, abin in enumerate(packing.bins):
        ax = fig.add_subplot(gs[i // 4, i % 4], aspect='equal')
        ax.axis('off')
        plot_bin(abin, packing.bin_size, ax)

    plt.show()
