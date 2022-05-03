import os
import h5py
import datetime
import tifffile

import numpy as np
import pandas as pd

from collections import OrderedDict, deque
from tomolog_cli import log

def find_min_max(data, scale):
    """Find min and max values according to histogram"""

    h, e = np.histogram(data[:], 1000)
    stend = np.where(h > np.max(h)*scale)
    st = stend[0][0]
    end = stend[0][-1]
    mmin = e[st]
    mmax = e[end+1]
    return mmin, mmax

def read_tiff(fname):
    """
    Read data from tiff file.
    Parameters
    ----------
    fname : str
        String defining the path of file or file name.

    Returns
    -------
    ndarray
        Output 2D image.
    """

    try:
        arr = tifffile.imread(fname, out='memmap')
    except IOError:
        log.error('No such file or directory: %s', fname)
        return False

    return arr

