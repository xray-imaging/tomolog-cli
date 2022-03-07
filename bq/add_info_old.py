from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from snippets import SlidesSnippets
import matplotlib.pyplot as plt
import uuid
import h5py
import sys
import os
import utils
from epics import PV

# The ID of the presentation and folder for storing an image file in google drive
# Note: both should be open-accessed for editing
# PRESENTATION_ID = '1g5V_lcG35-Q6e4XLoGQaM27Ace1UR6AEo9WUXu-Xhr0'
PRESENTATION_ID = '1UWF1oCluvV4Gmo3iWtyK8F5pwysCuQYLiSXqKaELCws'#Julie
FOLDER_ID = '1XGx5-0qC8ZYwTusxYszsRHNgRw8o5l36'

# scopes for google slides and drive
SCOPES = ['https://www.googleapis.com/auth/presentations',
          'https://www.googleapis.com/auth/drive.file']

def read_scan_info(file_name):
    pars = {}
    with h5py.File(file_name) as fid:        
        pars['energy'] = fid['measurement/instrument/monochromator/energy'][0]
        pars['height'] = fid['exchange/data'].shape[1]
        pars['width'] = fid['exchange/data'].shape[2]    
        pars['pixelsize'] = float(fid['measurement/instrument/detection_system/objective/resolution'][0])
        pars['ntheta'] = len(fid['exchange/theta'])
        pars['exposure'] = fid['measurement/instrument/detector/exposure_time'][0]
        pars['step'] = fid['exchange/theta'][1]-fid['exchange/theta'][0]
        pars['proj'] = fid['exchange/data'][0][:]
    return pars

def main():
    if len(sys.argv)==2:
        file_name = sys.argv[1]    
    else:
        file_name = PV('32idcSP1:HDF1:FullFileName_RBV').get(as_string=True)
    
    pars = read_scan_info(file_name)
    mmin,mmax = utils.find_min_max(pars['proj'])
    pars['proj'][pars['proj']>mmax] = mmax
    pars['proj'][pars['proj']<mmin] = mmin
    
    plt.imshow(pars['proj'], cmap='gray')
    plt.plot([pars['width']*8.7/10,pars['width']*8.7/10+10000/pars['pixelsize']],[pars['height']*9.5/10,pars['height']*9.5/10],'r')
    plt.text(pars['width']*8.75/10,pars['height']*9.2/10,'10um',color='red')
    plt.savefig('projection_for_google.png',bbox_inches='tight',pad_inches = 0) 
        
    # connect with the token
    credentials = service_account.Credentials.from_service_account_file('token.json')
    creds = credentials.with_scopes(SCOPES)
    service = build('slides', 'v1', credentials=creds)
    drive =  build('drive',  'v3', credentials=creds)
                
    # remove existing file in the google folder (otherwise it will be not enogh memory in a while)
    rsp = drive.files().list(
            q="name='projection_for_google.png'" ).execute().get('files')
        
    if len(rsp)>0:
        drive.files().delete(fileId=rsp[0]['id']).execute()
    # upload a file
    # first, define file metadata, such as the name and the parent folder ID
    file_metadata = {
        "name": "projection_for_google.png",
        "parents": [FOLDER_ID]
    }
    # upload
    media = MediaFileUpload("projection_for_google.png", resumable=True)
    file = drive.files().create(body=file_metadata, media_body=media, fields='id').execute()        
    # take file id and generate the url of the image
    rsp = drive.files().list(
            q="name='projection_for_google.png'" ).execute().get('files')[0]
    IMAGE_URL = 'https://drive.google.com/uc?export=download&id=' + rsp['id']
    
    
    #### Create a slide
    snippets = SlidesSnippets(service, creds)
    uuid.uuid4()
    page_id = str(uuid.uuid4())
    snippets.create_slide(PRESENTATION_ID,page_id)
    #title
    snippets.create_textbox_with_text(PRESENTATION_ID,page_id, os.path.basename(file_name)[:-3], 50, 400, 10, 10, 24)
    descr = f"Particle description:\n\n"
    descr += f"Scan energy: {pars['energy']} keV\n"
    descr += f"Projection size: {pars['width']}x{pars['height']}\n"
    descr += f"Pixel size: {pars['pixelsize']:.02f} nm\n"
    descr += f"Number of angles: {pars['ntheta']}\n"
    descr += f"Exposure time: {pars['exposure']:.02f} s\n"
    descr += f"Angle step: {pars['step']:.03f} deg"
    snippets.create_textbox_with_bullets(PRESENTATION_ID,page_id, descr, 300,250, 10, 50, 16)
    # projection in high resolution
    snippets.create_image(PRESENTATION_ID, page_id, IMAGE_URL, 280, 280, 10, 170)
    # projection in low resolution

if __name__ == '__main__':
    main()
