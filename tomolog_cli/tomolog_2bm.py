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
import meta
import h5py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
from mpl_toolkits.axes_grid1 import make_axes_locatable
import meta
from threading import Thread

from tomolog_cli import utils
from tomolog_cli import log
from tomolog_cli import TomoLog

__author__ = "Viktor Nikitin,  Francesco De Carlo"
__copyright__ = "Copyright (c) 2022, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['TomoLog2BM', ]

FILE_NAME_PROJ1 = 'projection_google1.jpg'


class TomoLog2BM(TomoLog):
    '''
    Class to publish experiment meta data, tomography projection and reconstruction on a 
    google slide document.
    '''

    def __init__(self, args):
        super().__init__(args)
        # add here beamline dependent keys
        self.energy_key               = '/measurement/instrument/monochromator/energy'
        self.sample_in_x_key          = '/process/acquisition/flat_fields/sample/in_x'
        self.sample_y_key             = '/measurement/instrument/sample_motor_stack/setup/y'
        self.sample_pitch_angle_key   = '/measurement/instrument/sample_motor_stack/setup/pitch'
        self.propogation_distance_key = '/measurement/instrument/detector_motor_stack/setup/z'
        self.load_key                 = '/measurement/sample/environment/load_raw'
        self.load_key_calc            = '/measurement/sample/environment/load_calc'

        self.binning_rec = -1
        self.mct_resolution = -1
        self.double_fov = False
        self.file_name_proj1 = FILE_NAME_PROJ1

    def publish_descr(self, presentation_id, page_id):
        descr = super().publish_descr(presentation_id, page_id)
        
        # add here beamline dependent bullets
        descr += self.read_meta_item(
            "Scan energy: {self.meta[self.energy_key][0]} {self.meta[self.energy_key][1]}")
        descr += self.read_meta_item(
            "Sample Y: {self.meta[self.sample_y_key][0]:.02f} {self.meta[self.sample_y_key][1]}")
        descr += self.read_meta_item(
            "Propagation dist.: {self.meta[self.propogation_distance_key][0]:.02f} {self.meta[self.propogation_distance_key][1]}")
        descr += self.read_meta_item(
            "Load Raw: {self.meta[self.load_key][0]:.05f} {self.meta[self.load_key][1]}")
        descr += self.read_meta_item(
            "Load: {self.meta[self.load_key_calc][0]:.05f} {self.meta[self.load_key_calc][1]}")

        pitch_angle = self.read_meta_item("{self.meta[self.sample_pitch_angle_key][0]:.02f}")
        if pitch_angle is not '':
            pitch_angle = float(pitch_angle)
            if pitch_angle != 0:
                pitch_angle = -pitch_angle
                pitch_angle_units = self.read_meta_item("{self.meta[self.sample_pitch_angle_key][1]}")
                descr += "Pitch angle: " + str(pitch_angle) + pitch_angle_units

        descr = descr[:-1]
        self.google.create_textbox_with_bullets(
            presentation_id, page_id, descr, 240, 120, 0, 18, 8, 0)

    def run_log(self):
        # read meta, calculate resolutions
        _, self.meta = meta.read_hdf(self.args.file_name, add_shape=True)
        if self.args.pixel_size!=-1:
            self.meta[self.pixel_size_key][0]  = self.args.pixel_size
        if self.args.magnification!=-1:
            self.meta[self.magnification_key][0]  = f'{self.args.magnification}x'
        if self.args.magnification!=-1 and self.args.pixel_size!=-1:
            self.meta[self.resolution_key][0]  = self.args.pixel_size/self.args.magnification
        self.mct_resolution = float(self.meta[self.pixel_size_key][0]) / float(self.meta[self.magnification_key][0].replace("x", ""))
        if (self.meta[self.sample_in_x_key][0] != 0):
            self.double_fov = True
            log.warning('Sample in x is off center: %s. Handling the data set as a double FOV' %
                        self.meta[self.sample_in_x_key][0])
        
        presentation_id, page_id = self.init_slide()
        self.publish_descr(presentation_id, page_id)
        proj = self.read_raw()
        recon = self.read_recon()
        self.publish_proj(presentation_id, page_id, proj)
        self.publish_recon(presentation_id, page_id, recon)

    def read_raw(self):
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
            log.info('Reading CT projection')
            try:
                proj.append(fid['exchange/web_camera_frame'][:])
                log.info('Reading camera frame')
            except:
                pass
        return proj

    def read_tiff_part(self,fname,x,y,z_start,z0_start,lchunk):
        for j in range(z0_start,z0_start+lchunk):
            id = z_start+j
            zz = utils.read_tiff(f'{fname}_{id:05}.tiff')
            y[j, :] = zz[self.args.idy]
            x[j, :] = zz[:, self.args.idx]

    def read_recon(self):

        width = int(self.meta[self.width_key][0])
        height = int(self.meta[self.height_key][0])
        binning = int(self.meta[self.binning_key][0])
        recon = []
        coeff_rec = 1

        if 0==0:
        # try:
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

            nthreads = 8
            threads = []
            lchunk = int(np.ceil((z_end-z_start)/nthreads))
            lchunk = np.minimum(lchunk, np.int32(z_end-z_start-np.arange(nthreads)*lchunk))  # chunk sizes
            for k in range(nthreads):
                read_proc = Thread(target=self.read_tiff_part, args=(f'{dirname}_rec/{basename}_rec/{rec_prefix}', x, y, z_start, k*lchunk[0], lchunk[k]))
                threads.append(read_proc)
                read_proc.start()
            for th in threads:
                th.join()

            recon = [x, y, z]

            # for j in range(z_start, z_end):
            #     zz = utils.read_tiff(
            #         f'{dirname}_rec/{basename}_rec/{rec_prefix}_{j:05}.tiff')
            #     y[j-z_start, :] = zz[self.args.idy]
            #     x[j-z_start, :] = zz[:, self.args.idx]

            # recon = [coeff_rec*x, coeff_rec*y, coeff_rec*z]

            self.binning_rec = binning_rec

            log.info('Adding reconstruction')
        # except ZeroDivisionError:
        #     log.error(
        #         'Reconstructions for %s are larger than raw data image width. This is the case in a 0-360. Please use: --double-fov' % top)
        #     log.warning('Skipping reconstruction')
        # except:
        #     log.warning('Skipping reconstruction')

        return recon

    def read_rec_line(self):
        line = None
        try:
            basename = os.path.basename(self.args.file_name)[:-3]
            dirname = os.path.dirname(self.args.file_name)
            with open(f'{dirname}_rec/{basename}_rec/rec_line.txt', 'r') as fid:
                line = fid.readlines()[0]
        except:
            log.warning('Skipping the command line for reconstruction')
            line = ''
        return line

    def publish_proj(self, presentation_id, page_id, proj):
        # 32-id datasets may include both nanoCT and microCT data as proj[0] and proj[1] respectively
        log.info('Micro Tomography Instrument')
        log.info('Plotting microCT projection')
        self.plot_projection(proj[0], self.file_name_proj0)
        proj_url = self.dbx.upload(self.file_name_proj0)
        self.google.create_image(
            presentation_id, page_id, proj_url, 170, 170, 0, 145)

        self.google.create_textbox_with_text(
            presentation_id, page_id, 'Micro-CT projection', 90, 20, 50, 155, 8, 0)
        try:
            log.info('Plotting frame the IP camera')
            plt.imshow(np.fliplr(proj[1].reshape(-1,3)).reshape(proj[1].shape))
            plt.axis('off')
            plt.savefig(self.file_name_proj1,dpi=300)
            proj_url = self.dbx.upload(self.file_name_proj1)
            self.google.create_image(
                presentation_id, page_id, proj_url, 170, 170, 0, 270)

            self.google.create_textbox_with_text(
                presentation_id, page_id, 'Frame from the IP camera in the hutch', 160, 20, 10, 290, 8, 0)
        except:
            log.warning('No frame from the IP camera')

    def publish_recon(self, presentation_id, page_id, recon):
        if len(recon) == 3:
            # publish reconstructions
            self.plot_recon(recon, self.file_name_recon)
            recon_url = self.dbx.upload(self.file_name_recon)
            rec_line = self.read_rec_line()
            self.google.create_image(
                presentation_id, page_id, recon_url, 470, 400, 230, 5)
            self.google.create_textbox_with_text(
                presentation_id, page_id, 'Reconstruction                                   Zoom 2x                                          Zoom 4x', 590, 20, 270, 0, 10, 0)
            self.google.create_textbox_with_text(
                presentation_id, page_id, rec_line, 1000, 20, 185, 391, 6, 0)

    def plot_projection(self, proj, fname):

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
        # plt.show()
        # save
        plt.savefig(fname, bbox_inches='tight', pad_inches=0, dpi=300)
        plt.cla()
        plt.close(fig)

    def plot_recon(self, recon, fname):
        fig = plt.figure(constrained_layout=True, figsize=(14, 12))
        grid = fig.add_gridspec(3, 3, height_ratios=[1, 1, 1])
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
            ax = fig.add_subplot(grid[3*k])
            im = ax.imshow(recon[k], cmap='gray')
            # Create scale bar
            scalebar = ScaleBar(self.mct_resolution *
                                self.binning_rec, "um", length_fraction=0.25)
            ax.add_artist(scalebar)
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size="5%", pad=0.1)
            cb = plt.colorbar(im, cax=cax)
            cb.remove()
            ax.set_ylabel(f'slice {slices[k]}={sl[k]}', fontsize=18)
        
        
        for k in range(3):
            [s0,s1] = recon[k].shape
            recon[k] = recon[k][s0//4:3*s0//4,s1//4:3*s1//4]
            recon[k][0, 0] = self.args.max
            recon[k][0, 1] = self.args.min
            recon[k][recon[k] > self.args.max] = self.args.max
            recon[k][recon[k] < self.args.min] = self.args.min
            ax = fig.add_subplot(grid[3*k+1])
            im = ax.imshow(recon[k], cmap='gray')
            # Create scale bar
            scalebar = ScaleBar(self.mct_resolution *
                                self.binning_rec, "um", length_fraction=0.25)
            ax.add_artist(scalebar)
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size="5%", pad=0.1)
            cb = plt.colorbar(im, cax=cax)
            cb.remove()
            # ax.set_ylabel(f'slice {slices[k]}={sl[k]}', fontsize=14)
        for k in range(3):
            [s0,s1] = recon[k].shape
            recon[k] = recon[k][s0//4:3*s0//4,s1//4:3*s1//4]
            recon[k][0, 0] = self.args.max
            recon[k][0, 1] = self.args.min
            recon[k][recon[k] > self.args.max] = self.args.max
            recon[k][recon[k] < self.args.min] = self.args.min
            ax = fig.add_subplot(grid[3*k+2])
            im = ax.imshow(recon[k], cmap='gray')
            # Create scale bar
            scalebar = ScaleBar(self.mct_resolution *
                                self.binning_rec, "um", length_fraction=0.25)
            ax.add_artist(scalebar)
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size="5%", pad=0.1)
            plt.colorbar(im, cax=cax)
        # save
        plt.savefig(fname, bbox_inches='tight', pad_inches=0, dpi=150)
        plt.cla()
        plt.close(fig)
