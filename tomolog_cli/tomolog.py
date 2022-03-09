import os
import json
import uuid
import dropbox

from epics import PV
from google.oauth2 import service_account
from googleapiclient.discovery import build

from tomolog_cli import logging
from tomolog_cli import plots
from tomolog_cli import reads
from tomolog_cli import google_snippets
from tomolog_cli import dropbox_auth

# tmp files to be created in dropbox
FILE_NAME_PROJ  = 'projection_google'
FILE_NAME_RECON = 'reconstruction_google.jpg'

log = logging.getLogger(__name__)

class TomoLog():
    def __init__(self):
        log.info('establishing connection to google and dropbox')
        creds = service_account.Credentials.from_service_account_file(
            '/home/beams/USERTXM/tokens/token_google.json').with_scopes(['https://www.googleapis.com/auth/presentations'])
        slides = build('slides', 'v1', credentials=creds)
        self.snippets = google_snippets.SlidesSnippets(slides, creds)
        try:
            with open('/home/beams/USERTXM/tokens/dropbox_token.json') as f:
                token = json.loads(json.load(f))
                self.dbx = dropbox.Dropbox(token['access_token'])
        except:
            dropbox_auth.auth()
            with open('/home/beams/USERTXM/tokens/dropbox_token.json') as f:
                token = json.loads(json.load(f))
                self.dbx = dropbox.Dropbox(token['access_token'])
        log.info('done')

        # hdf file key definitions
        self.description_1 = 'measurement_sample_description_1'
        self.description_2 = 'measurement_sample_description_2'
        self.description_3 = 'measurement_sample_description_3'
        self.date          = 'process_acquisition_start_date'
        self.energy        = 'measurement_instrument_monochromator_energy'
        self.pixel_size    = 'measurement_instrument_detector_pixel_size'
        self.magnification = 'measurement_instrument_detection_system_objective_camera_objective'
        self.resolution    = 'measurement_instrument_detection_system_objective_resolution'
        self.exposure_time = 'measurement_instrument_detector_exposure_time'
        self.angle_step    = 'process_acquisition_rotation_rotation_step'
        self.num_angle     = 'process_acquisition_rotation_num_angles'
        self.data_size     = 'exchange_data'
        self.binning       = 'measurement_instrument_detector_binning_x'

    def run_log(self, args):

        if args.file_name is None:
            args.file_name = PV(args.PV_prefix.get(as_string=True))
        presentation_id = args.presentation_url.split('/')[-2]

        # Create a new Google slide
        page_id = str(uuid.uuid4())
        self.snippets.create_slide(presentation_id, page_id)
        # title
        self.snippets.create_textbox_with_text(presentation_id, page_id, os.path.basename(
            args.file_name)[:-3], 50, 400, 0, 0, 18)  # magnitude
 
        proj, meta = reads.read_scan_info(args)
        # print(meta)
        # print(proj)
        dims          = meta['exchange_data'][0].replace("(", "").replace(")", "").split(',')
        width         = dims[2]
        height        = dims[1]

        plot_param = {}
        plot_param['width']         = int(dims[2])
        plot_param['height']        = int(dims[1])
        plot_param['pixel_size']    = float(meta[self.pixel_size][0])
        plot_param['resolution']    = float(meta[self.resolution][0])
        plot_param['magnification'] = int(meta[self.magnification][0].replace("x", ""))
        plot_param['binning']       = int(meta[self.binning][0])
        plot_param['scale']         = args.scale
        plot_param['idx']           = args.idx
        plot_param['idy']           = args.idy
        plot_param['idz']           = args.idz
        plot_param['min']           = args.min
        plot_param['max']           = args.max

        # publish labels and scan info in the new slide
        descr =  f"Particle description: {meta[self.description_1][0]} {meta[self.description_2][0]} {meta[self.description_3][0]}\n"
        descr += f"Scan date: {meta[self.date][0]}\n"
        descr += f"Scan energy: {meta[self.energy][0]} {meta[self.energy][1]}\n"
        descr += f"Pixel size: {meta[self.pixel_size][0]:.02f} {meta[self.pixel_size][1]}\n"
        descr += f"Lens magnification: {meta[self.magnification][0]}\n"
        descr += f"Resolution: {meta[self.resolution][0]:.02f} {meta[self.resolution][1]}\n"
        descr += f"Exposure time: {meta[self.exposure_time][0]:.02f} {meta[self.exposure_time][1]}\n"
        descr += f"Angle step: {meta[self.angle_step][0]:.03f} {meta[self.angle_step][1]}\n"
        descr += f"Number of angles: {meta[self.num_angle][0]}\n"
        descr += f"Projection size: {width} x {height}"
        self.snippets.create_textbox_with_bullets(
            presentation_id, page_id, descr, 270, 300, 0, 27, 12)

        # publish other labels
        self.snippets.create_textbox_with_text(
            presentation_id, page_id, 'Reconstruction', 30, 150, 270, 0, 14)
        self.snippets.create_textbox_with_text(
            presentation_id, page_id, 'Other info/screenshots', 30, 230, 480, 0, 14)
        self.snippets.create_textbox_with_text(
            presentation_id, page_id, 'Micro-CT projection', 30, 150, 0, 190, 10)
        self.snippets.create_textbox_with_text(
            presentation_id, page_id, 'Nano-CT projection', 30, 150, 0, 290, 10)
        
        # publish projections
        for i in range(len(proj)):
            fname = FILE_NAME_PROJ+str(i)+'.jpg'
            self.publish_projection(fname, proj[i], plot_param, presentation_id, page_id, 210, 210, 0, 115+i*125)

        # publish reconstructions
        recon = reads.read_recon(args, plot_param)    
        if len(recon) == 3:
            # prepare reconstruction
            plots.plot_recon(args, plot_param, recon, FILE_NAME_RECON)
            with open(FILE_NAME_RECON, 'rb') as f:
                self.dbx.files_upload(
                    f.read(), '/'+FILE_NAME_RECON, dropbox.files.WriteMode.overwrite)
            recon_url = self.dbx.files_get_temporary_link('/'+FILE_NAME_RECON).link            
            self.snippets.create_image(
                presentation_id, page_id, recon_url, 370, 370, 130, 30)

    def publish_projection(self, fname, proj, plot_param, presentation_id, page_id, a, b, c, d):
        plots.plot_projection(plot_param, proj, fname)
        with open(fname, 'rb') as f:
            try:
                self.dbx.files_upload(
                    f.read(), '/'+fname, dropbox.files.WriteMode.overwrite)
            except Exception as exc:                
                print(exc)
                log.error('The dropbox token might need to be updated, please follow the following instructions')
                dropbox_auth.auth()
                log.info('The token has been updated, continue upload..')
                self.dbx.files_upload(
                    f.read(), '/'+fname, dropbox.files.WriteMode.overwrite)
            proj_url = self.dbx.files_get_temporary_link('/'+fname).link            
            self.snippets.create_image(
                presentation_id, page_id, proj_url, a, b, c, d)
