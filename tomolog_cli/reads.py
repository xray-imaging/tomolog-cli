import os
import h5py

import numpy as np

from tomolog_cli import logging
from tomolog_cli import utils

log = logging.getLogger(__name__)

def read_scan_info(args):
    '''Read acquistion parameters
    '''
    proj, meta = utils.read_hdf_meta(args.file_name, add_shape=True)
    proj = []
    with h5py.File(args.file_name) as fid:
        proj.append(fid['exchange/data'][0][:])
        log.info('Adding nanoCT projection')
        try:
            proj.append(fid['exchange/data2'][0][:])
            log.info('Adding microCT projection')
        except:            
            log.warning('Skipping microCT projection')

    return meta


def read_raw(args):
    '''Read raw data from an hdf5 file
    '''
    proj, meta = utils.read_hdf_meta(args.file_name, add_shape=True)
    proj = []
    with h5py.File(args.file_name) as fid:
        proj.append(fid['exchange/data'][0][:])
        log.info('Adding nanoCT projection')
        try:
            proj.append(fid['exchange/data2'][0][:])
            log.info('Adding microCT projection')
        except:            
            log.warning('Skipping microCT projection')

    return proj


def read_recon(args, params):
    '''Read reconstructed orho-slices
    '''

    recon = []
    try:
        basename = os.path.basename(args.file_name)[:-3]
        dirname = os.path.dirname(args.file_name)
        # shift from the middle
        shift = 0
        # read z slices
        # take size
        tmp = utils.read_tiff(
            f'{dirname}_recgpu/{basename}_rec/r_00000.tiff').copy()
        params['binning'] = params['width']//tmp.shape[0]
        w = params['width']//params['binning']
        h = params['height']//params['binning']

        if args.idz == -1:
            args.idz = int(h//2+shift)
            args.idy = int(w//2+shift)
            args.idx = int(w//2+shift)
        z = utils.read_tiff(
            f'{dirname}_recgpu/{basename}_rec/r_{args.idz:05}.tiff').copy()
        # read x,y slices by lines
        y = np.zeros((h, w), dtype='float32')
        x = np.zeros((h, w), dtype='float32')
        for j in range(h):
            zz = utils.read_tiff(
                f'{dirname}_recgpu/{basename}_rec/r_{j:05}.tiff')
            y[j, :] = zz[args.idy]
            x[j, :] = zz[:, args.idx]
        recon = [x,y,z]
        log.info('Adding reconstruction')
    except:
        log.warning('Skipping reconstruction')
        
    return recon



