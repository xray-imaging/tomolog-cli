import uuid
import time

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

        