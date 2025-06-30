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
import meta
import h5py
import numpy as np
import matplotlib
matplotlib.use('Agg')  # use non-GUI backend before importing pyplot
import matplotlib.pyplot as plt

from matplotlib_scalebar.scalebar import ScaleBar
from mpl_toolkits.axes_grid1 import make_axes_locatable

import requests

from tomolog_cli import utils
from tomolog_cli import log
from tomolog_cli import TomoLog
from tomolog_cli import filebin

__author__ = "Viktor Nikitin,  Francesco De Carlo"
__copyright__ = "Copyright (c) 2022, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['TomoLog2BM', ]

FILE_NAME_WEBCAM = 'web_cam.jpg'


class TomoLog2BM(TomoLog):
    '''
    Class to publish experiment meta data, tomography projection and reconstruction on a 
    google slide document.
    '''

    def __init__(self, args):
        super().__init__(args)
        # add here beamline specific keys
        self.energy_key               = '/measurement/instrument/monochromator/energy'
        self.sample_y_key             = '/measurement/instrument/sample_motor_stack/setup/y'
        self.sample_pitch_angle_key   = '/measurement/instrument/sample_motor_stack/setup/pitch'
        self.propogation_distance_key = '/measurement/instrument/detector_motor_stack/setup/z'
        self.load_key                 = '/measurement/sample/environment/load_cell/load_raw'
        self.load_key_calc            = '/measurement/sample/environment/load_cell/load_calc'
        self.eurotherm1_key           = '/measurement/sample/environment/eurotherm1/thermocouple'
        self.eurotherm2_key           = '/measurement/sample/environment/eurotherm2/thermocouple'

        self.binning_rec = -1
        self.mct_resolution = -1
        self.double_fov = False
        self.file_name_webcam = FILE_NAME_WEBCAM

    def publish_descr(self, presentation_id, page_id):
        descr = super().publish_descr(presentation_id, page_id)
        
        # add here beamline specific bullets
        descr += self.read_meta_item(
            "Scan energy: {self.meta[self.energy_key][0]} {self.meta[self.energy_key][1]}")
        descr += self.read_meta_item(
            "Sample Y: {self.meta[self.sample_y_key][0]:.02f} {self.meta[self.sample_y_key][1]}")
        descr += self.read_meta_item(
            "Propagation dist.: {self.meta[self.propogation_distance_key][0]:.02f} {self.meta[self.propogation_distance_key][1]}")
        # descr += self.read_meta_item(
        #     "Eurotherm 1: {self.meta[self.eurotherm1_key][0]:.05f} {self.meta[self.eurotherm1_key][1]}")
        # descr += self.read_meta_item(
        #     "Eurotherm 2: {self.meta[self.eurotherm2_key][0]:.05f} {self.meta[self.eurotherm2_key][1]}")

        # descr += self.read_meta_item(
        #     "Load Raw: {self.meta[self.load_key][0]:.05f} {self.meta[self.load_key][1]}")
        # descr += self.read_meta_item(
        #     "Load: {self.meta[self.load_key_calc][0]:.05f} {self.meta[self.load_key_calc][1]}")

        pitch_angle = self.read_meta_item("{self.meta[self.sample_pitch_angle_key][0]:.02f}")
        if pitch_angle is not '':
            pitch_angle = float(pitch_angle)
            if pitch_angle != 0:
                pitch_angle = -pitch_angle
                pitch_angle_units = self.read_meta_item("{self.meta[self.sample_pitch_angle_key][1]}")
                descr += "Pitch angle: " + str(pitch_angle) + pitch_angle_units

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
            try:
                proj.append(fid['exchange/web_camera_frame'][:])
                log.info('Reading camera frame')
            except:
                pass
        return proj

    def publish_proj(self, presentation_id, page_id, proj):
        # 2-BM datasets may include both microCT data and a web camera image
        self.plot_projection(proj[0], self.file_name_proj0)
        proj_url = filebin.upload(self.args, self.file_name_proj0)
        log.info('Publish microCT projection')
        self.google_slide.create_image(
            presentation_id, page_id, proj_url, 120, 120, 30, 180)

        self.google_slide.create_textbox_with_text(
            presentation_id, page_id, 'Micro-CT projection', 90, 20, 50, 170, 8, 0)
        try:
            log.info('Plotting web camera image')
            plt.imshow(np.fliplr(proj[1].reshape(-1,3)).reshape(proj[1].shape))
            plt.axis('off')
            plt.savefig(self.file_name_webcam,dpi=300)
            proj_url = filebin.upload(self.args, self.file_name_webcam)
            log.info('Publish web camera image')
            self.google_slide.create_image(
                presentation_id, page_id, proj_url, 170, 170, 0, 270)

            self.google_slide.create_textbox_with_text(
                presentation_id, page_id, 'Frame from the IP camera in the hutch', 160, 20, 10, 290, 8, 0)
        except:
            log.warning('No frame from the IP camera')
