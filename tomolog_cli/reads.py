
from tomolog_cli import logging
import dxchange
import os
import h5py
import numpy as np

log = logging.getLogger(__name__)

def read_scan_info(pars):
    '''Read acquistion parameters and the first projection from an hdf5 file
    '''
    proj = []
    with h5py.File(pars['file_name']) as fid:
        pars['energy'] = fid['measurement/instrument/monochromator/energy'][0]
        pars['height'] = fid['exchange/data'].shape[1]
        pars['width'] = fid['exchange/data'].shape[2]
        pars['pixelsize'] = float(
            fid['measurement/instrument/detector/pixel_size'][0])
        pars['cameraobjective'] = float(
            fid['measurement/instrument/detection_system/objective/camera_objective'][0])
        pars['resolution'] = float(
            fid['measurement/instrument/detection_system/objective/resolution'][0])
        pars['ntheta'] = len(fid['exchange/theta'])
        pars['exposure'] = fid['measurement/instrument/detector/exposure_time'][0]
        pars['step'] = fid['exchange/theta'][1]-fid['exchange/theta'][0]
        proj.append(fid['exchange/data'][0][:])
        log.info('Adding nanoCT projection')
        try:
            proj.append(fid['exchange/data2'][0][:])
            log.info('Adding microCT projection')
        except:            
            log.warning('Skipping microCT projection')
    
    return proj


def read_recon(pars):
    '''Read reconstructed orho-slices
    '''

    recon = []
    try:
        basename = os.path.basename(pars['file_name'])[:-3]
        dirname = os.path.dirname(pars['file_name'])
        # shift from the middle
        shift = 0
        # read z slices
        # take size
        tmp = dxchange.read_tiff(
            f'{dirname}_recgpu/{basename}_rec/r_00000.tiff').copy()
        pars['binning'] = pars['width']//tmp.shape[0]
        w = pars['width']//pars['binning']
        h = pars['height']//pars['binning']

        if pars['idz'] == -1:
            pars['idz'] = int(h//2+shift)
            pars['idy'] = int(w//2+shift)
            pars['idx'] = int(w//2+shift)
        idz = pars['idz']
        z = dxchange.read_tiff(
            f'{dirname}_recgpu/{basename}_rec/r_{idz:05}.tiff').copy()
        # read x,y slices by lines
        y = np.zeros((h, w), dtype='float32')
        x = np.zeros((h, w), dtype='float32')
        for j in range(h):
            zz = dxchange.read_tiff(
                f'{dirname}_recgpu/{basename}_rec/r_{j:05}.tiff')
            y[j, :] = zz[pars['idy']]
            x[j, :] = zz[:, pars['idx']]
        recon = [x,y,z]
        log.info('Adding reconstruction')
    except:
        log.warning('Skipping reconstruction')
        
    return recon
