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

    def publish_proj(self, presentation_id, page_id, proj):
        # 7-bm datasets include only microCT data
        self.plot_projection(proj[0], self.file_name_proj0)
        proj_url = filebin.upload(self.args, self.file_name_proj0)
        log.info('Publish microCT projection')
        self.google_slide.create_image(
            presentation_id, page_id, proj_url, 120, 120, 30, 180)

        self.google_slide.create_textbox_with_text(
            presentation_id, page_id, 'Micro-CT projection', 90, 20, 50, 180, 8, 0)


