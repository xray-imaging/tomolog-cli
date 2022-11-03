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
import json
import uuid
import pathlib
import h5py
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
import meta

from tomolog_cli import log
from tomolog_cli import auth
from tomolog_cli import utils


__author__ = "Viktor Nikitin,  Francesco De Carlo"
__copyright__ = "Copyright (c) 2022, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['TomoLog', ]

# tmp files to be created in dropbox
FILE_NAME_PROJ_BASE  = 'projection_google'
FILE_NAME_RECON_BASE = 'reconstruction_google'

DROPBOX_TOKEN = os.path.join(
    str(pathlib.Path.home()), 'tokens', 'dropbox_token.json')
GOOGLE_TOKEN = os.path.join(
    str(pathlib.Path.home()), 'tokens', 'google_token.json')


class TomoLog():
    '''
    Class to publish experiment meta data, tomography projection and reconstruction on a 
    google slide document.
    '''

    def __init__(self, args):
        self.google = auth.google(GOOGLE_TOKEN)
        self.dbx = auth.drop_box(DROPBOX_TOKEN)
        self.args = args

        self.file_name_proj0 = FILE_NAME_PROJ_BASE + str(args.queue) + '.jpg'
        self.file_name_recon = FILE_NAME_RECON_BASE + str(args.queue) + '.jpg'

        # add here beamline independent keys
        self.full_file_name_key = '/measurement/sample/file/full_name'
        self.beamline_key       = '/measurement/instrument/source/beamline'
        self.date_key           = '/process/acquisition/start_date'
        self.exposure_time_key  = '/measurement/instrument/detector/exposure_time'
        self.pixel_size_key     = '/measurement/instrument/detector/pixel_size'
        self.magnification_key  = '/measurement/instrument/detection_system/objective/magnification'
        self.resolution_key     = '/measurement/instrument/detection_system/objective/resolution'
        self.angle_step_key     = '/process/acquisition/rotation/step'
        self.num_angle_key      = '/process/acquisition/rotation/num_angles'
        self.rotation_start_key = '/process/acquisition/rotation/start'
        self.width_key          = '/measurement/instrument/detector/array_size_x'
        self.height_key         = '/measurement/instrument/detector/array_size_y'
        self.binning_key        = '/measurement/instrument/detector/binning_x'
        self.instrument_key     = '/measurement/instrument/name'

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
            self.google.create_textbox_with_bullets(
                presentation_id, page_id, descr, 240, 120, 0, 18, 8, 0)
        
        return descr

    def run_log(self):
        _, self.meta = meta.read_hdf(self.args.file_name, add_shape=True)
        if self.args.pixel_size!=-1:
            self.meta[self.pixel_size_key][0]  = self.args.pixel_size
        if self.args.magnification!=-1:
            self.meta[self.magnification_key][0]  = f'{self.args.magnification}x'
        if self.args.magnification!=-1 and self.args.pixel_size!=-1:
            self.meta[self.resolution_key][0]  = self.args.pixel_size/self.args.magnification
        
        presentation_id, page_id = self.init_slide()
        self.publish_descr(presentation_id, page_id)
        proj = self.read_raw()
        recon, _ = self.read_recon()
        self.publish_proj(presentation_id, page_id, proj)
        self.publish_recon(presentation_id, page_id, recon)

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
        self.google.create_slide(presentation_id, page_id)
        self.google.create_textbox_with_text(presentation_id, page_id, os.path.basename(
            self.args.file_name)[:-3], 400, 50, 0, 0, 13, 1)
        # publish other labels
        # self.google.create_textbox_with_text(
            # presentation_id, page_id, 'Other info/screenshots', 120, 20, 480, 0, 10, 0)
        return presentation_id, page_id

    def read_meta_item(self, template):
        try:
            str = eval(f"f'{template}'")+"\n"
        except:
            log.warning(f'meta item missing: {template}')
            str = ""
        return str

    def read_raw(self):
        proj = []
        with h5py.File(self.args.file_name) as fid:
            data = fid['exchange/data'][0][:]
            proj.append(data)
        return proj

    def read_recon(self):
        recon = []
        binning_rec = -1
        try:
            basename = os.path.basename(self.args.file_name)[:-3]
            dirname = os.path.dirname(self.args.file_name)
            # set the correct prefix to find the reconstructions
            rec_prefix = 'recon'
            top = os.path.join(dirname+'_rec', basename+'_rec')
            tiff_file_list = sorted(
                list(filter(lambda x: x.endswith(('.tif', '.tiff')), os.listdir(top))))
            z_start = int(tiff_file_list[0].split('.')[0].split('_')[1])
            z_end = int(tiff_file_list[-1].split('.')[0].split('_')[1]) + 1
            height = z_end-z_start
            fname_tmp = os.path.join(top, tiff_file_list[0])
            # take size
            tmp = utils.read_tiff(fname_tmp).copy()

            w = tmp.shape[0]
            h = height
            if self.args.idz == -1:
                self.args.idz = int(h//2)
            if self.args.idy == -1:
                self.args.idy = int(w//2)
            if self.args.idx == -1:
                self.args.idx = int(w//2)

            z = utils.read_tiff(
                f'{dirname}_rec/{basename}_rec/{rec_prefix}_{self.args.idz:05}.tiff').copy()

            # read x,y slices by lines
            y = np.zeros((h, w), dtype='float32')
            x = np.zeros((h, w), dtype='float32')

            for j in range(z_start, z_end):
                zz = utils.read_tiff(
                    f'{dirname}_rec/{basename}_rec/{rec_prefix}_{j:05}.tiff')
                y[j-z_start, :] = zz[self.args.idy]
                x[j-z_start, :] = zz[:, self.args.idx]

            recon = [x, y, z]
            log.info('Adding reconstruction')
        except ZeroDivisionError:
            log.error(
                'Reconstructions for %s are larger than raw data image width.')
            log.warning('Skipping reconstruction')
        except:
            log.warning('Skipping reconstruction')

        return recon, binning_rec

    def publish_proj(self, presentation_id, page_id, proj, resolution=1):
        log.info('Plotting projection')
        self.plot_projection(proj[0], self.file_name_proj0)
        proj_url = self.dbx.upload(self.file_name_proj0)
        self.google.create_image(
            presentation_id, page_id, proj_url, 150, 150, 10, 157)

        self.google.create_textbox_with_text(
            presentation_id, page_id, 'Projection', 90, 20, 50, 163, 8, 0)

    def publish_recon(self, presentation_id, page_id, recon, resolution=1):
        if len(recon) == 3:
            self.plot_recon(recon, self.file_name_recon)
            recon_url = self.dbx.upload(self.file_name_recon)
            self.google.create_image(
                presentation_id, page_id, recon_url, 370, 370, 130, 25)
            self.google.create_textbox_with_text(
                presentation_id, page_id, 'Reconstruction', 90, 20, 270, 0, 10, 0)

    def plot_projection(self, proj, fname):
        # auto-adjust colorbar values according to a histogram
        mmin, mmax = utils.find_min_max(proj)
        proj[proj > mmax] = mmax
        proj[proj < mmin] = mmin

        # plot
        fig = plt.figure(constrained_layout=True, figsize=(6, 4))
        ax = fig.add_subplot()
        im = ax.imshow(proj, cmap='gray')
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        plt.colorbar(im, cax=cax)
        plt.savefig(fname, bbox_inches='tight', pad_inches=0, dpi=300)
        plt.cla()
        plt.close(fig)

    def plot_recon(self, recon, fname):
        fig = plt.figure(constrained_layout=True, figsize=(6, 12))
        grid = fig.add_gridspec(3, 1, height_ratios=[1, 1, 1])
        slices = ['x', 'y', 'z']
        # autoadjust colorbar values according to a histogram

        if self.args.min == self.args.max:
            self.args.min, self.args.max = utils.find_min_max(
                np.concatenate(recon))

        sl = [self.args.idx, self.args.idy, self.args.idz]
        for k in range(3):
            recon[k][0, 0] = self.args.max
            recon[k][0, 1] = self.args.min
            recon[k][recon[k] > self.args.max] = self.args.max
            recon[k][recon[k] < self.args.min] = self.args.min
            ax = fig.add_subplot(grid[k])
            im = ax.imshow(recon[k], cmap='gray')
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size="5%", pad=0.1)
            plt.colorbar(im, cax=cax)
            ax.set_ylabel(f'slice {slices[k]}={sl[k]}', fontsize=14)
        plt.savefig(fname, bbox_inches='tight', pad_inches=0, dpi=300)
        plt.cla()
        plt.close(fig)
