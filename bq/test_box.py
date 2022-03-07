
from __future__ import print_function

import argparse
import contextlib
import datetime
import os
import six
import sys
import time
import unicodedata
import dropbox

token = 'sl.BDRhPvDbZid3IJu40quwD4CMm46dUkgagXNdq3wLSxW9Q9jU-AA0iCjtpf_AXw8iykExIjJMnTMLEO90QagD2Vm8X4aVvFi3dUaDT7xJBXBDvDW_J1kcHaNGWJqv6af31lQCubsvXZg'
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import dropbox

class TransferData:
    def __init__(self, access_token):
        self.access_token = access_token

    def upload_file(self, file_from, file_to):
        """upload a file to Dropbox using API v2
        """
        dbx = dropbox.Dropbox('sl.BDRhPvDbZid3IJu40quwD4CMm46dUkgagXNdq3wLSxW9Q9jU-AA0iCjtpf_AXw8iykExIjJMnTMLEO90QagD2Vm8X4aVvFi3dUaDT7xJBXBDvDW_J1kcHaNGWJqv6af31lQCubsvXZg')

        with open(file_from, 'rb') as f:
            dbx.files_upload(f.read(), file_to)
        

def main():
    transferData = TransferData(token)

    file_from = 'proj_for_google.jpg'
    file_to = '/proj_for_google.jpg'  # The full path to upload the file to, including the file name

    # API v2
    transferData.upload_file(file_from, file_to)

if __name__ == '__main__':
    main()