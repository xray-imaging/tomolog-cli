import os
import h5py

import numpy as np

from tomolog_cli import logging
from tomolog_cli import utils

__author__ = "Viktor Nikitin"
__copyright__ = "Copyright (c) 2022, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['read_scan_info', 'read_raw', 'read_recon']


log = logging.getLogger(__name__)

def read_scan_info(args):
    '''Read acquistion parameters
    '''
    _, meta = utils.read_hdf_meta(args.file_name, add_shape=True)

    return meta


def read_raw(args):
    '''Read raw data from an hdf5 file
    '''
    proj = []
    with h5py.File(args.file_name) as fid:
        proj.append(fid['exchange/data'][0][:])
        log.info('Adding CT projection')
        try:
            proj.append(fid['exchange/data2'][0][:])
            log.info('Adding microCT projection')
        except:            
            pass

    return proj


def read_recon(args, meta):
    '''Read reconstructed orho-slices
    '''

    data_size     = 'exchange_data'
    binning       = 'measurement_instrument_detector_binning_x'

    dims          = meta[data_size][0].replace("(", "").replace(")", "").split(',')
    width         = int(dims[2])
    height        = int(dims[1])
    binning       = int(meta[binning][0])

    recon = []

    try:
        basename = os.path.basename(args.file_name)[:-3]
        dirname = os.path.dirname(args.file_name)
        # shift from the middle
        shift = 0
        # read z slices
        # take size
        rec_prefix = 'r'
        if args.rec_type == 'rec':
            rec_prefix = 'recon'
        tmp = utils.read_tiff(
            f'{dirname}_{args.rec_type}/{basename}_rec/{rec_prefix}_00000.tiff').copy()
        binning = width//tmp.shape[0]
        w = width//binning
        h = height//binning

        if args.idz == -1:
            args.idz = int(h//2+shift)
            args.idy = int(w//2+shift)
            args.idx = int(w//2+shift)
        z = utils.read_tiff(
            f'{dirname}_{args.rec_type}/{basename}_rec/{rec_prefix}_{args.idz:05}.tiff').copy()
        # read x,y slices by lines
        y = np.zeros((h, w), dtype='float32')
        x = np.zeros((h, w), dtype='float32')
        for j in range(h):
            zz = utils.read_tiff(
                f'{dirname}_{args.rec_type}/{basename}_rec/{rec_prefix}_{j:05}.tiff')
            y[j, :] = zz[args.idy]
            x[j, :] = zz[:, args.idx]
        recon = [x,y,z]
        log.info('Adding reconstruction')
    except:
        log.warning('Skipping reconstruction')
    return recon



