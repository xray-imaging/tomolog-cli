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

import re
import socks
import socket
import httplib2


# from google.auth.transport.urllib3 import AuthorizedHttp
from google_auth_httplib2 import AuthorizedHttp
from googleapiclient.discovery import build
from google.oauth2 import service_account

from tomolog_cli import log
from tomolog_cli import google_snippets

def google_slide(args, token_fname):

    log.info('Establishing connection to google')
    if(args.public):
        log.info('Running from a public network computer')
        try:
            creds = service_account.Credentials.from_service_account_file(token_fname).with_scopes(['https://www.googleapis.com/auth/presentations'])
            slides = build('slides', 'v1', credentials=creds)
            snippets = google_snippets.SlidesSnippets(slides, creds)
            log.info('Connection to google: OK')
            return snippets
        except FileNotFoundError:
            log.error('Google token file not found at %s' % token_fname)
            exit()
    else:
        log.info('Running from a private network computer')
        # Monkey-patch socket to route through SOCKS5
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 1081)
        socket.socket = socks.socksocket

        # Create an httplib2.Http instance with socks-configured socket
        http = httplib2.Http()

        creds = service_account.Credentials.from_service_account_file(token_fname).with_scopes(['https://www.googleapis.com/auth/presentations'])
        authed_http = AuthorizedHttp(creds, http=http)
        slides = build('slides', 'v1', http=authed_http)
        try:
            # Replace 'YOUR_PRESENTATION_ID' with a valid one if available
            slides.presentations().get(presentationId=extract_presentation_id(args.presentation_url)).execute()
            log.info("✅ Google Slides API connection verified.")
        except Exception as e:
            log.error("❌ Failed to verify Google Slides connection.")
            log.error(str(e))
            log.error('If this is a public network computer run tomolog using the --public option!')
            log.error('If this is a private network computer start SSH tunnel: ssh -D 1081 user@public.machine.ip -N')
            exit()
        snippets = google_snippets.SlidesSnippets(slides, creds)
        return snippets

def extract_presentation_id(slide_url):
    match = re.search(r"/presentation/d/([a-zA-Z0-9_-]+)", slide_url)
    return match.group(1) if match else None