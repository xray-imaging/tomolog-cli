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

import socks
import socket
import requests
import subprocess
import os
import json
from time import sleep
from tomolog_cli import log

def upload(args, filename):

    # url = 'https://uploadimgur.com/api/upload'#
    url = args.url # + '_' + str(args.count)
    log.info('Uploading image to %s' % url)
    if not args.public:
        log.info("Running from a private network computer, using SOCKS5 proxy ...")
        # Monkey-patch socket to route through SOCKS5
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 1081)
        socket.socket = socks.socksocket
        # Upload the file through the SOCKS5 proxy
    else:
        log.info("Running from a public network computer ...")
    # # Upload the file through public network
    # #cmd = f"curl -X  POST {url} -F image=@{filename}"
    # #result = os.popen(cmd).read()
    # #print(result)

    # command = ["curl", "-X", "POST", url, "-F", f"image=@{filename}"]    
    # print(command)
    # result = subprocess.run(command, capture_output=True, text=True)
    # print("Status:", result.returncode)
    # print("Response:", result.stdout)
    # print("Error:", result.stderr)

    # with open(filename, "rb") as f:
    #     response = requests.post(
    #         url,
    #         headers={
    #             "Accept": "application/json",
    #             # "Content-Type": "application/octet-stream"
    #         },
    #         data=f
    #     )


    with open(filename, "rb") as f:
        response = requests.post(
            url,
            files={"image": f}
        )

    print("Status code:", response.status_code)
    print("Response body:", response.text)

    # if (response.status_code == 201):
    #     log.info('*** Image upload completed')
    # else:
    #     log.error('*** An error occurred uploading image. Error %s' % response.status_code)
    #     exit()
    # Get final URL (mimicking curl -Ls behavior)
    headers = {
        "User-Agent": "curl/7.79.1"
    }

    # response = requests.get(url, headers=headers, allow_redirects=True, stream=True)
    if (response.status_code == 200):
        log.info('*** Image url created')


        s = response.text
        url = s.replace('{"link":"', '').replace('"}', '')
        print(url) 
        # data = json.loads(json_str)
        # url = data["link"]
        # print(url)
        # url = response.text['link']
        # print(url)
        # exit()
    else:
        log.error('*** An error occurred creating the image url. Error %s' % response.status_code)
        exit()
    response.close()  # prevent downloading the content

    args.count = args.count + 1
    return url, url


def delete(url):

    return
    #sleep(5) # make sure the image is taken by google, maybe not needed
    # command = ["curl", "-X", "DELETE", url]
    # print(command)
    # result = subprocess.run(command, capture_output=True, text=True)
    # print("Status:", result.returncode)
    # print("Response:", result.stdout)
    # print("Error:", result.stderr)
    headers = {
        "User-Agent": "curl/7.79.1"
    }

    response = requests.delete(url, headers=headers)
    if (response.status_code == 200):
        log.info('*** Delete url done')
    else:
        log.error('*** An error occurred deleting the image url. Error %s' % response.status_code)
        exit()
    response.close()  # prevent downloading the content

    # print("Delete status:", response.status_code)
    # print("Response text:", response.text)
