import os
import json
import uuid
import pathlib

from tomolog_cli import log
from tomolog_cli import plots
from tomolog_cli import reads
from tomolog_cli import auth

__author__ = "Viktor Nikitin,  Francesco De Carlo"
__copyright__ = "Copyright (c) 2022, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['TomoLog',]

# tmp files to be created in dropbox
FILE_NAME_PROJ0  = 'projection_google0.jpg'
FILE_NAME_PROJ1  = 'projection_google1.jpg'
FILE_NAME_RECON = 'reconstruction_google.jpg'

DROPBOX_TOKEN   = os.path.join(str(pathlib.Path.home()), 'tokens', 'dropbox_token.json')
GOOGLE_TOKEN    = os.path.join(str(pathlib.Path.home()), 'tokens', 'google_token.json')

class TomoLog():
    '''
    Class to publish experiment meta data, tomography projection and reconstruction on a 
    google slide document.
    '''
    def __init__(self):

        self.google  = auth.google(GOOGLE_TOKEN)
        self.dbx = auth.drop_box(DROPBOX_TOKEN)
        
        # hdf file key standardized definitions
        self.full_file_name_key  = '/measurement/sample/file/full_name'
        self.description_1_key   = '/measurement/sample/description_1'
        self.description_2_key   = '/measurement/sample/description_2'
        self.description_3_key   = '/measurement/sample/description_3'
        self.date_key            = '/process/acquisition/start_date'
        self.energy_key          = '/measurement/instrument/monochromator/energy'
        self.pixel_size_key      = '/measurement/instrument/detector/pixel_size'
        self.magnification_key   = '/measurement/instrument/detection_system/objective/magnification'
        self.resolution_key      = '/measurement/instrument/detection_system/objective/resolution'
        self.exposure_time_key   = '/measurement/instrument/detector/exposure_time'
        self.rotation_start_key  = '/process/acquisition/rotation/start'
        self.angle_step_key      = '/process/acquisition/rotation/step'
        self.num_angle_key       = '/process/acquisition/rotation/num_angles'
        self.width_key           = '/measurement/instrument/detector/array_size_x'
        self.height_key          = '/measurement/instrument/detector/array_size_y'
        self.binning_key         = '/measurement/instrument/detector/binning_x'
        self.beamline_key        = '/measurement/instrument/source/beamline'
        self.instrument_key      = '/measurement/instrument/name'
        self.camera_distance_key = '/measurement/instrument/detector_motor_stack/setup/z'
        self.sample_in_x_key     = '/process/acquisition/flat_fields/sample/in_x'

    def run_log(self, args):

        args.double_fov = False # Set to true for 0-360 data sets
        try:
            presentation_id = args.presentation_url.split('/')[-2]
        except AttributeError:
            log.error("Set --presentation-url to point to a valid Google slide location")
            exit()
        # Create a new Google slide
        page_id = str(uuid.uuid4())
        self.google.create_slide(presentation_id, page_id)

        meta = reads.read_scan_info(args)
        file_name =  os.path.basename(args.file_name)
        # print(meta)
        # publish title
        # exit()
        try:
            instrument_name = meta[self.instrument_key][0]
            log.info(instrument_name)
        except KeyError:
            log.error('Corrupted file: missing instrument name')
            log.error('or File locked by another program')
            return

        try:
            original_full_file_name = meta[self.full_file_name_key][0]
            self.google.create_textbox_with_text(presentation_id, page_id, os.path.basename(
                original_full_file_name)[:-3], 400, 50, 0, 0, 13, 0)
        except TypeError:
            self.google.create_textbox_with_text(presentation_id, page_id, file_name, 400, 50, 0, 0, 13, 1)
        except KeyError:
            self.google.create_textbox_with_text(presentation_id, page_id, str(args.file_name), 400, 50, 0, 0, 13, 1)
            self.google.create_textbox_with_text(presentation_id, page_id, 'Unable to open file (truncated file)', 90, 20, 350, 0, 10, 1)
            return

        try:
            meta[self.magnification_key][0].replace("x", "")
            fontcolor = 0
        except:
            log.error('Objective magnification was not stored [%s, %s] for dataset: %s' % (meta[self.magnification_key][0], meta[self.magnification_key][1], original_full_file_name))
            log.error('Using --magnification parameter: %s' % args.magnification)
            log.error('Using --pixel-size parameter: %f' % args.pixel_size)
            meta[self.pixel_size_key][0] = args.pixel_size
            meta[self.pixel_size_key][1] ='um'
            meta[self.magnification_key][0] = args.magnification
            meta[self.resolution_key][0] = args.pixel_size / float(meta[self.magnification_key][0].replace("x", ""))
            log.warning('Calculated resolution: %s' % meta[self.resolution_key][0])
            meta[self.resolution_key][1] = 'um'
            fontcolor = 1

        self.width  = int(meta[self.width_key][0])
        self.height = int(meta[self.height_key][0])
        
        self.resolution       = float(meta[self.resolution_key][0])
        self.resolution_units = str(meta[self.resolution_key][1])
        self.pixel_size       = float(meta[self.pixel_size_key][0])
        self.pixel_size_units = str(meta[self.pixel_size_key][1])
        self.magnification    = float(meta[self.magnification_key][0].replace("x", ""))
        self.binning          = int(meta[self.binning_key][0])
        if meta[self.exposure_time_key][1] == None:
            log.warning('Exposure time units are missing assuming (s)')
            meta[self.exposure_time_key][1] = 's'

        # publish scan info
        descr  =  f"File name: {file_name}\n"
        descr +=  f"Beamline: {meta[self.beamline_key][0]} {meta[self.instrument_key][0]}\n"
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
            if (meta[self.sample_in_x_key][0] != 0):
                args.double_fov = True
                log.warning('Sample in x is off center: %s. Handling the data set as a double FOV' % meta[self.sample_in_x_key][0])
        self.google.create_textbox_with_bullets(
            presentation_id, page_id, descr, 240, 120, 0, 18, 8, fontcolor)

        # read projection(s)
        proj = reads.read_raw(args)
 
        if(meta[self.instrument_key][0] == 'Transmission X-Ray Microscope'):
            log.info('Transmission X-Ray Microscope Instrument')
            log.info('Plotting nanoCT projection')
            # 32-id datasets may include both nanoCT and microCT data as proj[0] and proj[1] respectively
            nct_resolution = self.resolution / 1000.
            
            plots.plot_projection(proj[0], FILE_NAME_PROJ0, resolution=nct_resolution) 
            proj_url = self.dbx.upload(FILE_NAME_PROJ0)
            self.google.create_image(presentation_id, page_id, proj_url, 170, 170, 0, 145)        

            self.google.create_textbox_with_text(
                presentation_id, page_id, 'Nano-CT projection', 90, 20, 50, 150, 8, 0)
            try:
                log.info('Plotting microCT projection')
                mct_resolution = self.pixel_size / self.magnification
                plots.plot_projection(proj[1], FILE_NAME_PROJ1, resolution=mct_resolution)
                proj_url = self.dbx.upload(FILE_NAME_PROJ1)
                self.google.create_image(presentation_id, page_id, proj_url, 170, 170, 0, 270)

                self.google.create_textbox_with_text(
                    presentation_id, page_id, 'Micro-CT projection', 160, 20, 10, 290, 8, 0)
            except:
                log.warning('No microCT data available')
        else:
            log.info('Micro Tomography Instrument')
            log.info('Plotting microCT projection')
            self.resolution = self.resolution * self.binning
            plots.plot_projection(proj[0], FILE_NAME_PROJ0, resolution=self.resolution)
            proj_url = self.dbx.upload(FILE_NAME_PROJ0)
            self.google.create_image(presentation_id, page_id, proj_url, 150, 150, 10, 157)
            
            self.google.create_textbox_with_text(
                presentation_id, page_id, 'Micro-CT projection', 90, 20, 50, 153, 8, 0)
            try:
                log.info('Plotting frame the IP camera')
                plots.plot_frame(proj[1], FILE_NAME_PROJ1)
                proj_url = self.dbx.upload(FILE_NAME_PROJ1)
                self.google.create_image(presentation_id, page_id, proj_url, 170, 170, 0, 270)
                self.google.create_textbox_with_text(
                    presentation_id, page_id, 'Frame from the IP camera in the hutch', 160, 20, 10, 290, 8, 0)
            except:
                log.warning('No frame from the IP camera')
        # read reconstructions
        recon, binning_rec = reads.read_recon(args, meta)    
        rec_line = reads.read_rec_line(args)
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
            recon_url = self.dbx.upload(FILE_NAME_RECON)
            self.google.create_image(presentation_id, page_id, recon_url, 370, 370, 130, 25)
            self.google.create_textbox_with_text(
                presentation_id, page_id, 'Reconstruction', 90, 20, 270, 0, 10, 0)
        if rec_line is not None:
            self.google.create_textbox_with_text(
                    presentation_id, page_id, rec_line, 1000, 20, 185, 391, 6, 0)
        # publish other labels
        self.google.create_textbox_with_text(
            presentation_id, page_id, 'Other info/screenshots', 120, 20, 480, 0, 10, 0)

