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
import meta
import h5py
import numpy as np
import matplotlib
matplotlib.use('Agg')  # use non-GUI backend before importing pyplot
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
from mpl_toolkits.axes_grid1 import make_axes_locatable
import meta

from tomolog_cli import utils
from tomolog_cli import log
from tomolog_cli import TomoLog
from tomolog_cli import filebin

__author__ = "Viktor Nikitin,  Francesco De Carlo"
__copyright__ = "Copyright (c) 2022, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['TomoLog7BM', ]


class TomoLog7BM(TomoLog):
    '''
    Class to publish experiment meta data, tomography projection and reconstruction on a 
    google slide document.
    '''

    def __init__(self, args):
        super().__init__(args)
        # add here beamline dependent keys
        self.sample_y_key             = '/measurement/instrument/sample_motor_stack/setup/y'
        self.attenuator_1_description = '/measurement/instrument/attenuator_1/description' 
        self.attenuator_1_name        = '/measurement/instrument/attenuator_1/name' 
        self.attenuator_1_thickness   = '/measurement/instrument/attenuator_1/thickness' 
        self.attenuator_2             = '/measurement/instrument/attenuator_2/setup/filter_unit_text' 
        self.attenuator_3             = '/measurement/instrument/attenuator_3/setup/filter_unit_text' 
        self.propogation_distance_key = '/measurement/instrument/sample_motor_stack/detector_distance'

        self.binning_rec = -1
        self.mct_resolution = -1
        self.double_fov = False

    def publish_descr(self, presentation_id, page_id):
        descr = super().publish_descr(presentation_id, page_id)
        
        # add here beamline specific bullets
        descr += self.read_meta_item(
            "Attenuator 1: {self.meta[self.attenuator_1_name][0]} {self.meta[self.attenuator_1_thickness][0]}")
        descr += self.read_meta_item(
            "Attenuator 2: {self.meta[self.attenuator_2][0]}")
        descr += self.read_meta_item(
            "Attenuator 3: {self.meta[self.attenuator_3][0]}")
        descr += self.read_meta_item(
            "Sample Y: {self.meta[self.sample_y_key][0]:.02f} {self.meta[self.sample_y_key][1]}")
        descr += self.read_meta_item(
            "Propagation dist.: {self.meta[self.propogation_distance_key][0]:.02f} {self.meta[self.propogation_distance_key][1]}")

        descr = descr[:-1]
        self.google_slide.create_textbox_with_bullets(
            presentation_id, page_id, descr, 240, 120, 0, 18, 8, 0)

    def read_raw(self):
        log.info('Reading microCT projection')
        proj = []
        with h5py.File(self.args.file_name) as fid:
            if self.double_fov == True:
                log.warning('Data read: Handling the data set as a double FOV')
                image_0 = np.flip(fid['exchange/data'][0][:], axis=1)
                image_1 = fid['exchange/data'][-1][:]
                data = np.hstack((image_0, image_1))
            else:
                data = fid['exchange/data'][0][:]
            proj.append(data)
        return proj

    def read_recon(self):
        log.info('Read reconstruction')
        width = int(self.meta[self.width_key][0])
        height = int(self.meta[self.height_key][0])
        binning = int(self.meta[self.binning_key][0])
        recon = []
        coeff_rec = 1

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

            recon = [coeff_rec*x, coeff_rec*y, coeff_rec*z]

            self.binning_rec = binning_rec

            log.info('Adding reconstruction')
        except ZeroDivisionError:
            log.error(
                'Reconstructions for %s are larger than raw data image width. This is the case in a 0-360. Please use: --double-fov' % top)
            log.warning('Skipping reconstruction')
        except:
            log.warning('Skipping reconstruction')

        return recon

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

    def publish_proj(self, presentation_id, page_id, proj):
        # 7-bm datasets include only microCT data
        log.info('Publish microCT projection')
        self.plot_projection(proj[0], self.file_name_proj0)
        proj_url = filebin.upload(self.args, self.file_name_proj0)
        self.google_slide.create_image(
            presentation_id, page_id, proj_url, 170, 170, 0, 145)

        self.google_slide.create_textbox_with_text(
            presentation_id, page_id, 'Micro-CT projection', 90, 20, 50, 190, 8, 0)

    def publish_recon(self, presentation_id, page_id, recon):
        log.info('Publish reconstruction')
        if len(recon) == 3:
            # publish reconstructions
            self.plot_recon(recon, self.file_name_recon)
            recon_url = filebin.upload(self.args, self.file_name_recon)
            rec_line = self.read_rec_line()
            self.google_slide.create_image(
                presentation_id, page_id, recon_url, 370, 370, 130, 25)
            self.google_slide.create_textbox_with_text(
                presentation_id, page_id, 'Reconstruction', 90, 20, 270, 0, 10, 0)
            self.google_slide.create_textbox_with_text(
                presentation_id, page_id, rec_line, 1000, 20, 185, 391, 6, 0)