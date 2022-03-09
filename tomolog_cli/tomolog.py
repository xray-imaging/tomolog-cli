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
FILE_NAME_PROJ = 'projection_google.jpg'
FILE_NAME_PROJ2 = 'projection2_google.jpg'
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

        
    def run_log(self, args):
        if args.file_name is None:
            args.file_name = PV(args.PV_prefix.get(as_string=True))
        presentation_id = args.presentation_url.split('/')[-2]

        proj, meta = reads.read_scan_info(args)
        # print(meta)

        # Add scan info to a new slide
        page_id = str(uuid.uuid4())
        self.snippets.create_slide(presentation_id, page_id)
        # title
        self.snippets.create_textbox_with_text(presentation_id, page_id, os.path.basename(
            args.file_name)[:-3], 50, 400, 0, 0, 18)  # magnitude
 
        # key definitions
        description_1 = 'measurement_sample_description_1'
        description_2 = 'measurement_sample_description_2'
        description_3 = 'measurement_sample_description_3'
        date          = 'process_acquisition_start_date'
        energy        = 'measurement_instrument_monochromator_energy'
        pixel_size    = 'measurement_instrument_detector_pixel_size'
        magnification = 'measurement_instrument_detection_system_objective_camera_objective'
        resolution    = 'measurement_instrument_detection_system_objective_resolution'
        exposure_time = 'measurement_instrument_detector_exposure_time'
        angle_step    = 'process_acquisition_rotation_rotation_step'
        num_angle     = 'process_acquisition_rotation_num_angles'
        data_size     = 'exchange_data'
        binning       = 'measurement_instrument_detector_binning_x'
        dims          = meta['exchange_data'][0].replace("(", "").replace(")", "").split(',')
        width         = dims[2]
        height        = dims[1]

        plot_param = {}
        plot_param['width']         = int(dims[2])
        plot_param['height']        = int(dims[1])
        plot_param['pixel_size']    = float(meta[pixel_size][0])
        plot_param['resolution']    = float(meta[resolution][0])
        plot_param['magnification'] = int(meta[magnification][0].replace("x", ""))
        plot_param['binning']       = int(meta[binning][0])
        plot_param['scale']         = args.scale
        plot_param['idx']           = args.idx
        plot_param['idy']           = args.idy
        plot_param['idz']           = args.idz

        descr =  f"Particle description: {meta[description_1][0]} {meta[description_2][0]} {meta[description_3][0]}\n"
        descr += f"Scan date: {meta[date][0]}\n"
        descr += f"Scan energy: {meta[energy][0]} {meta[energy][1]}\n"
        descr += f"Pixel size: {meta[pixel_size][0]:.02f} {meta[pixel_size][1]}\n"
        descr += f"Lens magnification: {meta[magnification][0]}\n"
        descr += f"Resolution: {meta[resolution][0]:.02f} {meta[resolution][1]}\n"
        descr += f"Exposure time: {meta[exposure_time][0]:.02f} {meta[exposure_time][1]}\n"
        descr += f"Angle step: {meta[angle_step][0]:.03f} {meta[angle_step][1]}\n"
        descr += f"Number of angles: {meta[num_angle][0]}\n"
        descr += f"Projection size: {width} x {height}"
 
        self.snippets.create_textbox_with_bullets(
            presentation_id, page_id, descr, 270, 300, 0, 27, 12)
        # other labels
        self.snippets.create_textbox_with_text(
            presentation_id, page_id, 'Reconstruction', 30, 150, 270, 0, 14)
        self.snippets.create_textbox_with_text(
            presentation_id, page_id, 'Other info/screenshots', 30, 230, 480, 0, 14)
        self.snippets.create_textbox_with_text(
            presentation_id, page_id, 'Micro-CT projection', 30, 150, 0, 190, 10)
        self.snippets.create_textbox_with_text(
            presentation_id, page_id, 'Nano-CT projection', 30, 150, 0, 290, 10)

        # prepare projection 1
        plots.plot_projection(plot_param, proj[0], FILE_NAME_PROJ)

        with open(FILE_NAME_PROJ, 'rb') as f:
            self.dbx.files_upload(
                f.read(), '/'+FILE_NAME_PROJ, dropbox.files.WriteMode.overwrite)
            proj_url = self.dbx.files_get_temporary_link('/'+FILE_NAME_PROJ).link            
            self.snippets.create_image(
                presentation_id, page_id, proj_url, 210, 210, 0, 240)
            
        if len(proj) == 2:
            # prepare projection 2
            plots.plot_projection(plot_param, proj[1], FILE_NAME_PROJ2, scale=100)
            with open(FILE_NAME_PROJ2, 'rb') as f:
                self.dbx.files_upload(
                    f.read(), '/'+FILE_NAME_PROJ2, dropbox.files.WriteMode.overwrite)
            proj_url = self.dbx.files_get_temporary_link('/'+FILE_NAME_PROJ2).link            
            self.snippets.create_image(
                presentation_id, page_id, proj_url, 210, 210, 0, 115)

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
