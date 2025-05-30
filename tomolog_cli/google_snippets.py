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

import uuid

from googleapiclient.http import MediaFileUpload

from tomolog_cli import log


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
        log.info('Created slide with ID: {0}'.format(
            create_slide_response.get('objectId')))
        return response
    
    def create_textbox_with_text(self, presentation_id, page_id, text, magnitude_width, magnitude_height, posx, posy, fontsize, fontcolor):
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
                            'height': {'magnitude': magnitude_height, 'unit': 'PT'},
                            'width': {'magnitude': magnitude_width, 'unit': 'PT'}
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
                        'foregroundColor': {
                            'opaqueColor': {
                                'rgbColor': {
                                    'blue': 0.0,
                                    'green': 0.0,
                                    'red': fontcolor
                                }
                            }
                        }                        
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
        log.info('Created textbox with ID: {0}'.format(
            create_shape_response.get('objectId')))
        # [END slides_create_textbox_with_text]
        return response    

    def create_textbox_with_bullets(self, presentation_id, page_id, text, magnitude_width, magnitude_height, posx, posy, fontsize, fontcolor):
        slides_service = self.service
        # [START slides_create_textbox_with_text]
        # Create a new square textbox, using the supplied element ID.
        if text=="":
            return
        element_id = str(uuid.uuid4())
        requests = [
            {
                'createShape': {
                    'objectId': element_id,
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                        'pageObjectId': page_id,
                        'size': {
                            'height': {'magnitude': magnitude_height, 'unit': 'PT'},
                            'width': {'magnitude': magnitude_width, 'unit': 'PT'}
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
                        'foregroundColor': {
                            'opaqueColor': {
                                'rgbColor': {
                                    'blue': 0.0,
                                    'green': 0.0,
                                    'red': fontcolor
                                }
                            }
                        }
                    },
                    'fields': 'foregroundColor,fontSize'
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
        log.info('Created textbox bullets with ID: {0}'.format(
            create_shape_response.get('objectId')))
        return response            
    
    def create_image(self, presentation_id, page_id, IMAGE_URL, magnitude_width, magnitude_height, posx, posy):
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
                        'height': {'magnitude': magnitude_height, 'unit': 'PT'},
                        'width': {'magnitude': magnitude_width, 'unit': 'PT'},
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
        log.info('Created image with ID: {0}'.format(
        create_image_response.get('objectId')))        
        return response

class DriveSnippets(object):
    def __init__(self, service, credentials):
        self.service = service
        self.credentials = credentials

    def upload_file(self, file_name, mimetype, parent_folder_id=None):
        file_metadata = {'name': file_name}
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]

        media = MediaFileUpload(file_name, mimetype=mimetype)
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        print('Google file uploaded. Google file ID:', file.get('id'))
        
    def find_file_id(self, filename, parent_folder_id=None):
        query = f"name='{filename}'"
        if parent_folder_id:
            query += f" and '{parent_folder_id}' in parents"
        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            pageSize=1
        ).execute()
        files = results.get('files', [])
        if files:
            return files[0]['id']
        return None

    def upload_or_update_file(self, file_name, mimetype, parent_folder_id=None):

        file_id = self.find_file_id(file_name, parent_folder_id)
        media = MediaFileUpload(file_name, mimetype=mimetype)

        if file_id:
            log.info("Google file %s exists (ID: %s), updating..." % (file_name, file_id))
            # print(f"Google file '{file_name}' exists (ID: {file_id}), updating...")
            updated_file = self.service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()
            file_id = updated_file.get('id')
            # print(file_id)
            log.info('Google file updated: %s' % str(file_id))

            image_url = f"https://drive.google.com/uc?export=view&id={file_id}"
            log.info('Image url: %s' % image_url)
            return image_url
        else:
            log.info("Google file %s does not exist, creating..." % file_name)
            file_metadata = {'name': file_name}
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            created_file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            file_id = created_file.get('id')
            log.info('Google file created: %s' % str(file_id))
            # print(file_id)
            image_url = f"https://drive.google.com/uc?export=view&id={file_id}"
            return image_url
