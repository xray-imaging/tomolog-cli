import os
import json
import uuid
import dropbox
import pathlib

from epics import PV

from tomolog_cli import log
from tomolog_cli import plots
from tomolog_cli import reads
from tomolog_cli import auth

__author__ = "Viktor Nikitin"
__copyright__ = "Copyright (c) 2022, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['TomoLog',]

# tmp files to be created in dropbox
FILE_NAME_PROJ0  = 'projection_google0'
FILE_NAME_PROJ1  = 'projection_google1'
FILE_NAME_RECON = 'reconstruction_google.jpg'

DROPBOX_TOKEN   = os.path.join(str(pathlib.Path.home()), 'tokens', 'dropbox_token.json')
GOOGLE_TOKEN    = os.path.join(str(pathlib.Path.home()), 'tokens', 'google_token.json')

class TomoLog():
    def __init__(self):

        self.snippets  = auth.google(GOOGLE_TOKEN)
        self.dbx = auth.drop_box(DROPBOX_TOKEN)
        
        # hdf file key definitions
        self.full_file_name_key = 'measurement_sample_full_file_name'
        self.description_1_key  = 'measurement_sample_description_1'
        self.description_2_key  = 'measurement_sample_description_2'
        self.description_3_key  = 'measurement_sample_description_3'
        self.date_key           = 'process_acquisition_start_date'
        self.energy_key         = 'measurement_instrument_monochromator_energy'
        self.pixel_size_key     = 'measurement_instrument_detector_pixel_size'
        self.magnification_key  = 'measurement_instrument_detection_system_objective_camera_objective'
        self.resolution_key     = 'measurement_instrument_detection_system_objective_resolution'
        self.exposure_time_key  = 'measurement_instrument_detector_exposure_time'
        self.angle_step_key     = 'process_acquisition_rotation_rotation_step'
        self.num_angle_key      = 'process_acquisition_rotation_num_angles'
        self.data_size_key      = 'exchange_data'
        self.binning_key        = 'measurement_instrument_detector_binning_x'


    def run_log(self, args):

        if args.file_name is None:
            args.file_name = PV(args.PV_prefix.get(as_string=True))
        try:
            presentation_id = args.presentation_url.split('/')[-2]
        except AttributeError:
            log.error("Set --presentation-url to point to a valid Google slide location")
            exit()
        # Create a new Google slide
        page_id = str(uuid.uuid4())
        self.snippets.create_slide(presentation_id, page_id)
        

        meta = reads.read_scan_info(args)
        # print(meta)
        self.dims             = meta[self.data_size_key][0].replace("(", "").replace(")", "").split(',')
        self.width            = int(self.dims[2])
        self.height           = int(self.dims[1])
        self.resolution       = float(meta[self.resolution_key][0])
        self.resolution_units = str(meta[self.resolution_key][1])
        self.pixel_size       = float(meta[self.pixel_size_key][0])
        self.pixel_size_units = str(meta[self.pixel_size_key][1])
        self.magnification    = float(meta[self.magnification_key][0].replace("x", ""))
        self.binning          = int(meta[self.binning_key][0])

        # publish title
        full_file_name = meta[self.full_file_name_key][0]
        self.snippets.create_textbox_with_text(presentation_id, page_id, os.path.basename(
            full_file_name)[:-3], 50, 400, 0, 0, 18)
        dims          = meta[self.data_size_key][0].replace("(", "").replace(")", "").split(',')
        width         = int(dims[2])
        height        = int(dims[1])

        if meta[self.exposure_time_key][1] == None:
            log.warning('Exposure time units are missing assuming (s)')
            meta[self.exposure_time_key][1] = 's'
        print(meta[self.exposure_time_key][1])
        # publish scan info
        descr =  f"Particle description: {meta[self.description_1_key][0]} {meta[self.description_2_key][0]} {meta[self.description_3_key][0]}\n"
        descr += f"Scan date: {meta[self.date_key][0]}\n"
        descr += f"Scan energy: {meta[self.energy_key][0]} {meta[self.energy_key][1]}\n"
        descr += f"Pixel size: {meta[self.pixel_size_key][0]:.02f} {meta[self.pixel_size_key][1]}\n"
        descr += f"Lens magnification: {meta[self.magnification_key][0]}\n"
        descr += f"Resolution: {meta[self.resolution_key][0]:.02f} {meta[self.resolution_key][1]}\n"
        descr += f"Exposure time: {meta[self.exposure_time_key][0]:.02f} {meta[self.exposure_time_key][1]}\n"
        descr += f"Angle step: {meta[self.angle_step_key][0]:.03f} {meta[self.angle_step_key][1]}\n"
        descr += f"Number of angles: {meta[self.num_angle_key][0]}\n"
        descr += f"Projection size: {self.width} x {self.height}"
        self.snippets.create_textbox_with_bullets(
            presentation_id, page_id, descr, 240, 200, 0, 27, 8)

        # publish projection label(s)
        if(args.beamline == '32-id'):
            self.snippets.create_textbox_with_text(
                presentation_id, page_id, 'Nano-CT projection', 30, 100, 60, 255, 8)
            self.snippets.create_textbox_with_text(
                presentation_id, page_id, 'Micro-CT projection', 30, 100, 60, 375, 8)
        
        # read projection(s)
        proj = reads.read_raw(args)
 
        if(args.beamline == '32-id'):
            log.info('plotting nanoCT projection')
            # 32-id datasets may include both nanoCT and microCT data as proj[0] and proj[1] respectively
            fname = FILE_NAME_PROJ0+'.jpg'
            nct_resolution = self.resolution / 1000.
            plots.plot_projection(proj[0], fname, resolution=nct_resolution)
            self.publish_projection(fname, presentation_id, page_id, 0, 100)
            try:
                log.info('plotting microCT projection')
                fname = FILE_NAME_PROJ1+'.jpg'
                mct_resolution = self.pixel_size / self.magnification
                plots.plot_projection(proj[1], fname, resolution=mct_resolution)
                self.publish_projection(fname, presentation_id, page_id, 0, 225)
            except:
                log.warning('No microCT data available')
        else:
            fname = FILE_NAME_PROJ0+'.jpg'
            plots.plot_projection(proj[0], fname, resolution=self.resolution)
            self.publish_projection(fname, presentation_id, page_id, 0, 100)
        self.snippets.create_textbox_with_text(
            presentation_id, page_id, 'Reconstruction', 30, 150, 270, 0, 10)

        # read reconstructions
        recon = reads.read_recon(args, meta)    

        # publish reconstructions
        if len(recon) == 3:
            # prepare reconstruction
            if(args.beamline == '32-id'):
                self.resolution = self.resolution / 1000.

            plots.plot_recon(args, dims, recon, FILE_NAME_RECON, self.resolution, self.binning)
            with open(FILE_NAME_RECON, 'rb') as f:
                self.dbx.files_upload(f.read(), '/'+FILE_NAME_RECON, dropbox.files.WriteMode.overwrite)
            recon_url = self.dbx.files_get_temporary_link('/'+FILE_NAME_RECON).link            
            self.snippets.create_image(presentation_id, page_id, recon_url, 370, 370, 130, 30)

        # publish other labels
        self.snippets.create_textbox_with_text(
            presentation_id, page_id, 'Other info/screenshots', 30, 230, 480, 0, 10)

    def publish_projection(self, fname, presentation_id, page_id, posx, posy):
        with open(fname, 'rb') as f:
            self.dbx.files_upload(f.read(), '/'+fname, dropbox.files.WriteMode.overwrite)
            proj_url = self.dbx.files_get_temporary_link('/'+fname).link
            self.snippets.create_image(presentation_id, page_id, proj_url, 210, 210, posx, posy)


