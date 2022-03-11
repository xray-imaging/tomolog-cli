import os
import json
import uuid
import time
import pathlib
import dropbox
import requests

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

from tomolog_cli import logging


log = logging.getLogger(__name__)

def drop_box(token_fname):

    log.info('establishing connection to dropbox')
    try:
        with open(token_fname) as f:
            token = json.loads(json.load(f))
            dbx = dropbox.Dropbox(token['access_token'])
            # try to upload a test file
            with open('tmp.txt','w') as fid:
                fid.write('test upload')
            with open('tmp.txt','rb') as fid:
                dbx.files_upload(
                    fid.read(), '/tmp.txt', dropbox.files.WriteMode.overwrite)
            return dbx
    except FileNotFoundError:
        log.error('Dropbox token file not found at %s' % token_fname)
        exit()
    except:
        # Set bot tokens as environment values
        env_path = os.path.join(str(pathlib.Path.home()), '.tomologenv')
        try:
            with open(env_path,'rb') as fid:
                log.info('APP_KEY and SECRET_KEY file found at %s' % env_path)
            load_dotenv(dotenv_path=env_path)
            app_key = os.environ.get("APP_KEY")
            app_secret = os.environ.get("APP_SECRET")
        except FileNotFoundError:
            log.error('APP_KEY and SECRET_KEY are missing. Set them in a file called: %s' % env_path)
            exit()
        # build the authorization URL:
        authorization_url = "https://www.dropbox.com/oauth2/authorize?client_id=%s&response_type=code" % app_key

        # send the user to the authorization URL:
        log.info('Go to the following URL and allow access:')
        log.info(authorization_url)

        # get the authorization code from the user:
        authorization_code = input('Enter the code:\n')

        # exchange the authorization code for an access token:
        token_url = "https://api.dropboxapi.com/oauth2/token"
        params = {
            "code": authorization_code,
            "grant_type": "authorization_code",
            "client_id": app_key,
            "client_secret": app_secret
        }
        log.info('Start authorization to Dropbox')
        r = requests.post(token_url, data=params)
        log.info(json.loads(r.text))
        json_string = json.dumps(json.loads(r.text))
        with open(token_fname, 'w') as f:
            json.dump(json_string, f)
        log.info('dropbox token is saved to %s and will be used for further authorization' % token_fname)
        with open(token_fname) as f:
            token = json.loads(json.load(f))
            dbx = dropbox.Dropbox(token['access_token'])
            log.info('connected to dropbox: OK')
            return dbx

def google(token_fname):

    log.info('establishing connection to google')
    try:
        creds = service_account.Credentials.from_service_account_file(token_fname).with_scopes(['https://www.googleapis.com/auth/presentations'])
        slides = build('slides', 'v1', credentials=creds)
        snippets = SlidesSnippets(slides, creds)
        log.info('connected to google: OK')
        return snippets
    except FileNotFoundError:
        log.error('Google token file not found at %s' % token_fname)
        exit()

class SlidesSnippets(object):
    def __init__(self, service, credentials):
        self.service = service
        self.credentials = credentials

    def create_slide(self, presentation_id, page_id):
        slides_service = self.service
        # take the current number of slides
        presentation = slides_service.presentations().get(
            presentationId=presentation_id).execute()
        nslides = len(presentation.get('slides'))
        # insert a slide at the end
        requests = [
            {
                'createSlide': {
                    'objectId': page_id,
                    'insertionIndex': nslides,#-1tmp for Julie
                    'slideLayoutReference': {
                        'predefinedLayout': 'BLANK'
                    }
                }
            }
        ]
        # Execute the request.
        body = {
            'requests': requests
        }
        response = slides_service.presentations().batchUpdate(presentationId=presentation_id, body=body).execute()
        create_slide_response = response.get('replies')[0].get('createSlide')
        print('Created slide with ID: {0}'.format(
            create_slide_response.get('objectId')))
        return response
    
    def create_textbox_with_text(self, presentation_id, page_id, text, magnitudex, magnitudey, posx, posy, fontsize):
        slides_service = self.service
        # [START slides_create_textbox_with_text]
        # Create a new square textbox, using the supplied element ID.
        element_id = str(uuid.uuid4())
        requests = [
            {
                'createShape': {
                    'objectId': element_id,
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                        'pageObjectId': page_id,
                        'size': {
                            'height': {'magnitude': magnitudex, 'unit': 'PT'},
                            'width': {'magnitude': magnitudey, 'unit': 'PT'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': posx,
                            'translateY': posy,
                            'unit': 'PT'
                        }
                    }
                }
            },

            # Insert text into the box, using the supplied element ID.
            {
                'insertText': {
                    'objectId': element_id,
                    'insertionIndex': 0,
                    'text': text
                }
            },
            
            {
                'updateTextStyle': {
                    'objectId': element_id,
                    'style': {
                        'fontFamily': 'Times New Roman',
                        'fontSize': {
                            'magnitude': fontsize,
                            'unit': 'PT'
                        },
                    },
                    'fields': 'fontSize'
                }
            }            
        ]

        # Execute the request.
        body = {
            'requests': requests
        }
        response = slides_service.presentations() \
            .batchUpdate(presentationId=presentation_id, body=body).execute()
        create_shape_response = response.get('replies')[0].get('createShape')
        print('Created textbox with ID: {0}'.format(
            create_shape_response.get('objectId')))
        # [END slides_create_textbox_with_text]
        return response    

    def create_textbox_with_bullets(self, presentation_id, page_id, text, magnitudex, magnitudey, posx, posy, fontsize):
        slides_service = self.service
        # [START slides_create_textbox_with_text]
        # Create a new square textbox, using the supplied element ID.
        element_id = str(uuid.uuid4())
        requests = [
            {
                'createShape': {
                    'objectId': element_id,
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                        'pageObjectId': page_id,
                        'size': {
                            'height': {'magnitude': magnitudex, 'unit': 'PT'},
                            'width': {'magnitude': magnitudey, 'unit': 'PT'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': posx,
                            'translateY': posy,
                            'unit': 'PT'
                        }
                    }
                }
            },

            # Insert text into the box, using the supplied element ID.
            {
                'insertText': {
                    'objectId': element_id,
                    'insertionIndex': 0,
                    'text': text
                }
            },
            
            {
                'updateTextStyle': {
                    'objectId': element_id,
                    'style': {
                        'fontFamily': 'Times New Roman',
                        'fontSize': {
                            'magnitude': fontsize,
                            'unit': 'PT'
                        },
                    },
                    'fields': 'fontSize'
                }
            },
            {
                'createParagraphBullets': {
                    'objectId': element_id,
                    'textRange': {
                        'type': 'ALL'
                    },
                    'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
                }
            }
        ]

        # Execute the request.
        body = {
            'requests': requests
        }
        response = slides_service.presentations() \
            .batchUpdate(presentationId=presentation_id, body=body).execute()
        create_shape_response = response.get('replies')[0].get('createShape')
        print('Created textbox bullets with ID: {0}'.format(
            create_shape_response.get('objectId')))
        return response            
    
    def create_image(self, presentation_id, page_id, IMAGE_URL, magnitudex, magnitudey, posx, posy):
        slides_service = self.service
        # [START slides_create_image]
        # Create a new image, using the supplied object ID,
        # with content downloaded from IMAGE_URL.
        requests = []
        image_id = str(uuid.uuid4())
        requests.append({
            'createImage': {
                'objectId': image_id,
                'url': IMAGE_URL,
                'elementProperties': {
                    'pageObjectId': page_id,
                    'size': {
                        'height': {'magnitude': magnitudey, 'unit': 'PT'},
                        'width': {'magnitude': magnitudex, 'unit': 'PT'},
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': posx,
                        'translateY': posy,
                        'unit': 'PT'
                    }
                }
            }
        })

        # Execute the request.
        body = {
            'requests': requests
        }
        response = slides_service.presentations() \
            .batchUpdate(presentationId=presentation_id, body=body).execute()
        create_image_response = response.get('replies')[0].get('createImage')
        print('Created image with ID: {0}'.format(
        create_image_response.get('objectId')))        
        return response

        