import os
import h5py
import datetime
import tifffile

import numpy as np
import pandas as pd

from collections import OrderedDict, deque
from tomolog_cli import log

PIPE = "│"
ELBOW = "└──"
TEE = "├──"
PIPE_PREFIX = "│   "
SPACE_PREFIX = "    "


def find_min_max(data, scale):
    """Find min and max values according to histogram"""

    h, e = np.histogram(data[:], 1000)
    stend = np.where(h > np.max(h)*scale)
    st = stend[0][0]
    end = stend[0][-1]
    mmin = e[st]
    mmax = e[end+1]
    return mmin, mmax

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

    try:
    # if 0==0:
        with h5py.File(fname, 'r') as hdf_object:
            _extract_hdf(tree, meta, hdf_object, add_shape=add_shape)
        # for entry in tree:
        #     print(entry)
    except:
        log.error('Unable to open file: %s', fname)
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


def create_rst_file(args):
    
    meta, year_month, pi_name = extract_dx_meta(args)

    decorator = '='
    if os.path.isdir(args.doc_dir):
        log_fname = os.path.join(args.doc_dir, 'log_' + year_month + '.rst')

    with open(log_fname, 'a') as f:
        if f.tell() == 0:
            # a new file or the file was empty
            f.write(add_header(year_month))
            f.write(add_title(pi_name))
        else:
            #  file existed, appending
            f.write(add_title(pi_name))
        f.write('\n')        
        f.write(meta)        
        f.write('\n\n')        
    log.warning('Please copy/paste the content of %s in your rst docs file' % (log_fname))

def extract_dx_meta(args):

    list_to_extract = ('measurement_sample_full_file_name',
                    'measurement_sample_description_1',
                    'measurement_sample_description_2',
                    'measurement_sample_description_3',
                    'process_acquisition_start_date',
                    'measurement_instrument_monochromator_energy',
                    'measurement_instrument_detector_pixel_size',
                    'measurement_instrument_detection_system_objective_camera_objective',
                    'measurement_instrument_detection_system_objective_resolution',
                    'measurement_instrument_detector_exposure_time',
                    'process_acquisition_rotation_rotation_step',
                    'process_acquisition_rotation_num_angles',
                    'exchange_data',
                    'measurement_instrument_detector_binning_x',
                    'measurement_instrument_source_beamline',
                    'measurement_instrument_instrument_name'
                    'measurement_instrument_monochromator_energy', 
                    'measurement_sample_experimenter_email',
                    'measurement_instrument_sample_motor_stack_setup_sample_x', 
                    'measurement_instrument_sample_motor_stack_setup_sample_y'
                    )

    # set pandas display
    pd.options.display.max_rows = 999
    year_month = 'unknown'
    pi_name    = 'unknown'
    fname      = args.file_name

    if os.path.isfile(fname): 
        meta_dict, year_month, pi_name = extract_dict(fname, list_to_extract)
        # print (meta_dict, year_month, pi_name)
    elif os.path.isdir(fname):
        # Add a trailing slash if missing
        top = os.path.join(fname, '')
        # Set the file name that will store the rotation axis positions.
        h5_file_list = list(filter(lambda x: x.endswith(('.h5', '.hdf')), os.listdir(top)))
        h5_file_list.sort()
        meta_dict = {}
        file_counter=0
        for fname in h5_file_list:
            h5fname = top + fname
            sub_dict, year_month, pi_name = extract_dict(h5fname, list_to_extract, index=file_counter)
            meta_dict.update(sub_dict)
            file_counter+=1
        if year_month == 'unknown':
            log.error('No valid HDF5 file(s) fund in the directory %s' % top)
            log.warning('Make sure to use the --h5-name H5_NAME  option to select  the hdf5 file or directory containing multiple hdf5 files')
            return None
           
    else:
        log.error('No valid HDF5 file(s) fund')
        return None

    df = pd.DataFrame.from_dict(meta_dict, orient='index', columns=('value', 'unit'))
    return df.to_markdown(tablefmt='grid'), year_month, pi_name

def extract_dict(fname, list_to_extract, index=0):

    tree, meta = read_hdf_meta(fname)

    start_date     = 'process_acquisition_start_date'
    experimenter   = 'measurement_sample_experimenter_experimenter_name'
    full_file_name = 'measurement_sample_full_file_name'

    try: 
        dt = datetime.datetime.strptime(meta[start_date][0], "%Y-%m-%dT%H:%M:%S%z")
        year_month = str(dt.year) + '-' + '{:02d}'.format(dt.month)
    except ValueError:
        log.error("The start date information is missing from the hdf file %s. Error (2020-01)." % fname)
        year_month = '2020-01'
    except TypeError:
        log.error("The start date information is missing from the hdf file %s. Error (2020-02)." % fname)
        year_month = '2020-02'
    try:
        pi_name = meta[experimenter][0]
    except KeyError:
        log.error("The experimenter name is missing from the hdf file %s." % fname)
        pi_name = 'Unknown'
    try:    
        # compact full_file_name to file name only as original data collection directory may have changed
        meta[full_file_name][0] = os.path.basename(meta[full_file_name][0])
    except KeyError:
        log.error("The full file name is missing from the hdf file %s." % fname)

    sub_dict = {(('%3.3d' % index) +'_' + k):v for k, v in meta.items() if k in list_to_extract}

    return sub_dict, year_month, pi_name


def add_header(label):

    header = add_decorator(label) + '\n' + label + '\n' + add_decorator(label) + '\n\n'

    return header


def add_title(label):

    title = label + '\n' + add_decorator(label, decorator='-') + '\n\n' 

    return title


def add_decorator(label, decorator='='):
    
    return decorator.replace(decorator, decorator*len(label))
