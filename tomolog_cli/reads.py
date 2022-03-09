import os
import h5py
import numpy as np
import tifffile

from collections import OrderedDict, deque

from tomolog_cli import logging

PIPE = "│"
ELBOW = "└──"
TEE = "├──"
PIPE_PREFIX = "│   "
SPACE_PREFIX = "    "

log = logging.getLogger(__name__)

def read_scan_info(args):
    '''Read acquistion parameters and the first projection from an hdf5 file
    '''
    proj, meta = read_hdf_meta(args.file_name, add_shape=True)
    proj = []
    with h5py.File(args.file_name) as fid:
        proj.append(fid['exchange/data'][0][:])
        log.info('Adding nanoCT projection')
        try:
            proj.append(fid['exchange/data2'][0][:])
            log.info('Adding microCT projection')
        except:            
            log.warning('Skipping microCT projection')

    return proj, meta


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
        tmp = read_tiff(
            f'{dirname}_recgpu/{basename}_rec/r_00000.tiff').copy()
        params['binning'] = params['width']//tmp.shape[0]
        w = params['width']//params['binning']
        h = params['height']//params['binning']

        if args.idz == -1:
            args.idz = int(h//2+shift)
            args.idy = int(w//2+shift)
            args.idx = int(w//2+shift)
        idz = args.idz
        z = read_tiff(
            f'{dirname}_recgpu/{basename}_rec/r_{idz:05}.tiff').copy()
        # read x,y slices by lines
        y = np.zeros((h, w), dtype='float32')
        x = np.zeros((h, w), dtype='float32')
        for j in range(h):
            zz = read_tiff(
                f'{dirname}_recgpu/{basename}_rec/r_{j:05}.tiff')
            y[j, :] = zz[args.idy]
            x[j, :] = zz[:, args.idx]
        recon = [x,y,z]
        params['idx'] = args.idx
        params['idy'] = args.idy
        params['idz'] = args.idz
        log.info('Adding reconstruction')
    except:
        log.warning('Skipping reconstruction')
        
    return recon


def read_hdf_meta(fname, add_shape=True):
    """
    Get the tree view of a hdf/nxs file.

    Parameters
    ----------
    file_path : str
        Path to the file.
    add_shape : bool
        Including the shape of a dataset to the tree if True.

    Returns
    -------
    list of string
    """

    tree = deque()
    meta = {}

    with h5py.File(fname, 'r') as hdf_object:
        _extract_hdf(tree, meta, hdf_object, add_shape=add_shape)
    # for entry in tree:
    #     print(entry)
    return tree, meta


def _get_subgroups(hdf_object, key=None):
    """
    Supplementary method for building the tree view of a hdf5 file.
    Return the name of subgroups.
    """
    list_group = []
    if key is None:
        for group in hdf_object.keys():
            list_group.append(group)
        if len(list_group) == 1:
            key = list_group[0]
        else:
            key = ""
    else:
        if key in hdf_object:
            try:
                obj = hdf_object[key]
                if isinstance(obj, h5py.Group):
                    for group in hdf_object[key].keys():
                        list_group.append(group)
            except KeyError:
                pass
    if len(list_group) > 0:
        list_group = sorted(list_group)
    return list_group, key


def _add_branches(tree, meta, hdf_object, key, key1, index, last_index, prefix,
                  connector, level, add_shape):
    """
    Supplementary method for building the tree view of a hdf5 file.
    Add branches to the tree.
    """
    shape = None
    key_comb = key + "/" + key1
    if add_shape is True:
        if key_comb in hdf_object:
            try:
                obj = hdf_object[key_comb]
                if isinstance(obj, h5py.Dataset):
                    shape = str(obj.shape)
                    if obj.shape[0]==1:
                        s = obj.name.split('/')
                        name = "_".join(s)[1:]
                        # print(s)
                        # print(name)
                        value = obj[()][0]
                        attr = obj.attrs.get('units')
                        if attr != None:
                            attr = attr.decode('UTF-8')
                            # log.info(">>>>>> %s: %s %s" % (obj.name, value, attr))
                        if  (value.dtype.kind == 'S'):
                            value = value.decode(encoding="utf-8")
                            # log.info(">>>>>> %s: %s" % (obj.name, value))
                        meta.update( {name : [value, attr] } )
                    if obj.shape[0]>1:
                        s = obj.name.split('/')
                        name = "_".join(s)[1:]
                        meta.update( {name : [shape] } )
            except KeyError:
                shape = str("-> ???External-link???")
    if shape is not None:
        tree.append(f"{prefix}{connector} {key1} {shape}")
    else:
        tree.append(f"{prefix}{connector} {key1}")
    if index != last_index:
        prefix += PIPE_PREFIX
    else:
        prefix += SPACE_PREFIX
    _extract_hdf(tree, meta, hdf_object, prefix=prefix, key=key_comb,
                    level=level, add_shape=add_shape)


def _extract_hdf(tree, meta, hdf_object, prefix="", key=None, level=0,
                    add_shape=True):
    """
    Supplementary method for extracting from a generic hdf file the meta data 
    tree view and the 1D meta data values/units.
    Create the tree body and a meta dictionary 
    """
    entries, key = _get_subgroups(hdf_object, key)
    num_ent = len(entries)
    last_index = num_ent - 1
    level = level + 1
    if num_ent > 0:
        if last_index == 0:
            key = "" if level == 1 else key
            if num_ent > 1:
                connector = PIPE
            else:
                connector = ELBOW if level > 1 else ""
            _add_branches(tree, meta, hdf_object, key, entries[0], 0, 0, prefix,
                          connector, level, add_shape)
        else:
            for index, key1 in enumerate(entries):
                connector = ELBOW if index == last_index else TEE
                if index == 0:
                    tree.append(prefix + PIPE)
                _add_branches(tree, meta, hdf_object, key, key1, index, last_index,
                              prefix, connector, level, add_shape)

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

