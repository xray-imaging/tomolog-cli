# #########################################################################
# Copyright (c) 2022, UChicago Argonne, LLC. All rights reserved.         #
#                                                                         #
# Copyright 2022. UChicago Argonne, LLC. This software was produced       #
# under U.S. Government contract DE-AC02-06CH11357 for Argonne National   #
# Laboratory (ANL), which is operated by UChicago Argonne, LLC for the    #
# U.S. Department of Energy. The U.S. Government has rights to use,       #
# reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR    #
# UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR        #
# ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is     #
# modified to produce derivative works, such modified software should     #
# be clearly marked, so as not to confuse it with the version available   #
# from ANL.                                                               #
#                                                                         #
# Additionally, redistribution and use in source and binary forms, with   #
# or without modification, are permitted provided that the following      #
# conditions are met:                                                     #
#                                                                         #
#     * Redistributions of source code must retain the above copyright    #
#       notice, this list of conditions and the following disclaimer.     #
#                                                                         #
#     * Redistributions in binary form must reproduce the above copyright #
#       notice, this list of conditions and the following disclaimer in   #
#       the documentation and/or other materials provided with the        #
#       distribution.                                                     #
#                                                                         #
#     * Neither the name of UChicago Argonne, LLC, Argonne National       #
#       Laboratory, ANL, the U.S. Government, nor the names of its        #
#       contributors may be used to endorse or promote products derived   #
#       from this software without specific prior written permission.     #
#                                                                         #
# THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS     #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS       #
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago     #
# Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,        #
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,    #
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;        #
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER        #
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT      #
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN       #
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE         #
# POSSIBILITY OF SUCH DAMAGE.                                             #
# #########################################################################

import os
import h5py
import datetime
import tifffile

import numpy as np

from collections import OrderedDict, deque
from tomolog_cli import log

def find_min_max(data,th=0.003):
    """Find min and max values according to histogram"""

    h, e = np.histogram(data[:], 1000)
    stend = np.where(h > np.max(h)*th)
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
        arr = tifffile.imread(fname)
    except IOError:
        log.error('No such file or directory: %s', fname)
        return False

    return arr


def read_tiff_chunk(x,y, fname,idx,idy, k, lchunk):
    """Read a chunk of data from tiff"""
    log.info(k,st,end)
    st = k*lchunk
    end = min((k+1)*lchunk,rec.shape[0])
    zz = dxchange.read_tiff_stack(fname,ind=range(st,end))
    y[st:end, :] = zz[dy]
    x[st:end, :] = zz[:, idx]


def read_tiff_many(fname,z_start,z_end,idx,idy,nproc=8):
    t = time.time()        
    d = dxchange.read_tiff(fname)
    n = d.shape[-1]
    nz = z_end- z_start
    
    # read x,y slices by lines
    y = np.zeros((nz, n), dtype='float32')
    x = np.zeros((nz, n), dtype='float32')

    lchunk = int(np.ceil(nz/nproc))
    procs = []
    for k in range(nproc):
        read_proc = threading.Thread(
            target=read_tiff_chunk, args=(x, y, fname, idx,idy, k, lchunk))
        procs.append(read_proc)
        read_proc.start()
    for proc in procs:
        proc.join()
    log.info(time.time()-t)
    