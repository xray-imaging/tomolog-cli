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
from tomolog_cli import dropbox_snippets

def drop_box(token_fname):

    # env_path = os.path.join(str(pathlib.Path.home()), '.tomologenv')
    # with open(env_path,'rb') as fid:
    #     log.info('APP_KEY and SECRET_KEY file found at %s' % env_path)
    # load_dotenv(dotenv_path=env_path)
    # app_key = os.environ.get("APP_KEY")
    # authorization_url = "https://www.dropbox.com/oauth2/authorize?client_id=%s&response_type=code" % app_key
    # print(authorization_url)
    # exit()
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
            dbx = dropbox_snippets.DropboxSnippets(dbx)
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
            dbx = dropbox_snippets.DropboxSnippets(dbx)
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
