import json
import requests
import dropbox
from tomolog_cli import logging


log = logging.getLogger(__name__)

def auth(token):

    print(token)
    try:
        with open(token) as f:
            token = json.loads(json.load(f))
            dbx = dropbox.Dropbox(token['access_token'])
            # try to upload a test file
            with open('tmp.txt','w') as fid:
                fid.write('test upload')
            with open('tmp.txt','rb') as fid:
                dbx.files_upload(
                    fid.read(), '/tmp.txt', dropbox.files.WriteMode.overwrite)
            return dbx
    except:
        dropbox_auth.auth()
        with open(token) as f:
            token = json.loads(json.load(f))
            dbx = dropbox.Dropbox(token['access_token'])
    app_key = "evwc7v2rksnhoq3"
    app_secret = "sgz87wxix2p98vu"

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
    with open('/home/beams/USERTXM/tokens/dropbox_token.json', 'w') as f:
        json.dump(json_string, f)
    log.info("dropbox token is saved to /home/beams/USERTXM/tokens/dropbox_token.txt and will be used for further authorization")
    
    return dbx