import os
import json
import pathlib
import dropbox
import requests

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

from tomolog_cli import log
from tomolog_cli import google_snippets

def drop_box(token_fname):

    log.info('Establishing connection to dropbox')
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
            log.info('Connection to dropbox: OK')
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
            log.info('Connection to dropbox: OK')
            return dbx

def google(token_fname):

    log.info('Establishing connection to google')
    try:
        creds = service_account.Credentials.from_service_account_file(token_fname).with_scopes(['https://www.googleapis.com/auth/presentations'])
        slides = build('slides', 'v1', credentials=creds)
        snippets = google_snippets.SlidesSnippets(slides, creds)
        log.info('Connection to google: OK')
        return snippets
    except FileNotFoundError:
        log.error('Google token file not found at %s' % token_fname)
        exit()
