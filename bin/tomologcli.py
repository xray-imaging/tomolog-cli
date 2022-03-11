import os
import sys
import pathlib 
import argparse

from datetime import datetime

from tomolog_cli import log
from tomolog_cli import config
from tomolog_cli import TomoLog

# log = logging.getLogger(__name__)


def init(args):
    if not os.path.exists(str(args.config)):
        config.write(args.config)
    else:
        log.error("{0} already exists".format(args.config))


def run_status(args):
    config.log_values(args)


def run_log(args):

    log.warning('publication start')
    file_path = pathlib.Path(args.file_name)
    if file_path.is_file():
        log.info("publishing a single file: %s" % args.file_name)
        TomoLog().run_log(args)
    elif file_path.is_dir():
        log.info("publishing a multiple files in: %s" % args.file_name)
        top = os.path.join(args.file_name, '')
        h5_file_list = list(filter(lambda x: x.endswith(('.h5', '.hdf', 'hdf5')), os.listdir(top)))
        if (h5_file_list):
            h5_file_list.sort()
            log.info("found: %s" % h5_file_list) 
            index=0
            for fname in h5_file_list:
                args.file_name = top + fname
                log.warning("  *** file %d/%d;  %s" % (index, len(h5_file_list), fname))
                index += 1
                TomoLog().run_log(args)
        else:
            log.error("directory %s does not contain any file" % args.file_name)
    else:
        log.error("directory or File Name does not exist: %s" % args.file_name)

    config.write(args.config, args, sections=config.PARAMS)

def main():

    # make sure logs directory exists
    logs_home = os.path.join(str(pathlib.Path.home()), 'logs')

    # logs_home = args.logs_home
    if not os.path.exists(logs_home):
        os.makedirs(logs_home)

    lfname = os.path.join(logs_home, 'tomolog_' +
                          datetime.strftime(datetime.now(), "%Y-%m-%d_%H_%M_%S") + '.log')
    # log_level = 'DEBUG' if args.verbose else "INFO"
    log.setup_custom_logger(lfname)
    log.info("Started tomolog")
    log.info("Saving log at %s" % lfname)

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', **config.SECTIONS['general']['config'])
    params = config.PARAMS

    cmd_parsers = [
        ('init',        init,            (),    "Create configuration file"),
        ('run',         run_log,         params,"Run data logging to google slides"),
        ('status',      run_status,      params,"Show the tomolog status"),
    ]

    subparsers = parser.add_subparsers(title="Commands", metavar='')

    for cmd, func, sections, text in cmd_parsers:
        cmd_params = config.Params(sections=sections)
        cmd_parser = subparsers.add_parser(
            cmd, help=text, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        cmd_parser = cmd_params.add_arguments(cmd_parser)
        cmd_parser.set_defaults(_func=func)

    args = config.parse_known_args(parser, subparser=True)



    # make sure token directory exists
    token_home = args.token_home
    if not os.path.exists(token_home):
        os.makedirs(token_home)

    try:
        args._func(args)
    except RuntimeError as e:
        log.error(str(e))
        sys.exit(1)


if __name__ == '__main__':
    main()
