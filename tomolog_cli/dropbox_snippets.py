import dropbox


class DropboxSnippets(object):
    def __init__(self, service):
        self.service = service
        
    def upload(self,fname):
        with open(fname, 'rb') as f:
            self.service.files_upload(f.read(), '/'+fname, dropbox.files.WriteMode.overwrite)
            proj_url = self.service.files_get_temporary_link('/'+fname).link
            return proj_url