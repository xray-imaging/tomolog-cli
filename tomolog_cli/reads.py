import os
import h5py
import meta
import numpy as np

from tomolog_cli import log
from tomolog_cli import utils

__author__ = "Viktor Nikitin"
__copyright__ = "Copyright (c) 2022, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['read_scan_info', 'read_raw', 'read_recon']


def read_scan_info(args):
    '''Read acquistion parameters from an hdf5 file

    Parameters
    ----------
    args.file_name : string
        The raw data tomography hdf file name

    Returns
    -------
    meta_data
        Dictionary containing all hdf file stored experiment meta_data data
    '''
    _, meta_data = meta.read_hdf(args.file_name, add_shape=True)

    return meta_data


def read_raw(args):
    '''Read raw data from an hdf5 file

    Parameters
    ----------
    args.file_name : string
        The raw data tomography hdf file name

    Returns
    -------
    proj
        list of ndarray(s) containing the first data set projection of 
        each data set stored in the hdf file. Usually proj contains only
        one image but in some nano CT measurement it may also contain 
        a micro CT measurement of the same sample

    '''
    proj = []
    with h5py.File(args.file_name) as fid:
        if args.double_fov == True:
            log.warning('Data read: Handling the data set as a double FOV')
            image_0 = np.flip(fid['exchange/data'][0][:], axis=1)
            image_1 = fid['exchange/data'][-1][:]
            data = np.hstack((image_0, image_1))
        else:
            data = fid['exchange/data'][0][:]
        proj.append(data)
        log.info('Reading CT projection')
        try:
            proj.append(fid['exchange/data2'][0][:])
            log.info('Reading microCT projection')
        except:            
            pass
        try:
            proj.append(fid['exchange/web_camera_frame'][:])
            log.info('Reading camera frame')
        except:            
            pass
    return proj


def read_recon(args, meta_data):
    '''Read reconstructed ortho-slices

    Parameters
    ----------
    args.file_name : string
        The raw data tomography hdf file name
    args.idx
        Id of x slice for reconstruction visualization
    args.idy
        Id of y slice for reconstruction visualization
    args.idz
        Id of z slice for reconstruction visualization
    meta_data
        Dictionary containing all hdf file stored experiment meta_data data    

    Returns
    -------
    recon : list
        List containing 3 orthogonal (x, y, z) slices through the sample
    binning_rec : int
        Binning factor calculated by comparing raw image width and recon size
    '''

    binning_key = '/measurement/instrument/detector/binning_x'
    width_key   = '/measurement/instrument/detector/roi/size_x'
    height_key  = '/measurement/instrument/detector/roi/size_y'

    width         = int(meta_data[width_key][0])
    height        = int(meta_data[height_key][0])
    binning       = int(meta_data[binning_key][0])

    recon = []
    binning_rec = -1
    coeff_rec = 1

    # check if inversion is needed for the phase-contrast imaging at 32id
    if 'measurement_instrument_phase_ring_setup_y' in meta_data.keys():
      phase_ring_y = float(meta_data['measurement_instrument_phase_ring_setup_y'][0])
      if abs(phase_ring_y) < 1e-2:
         coeff_rec = -1      
    try:
        basename = os.path.basename(args.file_name)[:-3]
        dirname = os.path.dirname(args.file_name)
        # set the correct prefix to find the reconstructions
        rec_prefix = 'recon'

        top = os.path.join(dirname+'_rec', basename+'_rec')
        tiff_file_list = sorted(list(filter(lambda x: x.endswith(('.tif', '.tiff')), os.listdir(top))))
        z_start = int(tiff_file_list[0].split('.')[0].split('_')[1])
        z_end   = int(tiff_file_list[-1].split('.')[0].split('_')[1]) + 1
        height = z_end-z_start
        fname_tmp = os.path.join(top, tiff_file_list[0])
        # take size
        tmp = utils.read_tiff(fname_tmp).copy()

        if args.double_fov == True:
            width = width * 2
            binning_rec = 1
        else:
            binning_rec = width//tmp.shape[0]

        w = width//binning_rec
        h = height
        if args.idz==-1:
            args.idz = int(h//2)
        if args.idy==-1:
            args.idy = int(w//2)
        if args.idx==-1:
            args.idx = int(w//2)
        
        z = utils.read_tiff(
            f'{dirname}_rec/{basename}_rec/{rec_prefix}_{args.idz:05}.tiff').copy()
        
        # read x,y slices by lines
        y = np.zeros((h, w), dtype='float32')
        x = np.zeros((h, w), dtype='float32')

        for j in range(z_start, z_end):
            zz = utils.read_tiff(
                f'{dirname}_rec/{basename}_rec/{rec_prefix}_{j:05}.tiff')
            y[j-z_start, :] = zz[args.idy]
            x[j-z_start, :] = zz[:, args.idx]

        recon = [coeff_rec*x,coeff_rec*y,coeff_rec*z]
        log.info('Adding reconstruction')
    except ZeroDivisionError:
       log.error('Reconstructions for %s are larger than raw data image width. This is the case in a 0-360. Please use: --double-fov' % top)
       log.warning('Skipping reconstruction')
    except:
       log.warning('Skipping reconstruction')

    return recon, binning_rec

def read_rec_line(args):
    '''Read the command line for reconstruction
    Returns
    -------
    line : str
        command line for reconstruction
    '''
    
    line = None
    try:
        basename = os.path.basename(args.file_name)[:-3]
        dirname = os.path.dirname(args.file_name)
        with open(f'{dirname}_rec/{basename}_rec/rec_line.txt','r') as fid:
            line = fid.readlines()[0]            
    except:
        log.warning('Skipping the command line for reconstruction')

    return line
