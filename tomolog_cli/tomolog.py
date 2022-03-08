from tomolog_cli import logging
from tomolog_cli import plots
from tomolog_cli import reads
from tomolog_cli import google_snippets
from tomolog_cli import dropbox_auth
from google.oauth2 import service_account
from googleapiclient.discovery import build
from epics import PV
import dropbox
import os
import json
import uuid

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

        
    def run_log(self,args):
        
        args = args.__dict__
        if args['file_name'] is None:
            args['file_name'] = PV(
                args['PV_prefix'].get(as_string=True))
        args['presentation_id'] = args['presentation_url'].split('/')[-2]
        print(args['presentation_id'])
        proj = reads.read_scan_info(args)
        recon = reads.read_recon(args)

        # Add scan info to a new slide
        page_id = str(uuid.uuid4())
        self.snippets.create_slide(args['presentation_id'], page_id)
        # title
        self.snippets.create_textbox_with_text(args['presentation_id'], page_id, os.path.basename(
            args['file_name'])[:-3], 50, 400, 0, 0, 18)  # magnitude
        # description
        descr = f"Particle description:\n\n"
        descr += f"Scan energy: {args['energy']} keV\n"
        descr += f"Projection size: {args['width']}x{args['height']}\n"
        descr += f"Pixel size: {args['resolution']:.02f} nm\n"
        descr += f"Number of angles: {args['ntheta']}\n"
        descr += f"Exposure time: {args['exposure']:.02f} s\n"
        descr += f"Angle step: {args['step']:.03f} deg"
        self.snippets.create_textbox_with_bullets(
            args['presentation_id'], page_id, descr, 270, 200, 0, 27, 12)
        # other labels
        self.snippets.create_textbox_with_text(
            args['presentation_id'], page_id, 'Reconstruction', 30, 150, 270, 0, 14)
        self.snippets.create_textbox_with_text(
            args['presentation_id'], page_id, 'Other info/screenshots', 30, 230, 480, 0, 14)
        self.snippets.create_textbox_with_text(
            args['presentation_id'], page_id, 'Micro-CT projection', 30, 150, 0, 145, 10)
        self.snippets.create_textbox_with_text(
            args['presentation_id'], page_id, 'Nano-CT projection', 30, 150, 0, 270, 10)

        # prepare projection 1
        plots.plot_projection(args, proj[0], FILE_NAME_PROJ)
        with open(FILE_NAME_PROJ, 'rb') as f:
            try:
                self.dbx.files_upload(
                    f.read(), '/'+FILE_NAME_PROJ, dropbox.files.WriteMode.overwrite)
            except Exception as exc:                
                print(exc)
                log.error('The dropbox token might need to be updated, please follow the following instructions')
                dropbox_auth.auth()
                log.info('The token has been updated, continue upload..')
                self.dbx.files_upload(
                    f.read(), '/'+FILE_NAME_PROJ, dropbox.files.WriteMode.overwrite)
                
            proj_url = self.dbx.files_get_temporary_link('/'+FILE_NAME_PROJ).link            
            self.snippets.create_image(
                args['presentation_id'], page_id, proj_url, 210, 210, 0, 240)
            
        if len(proj) == 2:
            # prepare projection 2
            plots.plot_projection2(args, proj[1], FILE_NAME_PROJ2)
            with open(FILE_NAME_PROJ2, 'rb') as f:
                self.dbx.files_upload(
                    f.read(), '/'+FILE_NAME_PROJ2, dropbox.files.WriteMode.overwrite)
            proj_url = self.dbx.files_get_temporary_link('/'+FILE_NAME_PROJ2).link            
            self.snippets.create_image(
                args['presentation_id'], page_id, proj_url, 210, 210, 0, 115)
        
        if len(recon) == 3:
            # prepare reconstruction
            plots.plot_recon(args, recon, FILE_NAME_RECON)
            with open(FILE_NAME_RECON, 'rb') as f:
                self.dbx.files_upload(
                    f.read(), '/'+FILE_NAME_RECON, dropbox.files.WriteMode.overwrite)
            recon_url = self.dbx.files_get_temporary_link('/'+FILE_NAME_RECON).link            
            self.snippets.create_image(
                args['presentation_id'], page_id, recon_url, 370, 370, 130, 30)
