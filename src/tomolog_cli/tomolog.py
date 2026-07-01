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
import uuid
import pathlib
import datetime
import yaml
import h5py
import matplotlib.pyplot as plt
import numpy as np

from matplotlib_scalebar.scalebar import ScaleBar
from mpl_toolkits.axes_grid1 import make_axes_locatable
from threading import Thread
from ast import literal_eval

import meta

from tomolog_cli import log
from tomolog_cli import auth
from tomolog_cli import utils
from tomolog_cli import cloud

__author__ = "Viktor Nikitin,  Francesco De Carlo"
__copyright__ = "Copyright (c) 2022, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['TomoLog', ]

# Temporary local files to be uploaded to the url service. Google API retrieves images by url before publishing on slides
FILE_NAME_PROJ  = 'projection'
FILE_NAME_RECON = 'reconstruction'

# Credentials of the Google service that will create the slides
# For details see: https://tomologcli.readthedocs.io/en/latest/source/install.html#google
GOOGLE_TOKEN = os.path.join(str(pathlib.Path.home()), 'tokens', 'google_token.json')

class TomoLog():
    '''
    Class to publish experiment meta data, tomography projection and reconstruction on a 
    google slide document.
    '''

    def __init__(self, args):
        self.google_slide = auth.google_slide(args, GOOGLE_TOKEN)

        self.args = args

        self.file_name_proj0 = FILE_NAME_PROJ  + '.jpg'
        self.file_name_recon = FILE_NAME_RECON + '.jpg'

        # add here beamline independent keys
        self.full_file_name_key = '/measurement/sample/file/full_name'
        self.beamline_key       = '/measurement/instrument/source/beamline'
        self.exposure_time_key  = '/measurement/instrument/detector/exposure_time'
        self.pixel_size_key     = '/measurement/instrument/detector/pixel_size'
        self.magnification_key  = '/measurement/instrument/detection_system/objective/magnification'
        self.resolution_key     = '/measurement/instrument/detection_system/objective/resolution'
        self.width_key          = '/measurement/instrument/detector/array_size_x'
        self.height_key         = '/measurement/instrument/detector/array_size_y'
        self.binning_key        = '/measurement/instrument/detector/binning_x'
        self.instrument_key     = '/measurement/instrument/name'
        self.sample_in_x_key    = '/process/acquisition/flat_fields/sample/in_x'
        self.angle_step_key     = '/process/acquisition/rotation/step'
        self.num_angle_key      = '/process/acquisition/rotation/num_angles'
        self.rotation_start_key = '/process/acquisition/rotation/start'
        self.date_key           = '/process/acquisition/start_date'
        self.proposal_key       = '/measurement/sample/experiment/proposal'
        self.user_name_key      = '/measurement/sample/experimenter/name'
        self.user_id_key        = '/measurement/sample/experimenter/user_id'

    def publish_descr(self, presentation_id, page_id):
        # add here beamline independent bullets
        descr = self.read_meta_item(
            "File name: {os.path.basename(self.meta[self.full_file_name_key][0])}")
        descr += self.read_meta_item(
            "Beamline: {self.meta[self.beamline_key][0]} {self.meta[self.instrument_key][0]}")
        descr += self.read_meta_item(
            "Scan date: {self.meta[self.date_key][0]}")
        descr += self.read_meta_item(
            "Exposure time: {self.meta[self.exposure_time_key][0]:.05f} {self.meta[self.exposure_time_key][1]}")
        descr += self.read_meta_item(
            "Camera pixel size: {self.meta[self.pixel_size_key][0]:.02f} {self.meta[self.pixel_size_key][1]}")
        descr += self.read_meta_item(
            "Lens magnification: {self.meta[self.magnification_key][0]}")
        descr += self.read_meta_item(
            "Projection pixel size: {self.meta[self.resolution_key][0]:.02f} {self.meta[self.resolution_key][1]}")
        descr += self.read_meta_item(
            "Angle step: {self.meta[self.angle_step_key][0]:.03f} {self.meta[self.angle_step_key][1]}")
        self.rotation_end = self.meta[self.rotation_start_key][0] + (self.meta[self.num_angle_key][0] * self.meta[self.angle_step_key][0]) - self.meta[self.angle_step_key][0]
        descr += self.read_meta_item(
            "Number of angles: {self.meta[self.num_angle_key][0]} ({self.meta[self.rotation_start_key][0]:.02f} - {self.rotation_end:.02f})")
        descr += self.read_meta_item(
            "Projection size: {int(self.meta[self.width_key][0])} x {int(self.meta[self.height_key][0])}")
        if (self.args.beamline == "None"):
            descr = descr[:-1]
            self.google_slide.create_textbox_with_bullets(
                presentation_id, page_id, descr, 240, 120, 0, 18, 8, 0)
        
        return descr

    def publish_note(self, presentation_id, page_id):
        note = self.args.note
        if self.args.note != None:
            log.info('Publish note')
            self.google_slide.create_textbox_with_text(
                presentation_id, page_id, note, 300,100, 10, 320, 10, 0
                )
        else:
            pass

    def _rec_dir(self):
        """Directory holding reconstructions for the current raw file.

        Defaults to '<dirname_of_raw>_rec' (the tomocupy convention).
        Overridden by --analysis-path when the recons live elsewhere
        (e.g. /gdata/.../analysis/ while raw data is at /gdata/.../data/).
        """
        if self.args.analysis_path is not None:
            return str(self.args.analysis_path)
        return os.path.dirname(self.args.file_name) + '_rec'

    def _recon_layout(self):
        """Resolve the reconstruction layout — 'h5', 'tiff', or None.

        If --save-format is 'auto' (default), inspect the filesystem and pick:
          - 'h5'   when <rec_dir>/<base>_rec.h5 exists (h5/h5nolinks output)
          - 'tiff' when <rec_dir>/<base>_rec/ directory exists
          - None   when neither is present (caller logs a warning)
        If --save-format is set explicitly, honor it. 'h5' and 'h5nolinks'
        both map to the single-h5-file reader (h5py reads them identically).
        """
        basename = os.path.basename(self.args.file_name)[:-3]
        rec_dir = self._rec_dir()
        h5_path = f'{rec_dir}/{basename}_rec.h5'
        tiff_dir = f'{rec_dir}/{basename}_rec'

        if self.args.save_format == 'auto':
            if os.path.exists(h5_path):
                log.info(f'Detected reconstruction layout: h5 ({h5_path})')
                return 'h5'
            if os.path.isdir(tiff_dir):
                log.info(f'Detected reconstruction layout: tiff ({tiff_dir})')
                return 'tiff'
            log.warning(f'No reconstruction found at {h5_path} or {tiff_dir}')
            return None
        if self.args.save_format in ('h5', 'h5nolinks'):
            return 'h5'
        return 'tiff'

    def read_rec_line(self):
        line = ''
        try:
            log.info('Publish reconstruction command line')
            basename = os.path.basename(self.args.file_name)[:-3]
            rec_dir = self._rec_dir()
            layout = self._recon_layout()
            if layout == 'h5':
                txt_path = f'{rec_dir}/{basename}_rec_line.txt'
                h5_path = f'{rec_dir}/{basename}_rec.h5'
                if os.path.exists(txt_path):
                    with open(txt_path, 'r') as fid:
                        line = fid.readlines()[0]
                else:
                    # Newer tomocupy runs no longer write the sidecar txt for h5
                    # output: the command line is stored as an attribute of
                    # /exchange/data. Fall back to reading it from the h5 file.
                    with h5py.File(h5_path, 'r') as fid:
                        cmd = fid['exchange/data'].attrs.get('command', '')
                        if isinstance(cmd, bytes):
                            cmd = cmd.decode('utf-8')
                        elif hasattr(cmd, 'decode'):
                            cmd = cmd.decode('utf-8')
                        line = str(cmd)
            else:
                path = f'{rec_dir}/{basename}_rec/rec_line.txt'
                with open(path, 'r') as fid:
                    line = fid.readlines()[0]
        except:
            log.warning('Skipping the command line for reconstruction')
            line = ''
        return line

    def run_log(self):
        # read meta, calculate resolutions
        mp = meta.read_meta.Hdf5MetadataReader(self.args.file_name)
        self.meta = mp.readMetadata()
        mp.close()

        if (self.meta[self.sample_in_x_key][0] != 0) and self.args.beamline == '2-bm':
            self.double_fov = True
            log.warning('Sample in x is off center: %s. Handling the data set as a double FOV' %
                        self.meta[self.sample_in_x_key][0])

        if (self.meta[self.sample_in_x_key][0] != 0) and self.args.beamline == '7-bm':
            log.warning('Sample in x is off center: %s. Assume rotation axis was not zeroed' %
                        self.meta[self.sample_in_x_key][0])

        # Option to overwrite the values of the pixel size and resolution stored h5 if missing or incorrect
        if self.args.pixel_size!=-1:
            self.meta[self.pixel_size_key][0]  = self.args.pixel_size
        if self.args.magnification!=-1:
            self.meta[self.magnification_key][0]  = f'{self.args.magnification}x'
        if self.args.magnification!=-1 and self.args.pixel_size!=-1:
            self.meta[self.resolution_key][0]  = self.args.pixel_size/self.args.magnification
        
        self.mct_resolution = float(self.meta[self.pixel_size_key][0]) / float(self.meta[self.magnification_key][0].lower().replace("x", ""))

        self.setup_resolutions()

        presentation_id, page_id = self.init_slide()
        self.save_history(self.args.presentation_url)
        self.publish_descr(presentation_id, page_id)
        self.publish_note(presentation_id, page_id)
        proj = self.read_raw()
        self.publish_proj(presentation_id, page_id, proj)
        recon = self.read_recon()
        #print(recon)
        self.publish_recon(presentation_id, page_id, recon)
        cloud.cleanup(self.args)

    def setup_resolutions(self):
        pass

    def init_slide(self):
        # create a slide and publish file name
        file_name = os.path.basename(self.args.file_name)
        try:
            presentation_id = self.args.presentation_url.split('/')[-2]
        except AttributeError:
            log.error(
                "Set --presentation-url to point to a valid Google slide location")
            exit()
        # Create a new Google slide
        page_id = str(uuid.uuid4())
        self.google_slide.create_slide(presentation_id, page_id)
        self.google_slide.create_textbox_with_text(presentation_id, page_id, os.path.basename(
            self.args.file_name)[:-3], 400, 50, 0, 0, 13, 1)
        return presentation_id, page_id

    def save_history(self, presentation_url):
        history_file = pathlib.Path.home() / '.tomolog'
        entry = {
            'date':             datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'presentation_url': str(presentation_url),
            'gup':              str(self.meta.get(self.proposal_key,  [None])[0]),
            'username':         str(self.meta.get(self.user_name_key, [None])[0]),
            'user_id':          str(self.meta.get(self.user_id_key,   [None])[0]),
            'beamline':         str(self.meta.get(self.beamline_key,  [None])[0]),
            'file':             str(self.args.file_name),
        }
        history = []
        if history_file.exists():
            try:
                with open(history_file) as f:
                    history = yaml.safe_load(f) or []
            except yaml.YAMLError:
                log.warning('Could not parse existing %s, starting fresh' % history_file)
                history = []
        history.append(entry)
        with open(history_file, 'w') as f:
            yaml.safe_dump(history, f, default_flow_style=False, allow_unicode=True)
        log.info('History saved to %s' % history_file)

    def read_meta_item(self, template):
        try:
            str = eval(f"f'{template}'")+"\n"
        except:
            log.warning(f'meta item missing: {template}')
            str = ""
        return str

    def read_raw(self):
        log.info('Reading CT projection')
        proj = []
        with h5py.File(self.args.file_name) as fid:
            data = fid['exchange/data'][0][:]
            proj.append(data)
        return proj

    def read_recon(self):
        log.info('Read reconstruction')
        width = int(self.meta[self.width_key][0])
        height = int(self.meta[self.height_key][0])
        binning = int(self.meta[self.binning_key][0])
        recon = []

        layout = self._recon_layout()
        if layout is None:
            return recon

        if layout == 'h5':
            basename = os.path.basename(self.args.file_name)[:-3]
            fname = f'{self._rec_dir()}/{basename}_rec.h5'
            try:
                with h5py.File(fname, 'r') as fid:
                    data = fid['exchange/data']
                    h, w = data.shape[:2]
                    if self.args.idz == -1:
                        self.args.idz = int(h//2)
                    if self.args.idy == -1:
                        self.args.idy = int(w//2)
                    if self.args.idx == -1:
                        self.args.idx = int(w//2)
                    if self.double_fov == True:
                        binning_rec = np.log2(width//(w//2))
                    else:
                        binning_rec = np.log2(width//(w))
                    x = data[:, :, self.args.idx]
                    y = data[:, self.args.idy]
                    z = data[self.args.idz]
                recon = [x, y, z]
                self.binning_rec = binning_rec
            except FileNotFoundError:
                log.error(f'Reconstruction h5 file missing: {fname}')
                log.warning('Skipping reconstruction')
            except KeyError:
                log.error(f'/exchange/data not found in {fname} (h5sino is not supported for slicing)')
                log.warning('Skipping reconstruction')
        else:
            try:
                basename = os.path.basename(self.args.file_name)[:-3]
                rec_dir = self._rec_dir()
                # set the correct prefix to find the reconstructions
                rec_prefix = 'recon'

                top = os.path.join(rec_dir, basename+'_rec')
                tiff_file_list = sorted(
                    list(filter(lambda x: x.endswith(('.tif', '.tiff')), os.listdir(top))))
                z_start = int(tiff_file_list[0].split('.')[0].split('_')[1])
                z_end = int(tiff_file_list[-1].split('.')[0].split('_')[1]) + 1
                height = z_end-z_start
                fname_tmp = os.path.join(top, tiff_file_list[0])
                # take size
                tmp = utils.read_tiff(fname_tmp).copy()

                if self.double_fov == True:
                    width = width * 2
                    binning_rec = 1
                else:
                    binning_rec = width//tmp.shape[0]

                w = width//binning_rec
                h = height
                if self.args.idz == -1:
                    self.args.idz = int(h//2)
                if self.args.idy == -1:
                    self.args.idy = int(w//2)+int(w//32)
                if self.args.idx == -1:
                    self.args.idx = int(w//2)-int(w//32)

                z = utils.read_tiff(
                    f'{rec_dir}/{basename}_rec/{rec_prefix}_{self.args.idz:05}.tiff').copy()
                
                # read x,y slices by lines
                y = np.zeros((h, w), dtype='float32')
                x = np.zeros((h, w), dtype='float32')

                nthreads = 8
                threads = []
                lchunk = int(np.ceil((z_end-z_start)/nthreads))
                lchunk = np.minimum(lchunk, np.int32(z_end-z_start-np.arange(nthreads)*lchunk))  # chunk sizes
                for k in range(nthreads):
                    read_proc = Thread(target=utils.read_tiff_part, args=(self.args, f'{rec_dir}/{basename}_rec/{rec_prefix}', x, y, z_start, k*lchunk[0], lchunk[k]))
                    threads.append(read_proc)
                    read_proc.start()
                for th in threads:
                    th.join()
                
                recon = [x, y, z]

                self.binning_rec = binning_rec
            except ZeroDivisionError:
                log.error('Reconstructions for %s are larger than raw data image width. This is the case in a 0-360. Please use: --double-fov' % top)
                log.warning('Skipping reconstruction')
            except FileNotFoundError:
                log.error('Reconstructions for %s are missing. Please run the recontruction.' % top)
                log.warning('Skipping reconstruction')
            except:
                log.warning('Skipping reconstruction')
        
        return recon


    def plot_projection(self, proj, fname):
        log.info('Plot microCT projection')
        # auto-adjust colorbar values according to a histogram
        mmin, mmax = utils.find_min_max(proj)
        proj[proj > mmax] = mmax
        proj[proj < mmin] = mmin

        # plot
        fig = plt.figure(constrained_layout=True, figsize=(6, 4))
        ax = fig.add_subplot()
        im = ax.imshow(proj, cmap='gray')
        # Create scale bar
        scalebar = ScaleBar(self.mct_resolution, "um", length_fraction=0.25)
        ax.add_artist(scalebar)
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        plt.colorbar(im, cax=cax, format='%.1e')
        plt.savefig(fname, bbox_inches='tight', pad_inches=0, dpi=300)
        plt.cla()
        plt.close(fig)

    def plot_recon(self, recon, fname):
        log.info('Plot reconstruction')
        fig = plt.figure(constrained_layout=True, figsize=(14, 12))
        grid = fig.add_gridspec(3, 3, height_ratios=[1, 1, 1])
        slices = ['x', 'y', 'z']
        # autoadjust colorbar values according to a histogram

        if self.args.min == self.args.max:
            self.args.min, self.args.max = utils.find_min_max(
                np.concatenate(recon))

        sl = [self.args.idx, self.args.idy, self.args.idz]
        tmp = literal_eval(self.args.zoom)
        if not isinstance(tmp,list):
            tmp = [tmp]
        
        zooms = tmp
        log.info('Zooms selected %s' % zooms)
        for j in range(3):
            for k in range(3):
                [s0,s1] = recon[k].shape
                recon0 = recon[k][s0//2-s0//2//zooms[j]:s0//2+s0//2//zooms[j],s1//2-s1//2//zooms[j]:s1//2+s1//2//zooms[j]]
                
                recon0[0, 0] = self.args.max
                recon0[0, 1] = self.args.min
                recon0[recon0 > self.args.max] = self.args.max
                recon0[recon0 < self.args.min] = self.args.min
                ax = fig.add_subplot(grid[3*k+j])
                im = ax.imshow(recon0, cmap='gray')
                # Create scale bar
                scalebar = ScaleBar(self.mct_resolution *
                                    self.binning_rec, "um", length_fraction=0.25)
                ax.add_artist(scalebar)
                divider = make_axes_locatable(ax)
                cax = divider.append_axes("right", size="5%", pad=0.1)
                cb = plt.colorbar(im, cax=cax)
                if j<2:
                    cb.remove()
                if j==0:
                    ax.set_ylabel(f'slice {slices[k]}={sl[k]}', fontsize=18)
        plt.savefig(fname, bbox_inches='tight', pad_inches=0, dpi=150)
        plt.cla()
        plt.close(fig)

    def publish_proj(self, presentation_id, page_id, proj, resolution=1):
        self.google_slide.create_textbox_with_text(
            presentation_id, page_id, 'Projection', 90, 20, 50, 163, 8, 0)        
        self.plot_projection(proj[0], self.file_name_proj0)
        proj_url = cloud.upload(self.args, self.file_name_proj0)
        log.info('Publish projection')
        self.google_slide.create_image(
            presentation_id, page_id, proj_url, 150, 150, 10, 157)

    def publish_recon(self, presentation_id, page_id, recon):
        if len(recon) == 3:
            # publish reconstructions
            self.google_slide.create_textbox_with_text(
                presentation_id, page_id, f'Reconstruction                                   Zoom {self.args.zoom}', 430, 14, 270, 2, 10, 0)
            self.plot_recon(recon, self.file_name_recon)
            recon_url = cloud.upload(self.args, self.file_name_recon)
            log.info('Publish reconstruction')
            self.google_slide.create_image(
                presentation_id, page_id, recon_url, 470, 336, 230, 21)

            rec_line = self.read_rec_line()
            self.google_slide.create_textbox_with_text(
                presentation_id, page_id, rec_line, 710, 43, 5, 360, 6, 0)

