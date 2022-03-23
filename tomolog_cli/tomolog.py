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
    '''
    Class to publish experiment meta data, tomography projection and reconstruction on a 
    google slide document.
    '''
    def __init__(self):

        self.snippets  = auth.google(GOOGLE_TOKEN)
        self.dbx = auth.drop_box(DROPBOX_TOKEN)
        
        # hdf file key definitions
        self.full_file_name_key  = 'measurement_sample_full_file_name'
        self.description_1_key   = 'measurement_sample_description_1'
        self.description_2_key   = 'measurement_sample_description_2'
        self.description_3_key   = 'measurement_sample_description_3'
        self.date_key            = 'process_acquisition_start_date'
        self.energy_key          = 'measurement_instrument_monochromator_energy'
        self.pixel_size_key      = 'measurement_instrument_detector_pixel_size'
        self.magnification_key   = 'measurement_instrument_detection_system_objective_camera_objective'
        self.resolution_key      = 'measurement_instrument_detection_system_objective_resolution'
        self.exposure_time_key   = 'measurement_instrument_detector_exposure_time'
        self.rotation_start_key  = 'process_acquisition_rotation_rotation_start'
        self.angle_step_key      = 'process_acquisition_rotation_rotation_step'
        self.num_angle_key       = 'process_acquisition_rotation_num_angles'
        self.width_key           = 'measurement_instrument_detector_dimension_x'
        self.height_key          = 'measurement_instrument_detector_dimension_y'
        self.binning_key         = 'measurement_instrument_detector_binning_x'
        self.beamline_key        = 'measurement_instrument_source_beamline'
        self.instrument_key      = 'measurement_instrument_instrument_name'
        self.camera_distance_key = 'measurement_instrument_camera_motor_stack_setup_camera_distance'

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
        # publish title
        try:
            instrument_name = meta[self.instrument_key][0]
            log.info('Transmission X-Ray Microscope Instrument')
        except KeyError:
            log.error('Corrupted file: missing instrument name')
            log.error('or File locked by another program')
            return
        
        try:
            full_file_name = meta[self.full_file_name_key][0]
            # print(full_file_name)
            self.snippets.create_textbox_with_text(presentation_id, page_id, os.path.basename(
                full_file_name)[:-3], 400, 50, 0, 0, 13, 0)
        except TypeError:
            file_name =  os.path.basename(args.file_name)
            self.snippets.create_textbox_with_text(presentation_id, page_id, file_name, 400, 50, 0, 0, 13, 1)
            # print('red')  ### temp for 2021-10 Cooley TXM
        except KeyError:
            self.snippets.create_textbox_with_text(presentation_id, page_id, str(args.file_name), 400, 50, 0, 0, 13, 1)
            self.snippets.create_textbox_with_text(presentation_id, page_id, 'Unable to open file (truncated file)', 90, 20, 350, 0, 10, 1)
            # print('red')  ### temp for 2021-10 Cooley TXM
            return

        try:
            meta[self.magnification_key][0].replace("x", "")
            fontcolor = 0
        except:
            log.error('Objective magnification was not stored [%s, %s] for dataset: %s' % (meta[self.magnification_key][0], meta[self.magnification_key][1], full_file_name))
            log.error('Using --magnification parameter: %s' % args.magnification)
            log.error('Using --pixel-size parameter: %f' % args.pixel_size)
            meta[self.pixel_size_key][0] = args.pixel_size
            meta[self.pixel_size_key][1] ='um'
            meta[self.magnification_key][0] = args.magnification
            meta[self.resolution_key][0] = args.pixel_size / float(meta[self.magnification_key][0].replace("x", ""))
            log.warning('Calculated resolution: %s' % meta[self.resolution_key][0])
            meta[self.resolution_key][1] = 'um'
            fontcolor = 1

        self.width            = int(meta[self.width_key][0])
        self.height           = int(meta[self.height_key][0])
        # meta[self.resolution_key][0] = 0.69 ### temp for 2021-10 Cooley 2-BM
        # meta[self.resolution_key][0] = 42.4 ### temp for 2021-10 Cooley TXM
        self.resolution       = float(meta[self.resolution_key][0])
        # meta[self.resolution_key][1] = 'nm'  ### temp for 2021-10 Cooley TXM
        self.resolution_units = str(meta[self.resolution_key][1])
        # meta[self.pixel_size_key][0] = 3.45 ### temp for 2021-10 Cooley TXM
        self.pixel_size       = float(meta[self.pixel_size_key][0])
        # meta[self.pixel_size_key][1] = 'um' ### temp for 2021-10 Cooley TXM
        self.pixel_size_units = str(meta[self.pixel_size_key][1])
        # meta[self.magnification_key][0] = '5x' ### temp for 2021-10 Cooley TXM
        self.magnification    = float(meta[self.magnification_key][0].replace("x", ""))
        # meta[self.binning_key][0] = '1' ### temp for 2021-10 Cooley TXM
        self.binning          = int(meta[self.binning_key][0])
        if meta[self.exposure_time_key][1] == None:
            log.warning('Exposure time units are missing assuming (s)')
            meta[self.exposure_time_key][1] = 's'

        # meta[self.exposure_time_key][0] = 2.0 ### temp for 2021-10 Cooley TXM
        # publish scan info
        descr  =  f"Beamline: {meta[self.beamline_key][0]} {meta[self.instrument_key][0]}\n"
        descr +=  f"Particle description: {meta[self.description_1_key][0]} {meta[self.description_2_key][0]} {meta[self.description_3_key][0]}\n"
        descr +=  f"Scan date: {meta[self.date_key][0]}\n"
        descr +=  f"Scan energy: {meta[self.energy_key][0]} {meta[self.energy_key][1]}\n"
        descr +=  f"Camera pixel size: {meta[self.pixel_size_key][0]:.02f} {meta[self.pixel_size_key][1]}\n"
        descr +=  f"Lens magnification: {meta[self.magnification_key][0]}\n"
        descr +=  f"Resolution: {meta[self.resolution_key][0]:.02f} {meta[self.resolution_key][1]}\n"
        descr +=  f"Exposure time: {meta[self.exposure_time_key][0]:.02f} {meta[self.exposure_time_key][1]}\n"
        descr +=  f"Angle step: {meta[self.angle_step_key][0]:.03f} {meta[self.angle_step_key][1]}\n"
        descr +=  f"Number of angles: {meta[self.num_angle_key][0]}\n"
        descr +=  f"Projection size: {self.width} x {self.height}\n"
        if(meta[self.instrument_key][0] == 'Micro-tomography'):
            descr +=  f"Sample detector distance: {meta[self.camera_distance_key][0]} {meta[self.camera_distance_key][1]}"
        self.snippets.create_textbox_with_bullets(
            presentation_id, page_id, descr, 240, 120, 0, 18, 8, fontcolor)

        # read projection(s)
        proj = reads.read_raw(args)
 
        if(meta[self.instrument_key][0] == 'Transmission X-Ray Microscope'):
            log.info('Transmission X-Ray Microscope Instrument')
            log.info('Plotting nanoCT projection')
            # 32-id datasets may include both nanoCT and microCT data as proj[0] and proj[1] respectively
            fname = FILE_NAME_PROJ0+'.jpg'
            nct_resolution = self.resolution / 1000.
            plots.plot_projection(proj[0], fname, resolution=nct_resolution)
            self.publish_projection(fname, presentation_id, page_id, 0, 110)
            self.snippets.create_textbox_with_text(
                presentation_id, page_id, 'Nano-CT projection', 90, 20, 60, 265, 8, 0)
            try:
                log.info('Plotting microCT projection')
                fname = FILE_NAME_PROJ1+'.jpg'
                mct_resolution = self.pixel_size / self.magnification
                plots.plot_projection(proj[1], fname, resolution=mct_resolution)
                self.publish_projection(fname, presentation_id, page_id, 0, 235)
                self.snippets.create_textbox_with_text(
                    presentation_id, page_id, 'Micro-CT projection', 90, 20, 60, 385, 8, 0)
            except:
                log.warning('No microCT data available')
        else:
            log.info('Micro Tomography Instrument')
            log.info('Plotting microCT projection')
            fname = FILE_NAME_PROJ0+'.jpg'
            self.resolution = self.resolution * self.binning
            plots.plot_projection(proj[0], fname, resolution=self.resolution)
            self.publish_projection(fname, presentation_id, page_id, 0, 110)
            self.snippets.create_textbox_with_text(
                presentation_id, page_id, 'Micro-CT projection', 90, 20, 60, 295, 8, 0)                

        # read reconstructions
        recon, binning_rec = reads.read_recon(args, meta)    
        # publish reconstructions
        if len(recon) == 3:
            # prepare reconstruction
            if(meta[self.instrument_key][0] == 'Transmission X-Ray Microscope'):
                log.info('Transmission X-Ray Microscope Instrument')
                self.resolution = self.resolution / 1000. * binning_rec
            else:
                log.info('Micro Tomography Instrument')
                self.resolution = self.resolution * self.binning * binning_rec
            plots.plot_recon(args, self.width, self.height, recon, FILE_NAME_RECON, self.resolution)
            with open(FILE_NAME_RECON, 'rb') as f:
                self.dbx.files_upload(f.read(), '/'+FILE_NAME_RECON, dropbox.files.WriteMode.overwrite)
            recon_url = self.dbx.files_get_temporary_link('/'+FILE_NAME_RECON).link            
            self.snippets.create_image(presentation_id, page_id, recon_url, 370, 370, 130, 30)
            self.snippets.create_textbox_with_text(
                presentation_id, page_id, 'Reconstruction', 90, 20, 270, 0, 10, 0)

        # publish other labels
        self.snippets.create_textbox_with_text(
            presentation_id, page_id, 'Other info/screenshots', 120, 20, 480, 0, 10, 0)

    def publish_projection(self, fname, presentation_id, page_id, posx, posy):
        with open(fname, 'rb') as f:
            self.dbx.files_upload(f.read(), '/'+fname, dropbox.files.WriteMode.overwrite)
            proj_url = self.dbx.files_get_temporary_link('/'+fname).link
            self.snippets.create_image(presentation_id, page_id, proj_url, 210, 210, posx, posy)


