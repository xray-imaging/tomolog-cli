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
import sys
import pathlib
import logging
import inspect
import warnings
import argparse
import configparser

from copy import copy
from pathlib import Path
from collections import OrderedDict

from tomolog_cli import log

LOGS_HOME = os.path.join(str(pathlib.Path.home()), 'logs')
CONFIG_FILE_NAME = os.path.join(str(pathlib.Path.home()), 'logs', 'tomolog.conf')
TOKEN_HOME      = os.path.join(str(pathlib.Path.home()), 'tokens')

def default_parameter(func, param):
    """Get the default value for a function parameter.

    For a given function *func*, introspect the function and return
    the default value for the function parameter named *param*.

    Return
    ======
    default_val
      The default value for the parameter.

    Raises
    ======
    RuntimeError
      Raised if the function *func* has no default value for the
      requested parameter *param*.

    """
    # Retrieve the function parameter by introspection
    try:
        sig = inspect.signature(func)
        _param = sig.parameters[param]
    except TypeError as e:
        warnings.warn(str(e))
        log.warning(str(e))
        return None
    # Check if a default value exists
    if _param.default is _param.empty:
        # No default is listed in the function, so throw an exception
        msg = ("No default value given for parameter *{}* of callable {}."
               "".format(param, func))
        raise RuntimeError(msg)
    else:
        # Retrieve and return the parameter's default value
        return _param.default


SECTIONS = OrderedDict()


SECTIONS['general'] = {
    'config': {
        'default': CONFIG_FILE_NAME,
        'type': str,
        'help': "File name of configuration file",
        'metavar': 'FILE'},
    'logs-home': {
        'default': LOGS_HOME,
        'type': str,
        'help': "Log file directory",
        'metavar': 'FILE'},
    'token-home': {
        'default': TOKEN_HOME,
        'type': str,
        'help': "Token file directory",
        'metavar': 'FILE'},    
    'verbose': {
        'default': False,
        'help': 'Verbose output',
        'action': 'store_true'},
    'config-update': {
        'default': False,
        'help': 'When set, the content of the config file is updated using the current params values',
        'action': 'store_true'},
    'public': {
        'default': False,
        'help': 'Set to run tomolog on a public network computer. When not set the assumption is that tomolog is running on a private network',
        'action': 'store_true'},
    'port': {
        'default': 1080,
        'type': int,
        'help': 'Port for tunneling'},
    'idx': {
        'type': int,
        'default': -1,
        'help': "Id of x slice for reconstruction visualization"},
    'idy': {
        'type': int,
        'default': -1,
        'help': "Id of y slice for reconstruction visualization"},
    'idz': {
        'type': int,
        'default': -1,
        'help': "Id of z slice for reconstruction visualization"},    
    'nproc': {
        'type': int,
        'default': 8,
        'help': "Number of threads to read tiff"},
    'save-format': {
        'default': 'tiff',
        'type': str,
        'help': "Reconstruction save format",
        'choices': ['tiff','h5']},    
    'magnification': {
        'type': float,
        'default': -1,
        'help': "Lens magnification. Overwrite value  to be used in case in missing from the hdf file"},
    'pixel-size': {
        'type': float,
        'default': -1,
        'help': "Detector pixel size. Overwrite value  to be used in case in missing from the hdf file"},
    'zoom': {
        'type': str,
        'default': '[1,2,4]',
        'help': "zoom for reconstruction, e.g. [1,2,4]"},
}

SECTIONS['file-reading'] = {
    'beamline': {
        'default': 'None',
        'type': str,
        'help': "When set adds the beamline name as a prefix to the slack channel name",
        'choices': ['None','2-bm', '7-bm', '32-id']},    
    'file-name': {
        'default': '.',
        'type': Path,
        'help': "Name of the hdf file",
        'metavar': 'PATH'},
    'doc-dir': {
        'type': str,
        'default': '.',
        'help': "sphinx/readthedocs documentation directory where the meta data table extracted from the hdf5 file should be saved, e.g. docs/source/..."},
}

SECTIONS['parameters'] = {
    'max': {
        'type': float,
        'default': 0.0,
        'help': "Maximum threshold value for reconstruction visualization"},
    'min': {
        'type': float,
        'default': 0.0,
        'help': "Minimum threshold value for reconstruction visualization"},
    'presentation-url': {
        'default': None,
        'type': str,
        'help': "Google presention. Create a public google slide presentation."},
    'cloud-service': {
        'default': 'imgur',
        'type': str,
        'help': "cloud service where generated images will be uploaded. Google API retrieves images by url before publishing on slides",
        'choices': ['imgur','globus', 'aps']},    
    'count': {
        'type': int,
        'default': 0,
        'help': "counter is incremented at each google slide generated. Conter is appended to the url to generate a unique url as required by some service"},
}

PARAMS = ('file-reading', 'parameters')
NICE_NAMES = ('General', 'File reading', 'Parameters')


def get_config_name():
    """Get the command line --config option."""
    name = CONFIG_FILE_NAME
    for i, arg in enumerate(sys.argv):
        if arg.startswith('--config'):
            if arg == '--config':
                return sys.argv[i + 1]
            else:
                name = sys.argv[i].split('--config')[1]
                if name[0] == '=':
                    name = name[1:]
                return name

    return name


def parse_known_args(parser, subparser=False):
    """
    Parse arguments from file and then override by the ones specified on the
    command line. Use *parser* for parsing and is *subparser* is True take into
    account that there is a value on the command line specifying the subparser.
    """
    if len(sys.argv) > 1:
        subparser_value = [sys.argv[1]] if subparser else []
        config_values = config_to_list(config_name=get_config_name())
        values = subparser_value + config_values + sys.argv[1:]
    else:
        values = ""

    return parser.parse_known_args(values)[0]


def config_to_list(config_name=CONFIG_FILE_NAME):
    """
    Read arguments from config file and convert them to a list of keys and
    values as sys.argv does when they are specified on the command line.
    *config_name* is the file name of the config file.
    """
    result = []
    config = configparser.ConfigParser()

    if not config.read([config_name]):
        return []

    for section in SECTIONS:
        for name, opts in ((n, o) for n, o in SECTIONS[section].items() if config.has_option(section, n)):
            value = config.get(section, name)

            if value != '' and value != 'None':
                action = opts.get('action', None)

                if action == 'store_true' and value == 'True':
                    # Only the key is on the command line for this action
                    result.append('--{}'.format(name))

                if not action == 'store_true':
                    if opts.get('nargs', None) == '+':
                        result.append('--{}'.format(name))
                        result.extend((v.strip() for v in value.split(',')))
                    else:
                        result.append('--{}={}'.format(name, value))

    return result


class Params(object):
    def __init__(self, sections=()):
        self.sections = sections + ('general', )

    def add_parser_args(self, parser):
        for section in self.sections:
            for name in sorted(SECTIONS[section]):
                opts = SECTIONS[section][name]
                parser.add_argument('--{}'.format(name), **opts)

    def add_arguments(self, parser):
        self.add_parser_args(parser)
        return parser

    def get_defaults(self):
        parser = argparse.ArgumentParser()
        self.add_arguments(parser)

        return parser.parse_args('')


def write(config_file, args=None, sections=None):
    """
    Write *config_file* with values from *args* if they are specified,
    otherwise use the defaults. If *sections* are specified, write values from
    *args* only to those sections, use the defaults on the remaining ones.
    """
    config = configparser.ConfigParser()

    for section in SECTIONS:
        config.add_section(section)
        for name, opts in SECTIONS[section].items():
            if args and sections and section in sections and hasattr(args, name.replace('-', '_')):
                value = getattr(args, name.replace('-', '_'))

                if isinstance(value, list):
                    value = ', '.join(value)
            else:
                value = opts['default'] if opts['default'] is not None else ''

            prefix = '# ' if value == '' else ''

            if name != 'config':
                config.set(section, prefix + name, str(value))

    with open(config_file, 'w') as f:
        config.write(f)


def show_config(args):
    """Log all values set in the args namespace.
    Arguments are grouped according to their section and logged alphabetically
    using the DEBUG log level thus --verbose is required.
    """
    args = args.__dict__

    log.warning('status start')
    for section, name in zip(SECTIONS, NICE_NAMES):
        entries = sorted(
            (k for k in args.keys() if k.replace('_', '-') in SECTIONS[section]))
        if entries:
            for entry in entries:
                value = args[entry] if args[entry] != None else "-"
                log.info("  {:<16} {}".format(entry, value))

    log.warning('status end')


def log_values(args):
    """Log all values set in the args namespace.
    Arguments are grouped according to their section and logged alphabetically
    using the DEBUG log level thus --verbose is required.
    """
    args = args.__dict__

    log.warning('status start')
    for section, name in zip(SECTIONS, NICE_NAMES):
        entries = sorted(
            (k for k in args.keys() if k.replace('_', '-') in SECTIONS[section]))

        # print('log_values', section, name, entries)
        if entries:
            log.info(name)

            for entry in entries:
                value = args[entry] if args[entry] is not None else "-"
                if (value == 'none'):
                    log.warning("  {:<16} {}".format(entry, value))
                elif (value is not False):
                    log.info("  {:<16} {}".format(entry, value))
                elif (value is False):
                    log.warning("  {:<16} {}".format(entry, value))

    log.warning('status end')
