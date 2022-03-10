import os
import json
import pathlib
import dropbox
import requests
from dotenv import load_dotenv

from tomolog_cli import logging


log = logging.getLogger(__name__)

def auth(token_fname):

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
    except:

        # Set bot tokens as environment values
        env_path = os.path.join(str(pathlib.Path.home()), '.tomologenv')
        load_dotenv(dotenv_path=env_path)
        app_key = os.environ.get("APP_KEY")
        app_secret = os.environ.get("APP_SECRET")

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
            return dbx