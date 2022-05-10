from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass
    
from tomolog_cli.config import *
from tomolog_cli.log import *
from tomolog_cli.auth import *
from tomolog_cli.google_snippets import *
from tomolog_cli.dropbox_snippets import *

from tomolog_cli.tomolog import *
from tomolog_cli.tomolog_32id import *
from tomolog_cli.utils import *