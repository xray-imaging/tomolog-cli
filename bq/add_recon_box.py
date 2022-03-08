from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from snippets2 import SlidesSnippets
import matplotlib.pyplot as plt
import uuid
import h5py
import sys
import os
import tomolog_cli.utils as utils
from epics import PV
import dxchange
import numpy as np
import matplotlib.patheffects as PathEffects
from mpl_toolkits.axes_grid1 import make_axes_locatable

# The ID of the presentation and folder for storing an image file in google drive
# Note: both should be open-accessed for editing
# PRESENTATION_ID = '1F-uy0yzMWSggTovn1wTUJQukZiGRv_J4rFFd2Em7T3w'
PRESENTATION_ID = '1UWF1oCluvV4Gmo3iWtyK8F5pwysCuQYLiSXqKaELCws'#Julie
FOLDER_ID = '1XGx5-0qC8ZYwTusxYszsRHNgRw8o5l36'
FILENAME_PROJ = 'proj_for_google2.jpg'
FILENAME_PROJ2 = 'proj2_for_google2.jpg'
FILENAME_RECON = 'recon_for_google2.jpg'

# scopes for google slides and drive
SCOPES = ['https://www.googleapis.com/auth/presentations',
          'https://www.googleapis.com/auth/drive.file']

def read_scan_info(pars):
    '''Read acquistion parameters and the first projection from an hdf5 file
    '''
    
    with h5py.File(pars['filename']) as fid:        
        pars['energy'] = fid['measurement/instrument/monochromator/energy'][0]
        pars['height'] = fid['exchange/data'].shape[1]
        pars['width'] = fid['exchange/data'].shape[2]    
        pars['pixelsize'] = float(fid['measurement/instrument/detector/pixel_size'][0])
        pars['cameraobjective'] = float(fid['measurement/instrument/detection_system/objective/camera_objective'][0])
        pars['resolution'] = float(fid['measurement/instrument/detection_system/objective/resolution'][0])
        pars['ntheta'] = len(fid['exchange/theta'])
        pars['exposure'] = fid['measurement/instrument/detector/exposure_time'][0]
        pars['step'] = fid['exchange/theta'][1]-fid['exchange/theta'][0]
        pars['proj'] = fid['exchange/data'][0][:]
        try:
            pars['proj2'] = fid['exchange/data2'][0][:]
        except:
            pars['proj2'] = None
    
    return pars

def read_recon(pars):
    '''Read reconstructed orho-slices
    '''    
    
    try:
        basename = os.path.basename(pars['filename'])[:-3]    
        dirname = os.path.dirname(pars['filename'])    
        # shift from the middle
        shift = -10
        # read z slices
        idz = pars['height']//2+shift
        pars['z'] = dxchange.read_tiff(f'{dirname}_recgpu/{basename}_rec/r_{idz:05}.tiff').copy()
        # read x,y slices by lines
        pars['y'] = np.zeros((pars['height'],pars['width']),dtype='float32')
        pars['x'] = np.zeros((pars['height'],pars['width']),dtype='float32')    
        for j in range(pars['height']):
            zz = dxchange.read_tiff(f'{dirname}_recgpu/{basename}_rec/r_{j:05}.tiff')
            pars['y'][j,:] = zz[pars['width']//2+shift]
            pars['x'][j,:] = zz[:,pars['width']//2+shift]        
    except:
        pars['z'] = None
        pars['y'] = None
        pars['x'] = None
    return pars

def plot_projection_micro(pars):
    '''Plot the first projection with a scalebar and colorbar, and save it to FILENAME_PROJ
    '''
    
    # auto-adjust colorbar values according to a histogram
    mmin,mmax = utils.find_min_max(pars['proj2'])
    pars['proj2'][pars['proj2']>mmax] = mmax
    pars['proj2'][pars['proj2']<mmin] = mmin

    # plot
    fig = plt.figure(constrained_layout=True, figsize=(6, 4))
    ax = fig.add_subplot()    
    im = ax.imshow(pars['proj2'], cmap='gray')
    ax.plot([pars['width']*8.7/10,pars['width']*8.7/10+100/(pars['pixelsize']/pars['cameraobjective'])],[pars['height']*9.5/10,pars['height']*9.5/10],'r')
    txt=ax.text(pars['width']*8.5/10,pars['height']*9.15/10,'100um',color='red',fontsize=14)
    txt.set_path_effects([PathEffects.withStroke(linewidth=1, foreground='w')])
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)   
    plt.colorbar(im, cax=cax)
    
    # save
    plt.savefig(FILENAME_PROJ2,bbox_inches='tight',pad_inches = 0,dpi=150) 

def plot_projection_nano(pars):
    '''Plot the first projection with a scalebar and colorbar, and save it to FILENAME_PROJ
    '''
    
    # auto-adjust colorbar values according to a histogram
    mmin,mmax = utils.find_min_max(pars['proj'])
    pars['proj'][pars['proj']>mmax] = mmax
    pars['proj'][pars['proj']<mmin] = mmin

    # plot
    fig = plt.figure(constrained_layout=True, figsize=(6, 4))
    ax = fig.add_subplot()    
    im = ax.imshow(pars['proj'], cmap='gray')
    ax.plot([pars['width']*8.7/10,pars['width']*8.7/10+10000/pars['resolution']],[pars['height']*9.5/10,pars['height']*9.5/10],'r')
    txt=ax.text(pars['width']*8.7/10,pars['height']*9.1/10,'10um',color='red',fontsize=14)
    txt.set_path_effects([PathEffects.withStroke(linewidth=1, foreground='w')])
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)   
    plt.colorbar(im, cax=cax)
    
    # save
    plt.savefig(FILENAME_PROJ,bbox_inches='tight',pad_inches = 0,dpi=150) 

def plot_recon(pars):
    '''Plot orthoslices with scalebars and colorbars, and save the figure as FILENAME_RECON
    '''
    
    fig = plt.figure(constrained_layout=True, figsize=(6, 12))
    grid = fig.add_gridspec(3, 1, height_ratios = [pars['width']/pars['height'], 1, 1])
    slices = ['z','y','x']
    # autoadjust colorbar values according to a histogram
    mmin,mmax = utils.find_min_max(pars[slices[1]])   
    
    scalebar = 10 #um
    # plot 3 slices in a column
    for k in range(3):
        s = slices[k]
        pars[s][pars[s]>mmax] = mmax
        pars[s][pars[s]<mmin] = mmin    
        ax = fig.add_subplot(grid[k])            
        im = ax.imshow(pars[s], cmap='gray')        
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)   
        plt.colorbar(im, cax=cax)
        ax.set_ylabel(f'slice {slices[k]}')
        if(k<2):
            ax.set_xticklabels([])    
        if k==0:# z slices
            ax.plot([pars['width']*8.7/10,pars['width']*8.7/10+scalebar*1000/pars['resolution']],[pars['width']*9.5/10,pars['width']*9.5/10],'r')
            txt = ax.text(pars['width']*8.7/10,pars['width']*9.15/10,f'{scalebar}um',color='red',fontsize=14)
            txt.set_path_effects([PathEffects.withStroke(linewidth=1, foreground='w')])
        else: #x,y slices
            ax.plot([pars['width']*8.7/10,pars['width']*8.7/10+scalebar*1000/pars['resolution']],[pars['height']*9.5/10,pars['height']*9.5/10],'r')
            txt = ax.text(pars['width']*8.7/10,pars['height']*9.1/10,f'{scalebar}um',color='red',fontsize=14)
            txt.set_path_effects([PathEffects.withStroke(linewidth=1, foreground='w')])    
    plt.savefig(FILENAME_RECON,bbox_inches='tight',pad_inches = 0,dpi=150) 

def upload_proj_micro(drive):
    # remove existing file in the google folder (otherwise it will be not enogh memory in a while)
    rsp = drive.files().list(
            q=f"name='{FILENAME_PROJ2}'" ).execute().get('files')
        
    if len(rsp)>0:
        drive.files().delete(fileId=rsp[0]['id']).execute()
    # upload a file
    # first, define file metadata, such as the name and the parent folder ID
    file_metadata = {
        "name": FILENAME_PROJ2,
        "parents": [FOLDER_ID]
    }
    # upload
    media = MediaFileUpload(FILENAME_PROJ2, resumable=True)
    file = drive.files().create(body=file_metadata, media_body=media, fields='id').execute()        
    # take file id and generate the url of the image
    rsp = drive.files().list(
            q=f"name='{FILENAME_PROJ2}'" ).execute().get('files')[0]
        
    proj_url = 'https://anl.box.com/shared/static/' + rsp['id'] + '.jpg'
    print(proj_url)
    return proj_url

def upload_proj_nano(drive):
    # remove existing file in the google folder (otherwise it will be not enogh memory in a while)
    rsp = drive.files().list(
            q=f"name='{FILENAME_PROJ}'" ).execute().get('files')
        
    if len(rsp)>0:
        drive.files().delete(fileId=rsp[0]['id']).execute()
    # upload a file
    # first, define file metadata, such as the name and the parent folder ID
    file_metadata = {
        "name": FILENAME_PROJ,
        "parents": [FOLDER_ID]
    }
    # upload
    media = MediaFileUpload(FILENAME_PROJ, resumable=True)
    file = drive.files().create(body=file_metadata, media_body=media, fields='id').execute()        
    # take file id and generate the url of the image
    rsp = drive.files().list(
            q=f"name='{FILENAME_PROJ}'" ).execute().get('files')[0]
        
    proj_url = 'https://anl.box.com/shared/static/' + rsp['id'] + '.jpg'
    print(proj_url)
    return proj_url


def upload_recon(drive):
    # remove existing file in the google folder (otherwise it will be not enogh memory in a while)
    rsp = drive.files().list(
            q=f"name='{FILENAME_RECON}'" ).execute().get('files')
        
    if len(rsp)>0:
        drive.files().delete(fileId=rsp[0]['id']).execute()
    # upload a file
    # first, define file metadata, such as the name and the parent folder ID
    file_metadata = {
        "name": FILENAME_RECON,
        "parents": [FOLDER_ID]
    }
    # upload
    media = MediaFileUpload(FILENAME_RECON, resumable=True)
    file = drive.files().create(body=file_metadata, media_body=media, fields='id').execute()        
    # take file id and generate the url of the image
    rsp = drive.files().list(
            q=f"name='{FILENAME_RECON}'" ).execute().get('files')[0]
    recon_url = 'https://anl.box.com/shared/static/' + rsp['id'] + '.jpg'
    print(recon_url)
    return recon_url    
    
def main():
    pars = {}
    if len(sys.argv)==2:
        pars['filename'] = sys.argv[1]    
    else:
        pars['filename'] = PV('32idcSP1:HDF1:FullFileName_RBV').get(as_string=True)
    
    
    # connect with the token
    credentials = service_account.Credentials.from_service_account_file('token.json')
    creds = credentials.with_scopes(SCOPES)
    slides = build('slides', 'v1', credentials=creds)
    drive =  build('drive',  'v3', credentials=creds)
    
    
    # magnitude_list = [210,210,370]
    # posx_list = [0,0,130]
    # posy_list = [115,240,30]
    
    
    read_scan_info(pars)            
    if pars is None:
        print('Error with opening h5 file')
        return    
    
    read_recon(pars)
    
    url_list = []
    magnitude_list = []
    posx_list = []
    posy_list = []
    
    print('prepare nanoCT projection')
    plot_projection_nano(pars)
    proj_url = upload_proj_nano(drive)                
    url_list.append(proj_url)
    magnitude_list.append(210)        
    posx_list.append(0)    
    posy_list.append(240)
     
    if pars['proj2'] is not None:    
        print('prepare microCT projection')
        plot_projection_micro(pars)    
        proj_url = upload_proj_micro(drive)                
        url_list.append(proj_url)
        magnitude_list.append(210)        
        posx_list.append(0)            
        posy_list.append(115)   
         
    if pars['z'] is not None:
        print('prepare reconstruction')
        plot_recon(pars)    
        recon_url = upload_recon(drive)
        url_list.append(recon_url)
        magnitude_list.append(370)
        posx_list.append(130)        
        posy_list.append(30)
    
    #### Slide construction with using snippets
    snippets = SlidesSnippets(slides, creds)
    page_id = str(uuid.uuid4())
    snippets.create_slide(PRESENTATION_ID,page_id)
    #title
    snippets.create_textbox_with_text(PRESENTATION_ID,page_id, os.path.basename(pars['filename'])[:-3], 50, 400, 0, 0, 18)# magnitude
    #description    
    descr = f"Particle description:\n\n"
    descr += f"Scan energy: {pars['energy']} keV\n"
    descr += f"Projection size: {pars['width']}x{pars['height']}\n"
    descr += f"Pixel size: {pars['resolution']:.02f} nm\n"
    descr += f"Number of angles: {pars['ntheta']}\n"
    descr += f"Exposure time: {pars['exposure']:.02f} s\n"
    descr += f"Angle step: {pars['step']:.03f} deg"
    snippets.create_textbox_with_bullets(PRESENTATION_ID,page_id, descr, 270,200, 0, 27, 12)
    snippets.create_textbox_with_text(PRESENTATION_ID,page_id, 'Reconstruction', 30, 150, 270, 0, 14)
    snippets.create_textbox_with_text(PRESENTATION_ID,page_id, 'Other info/screenshots', 30, 230, 480, 0, 14)
    snippets.create_textbox_with_text(PRESENTATION_ID,page_id, 'Micro-CT projection', 30, 150, 0, 145, 10)
    snippets.create_textbox_with_text(PRESENTATION_ID,page_id, 'Nano-CT projection', 30, 150, 0, 270, 10)
    # projection image
    # snippets.create_image(PRESENTATION_ID, page_id, proj_url, 210, 210, 0, 115)
    # snippets.create_image(PRESENTATION_ID, page_id, proj_url, 210, 210, 0, 240)
    # # recon image    
    # snippets.create_image(PRESENTATION_ID, page_id, recon_url, 370, 370, 130, 30)    
    
    snippets.create_images(PRESENTATION_ID, page_id, url_list, magnitude_list, magnitude_list, posx_list, posy_list)

if __name__ == '__main__':
    main()
