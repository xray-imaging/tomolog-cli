=====
Usage
=====

To publish experiment log information to a google page::

   $ tomolog run --file-name /local/data/2022-03/Peters/B4_Pb_03_c_10keV_892.h5 --presentation-url https://docs.google.com/presentation/d/128c8JYiJ5EjbQhAtegYYetwDUVZILQjZ5fUIoWuR_aI/edit#slide=id.p


For help::

   $ tomolog run -h
   usage: tomolog run [-h] [--beamline {None,2-bm,7-bm,32-id}] [--doc-dir DOC_DIR] [--file-name PATH] [--max MAX] [--min MIN] [--parent-folder-id PARENT_FOLDER_ID]
                      [--presentation-url PRESENTATION_URL] [--queue QUEUE] [--config FILE] [--config-update] [--idx IDX] [--idy IDY] [--idz IDZ] [--logs-home FILE]
                      [--magnification MAGNIFICATION] [--pixel-size PIXEL_SIZE] [--save-format {tiff,h5}] [--token-home FILE] [--verbose] [--zoom ZOOM]

   optional arguments:
     -h, --help            show this help message and exit
     --beamline {None,2-bm,7-bm,32-id}
                           When set adds the beamline name as a prefix to the slack channel name (default: None)
     --doc-dir DOC_DIR     sphinx/readthedocs documentation directory where the meta data table extracted from the hdf5 file should be saved, e.g. docs/source/... (default: .)
     --file-name PATH      Name of the hdf file (default: .)
     --max MAX             Maximum threshold value for reconstruction visualization (default: 0.0)
     --min MIN             Minimum threshold value for reconstruction visualization (default: 0.0)
     --parent-folder-id PARENT_FOLDER_ID
                           Google public folder ID. Create a public forlder on the google app drive and extract it from the share link: https://drive.google.com/drive/folders/<parent-
                           folder-id>?... (default: None)
     --presentation-url PRESENTATION_URL
                           Google presention. Create a public google slide presentation. (default: None)
     --queue QUEUE         set to separate dropbox files in case or running multiple instance of tomolog-cli (default: 0)
     --config FILE         File name of configuration file (default: /Users/decarlo/logs/tomolog.conf)
     --config-update       When set, the content of the config file is updated using the current params values (default: False)
     --idx IDX             Id of x slice for reconstruction visualization (default: -1)
     --idy IDY             Id of y slice for reconstruction visualization (default: -1)
     --idz IDZ             Id of z slice for reconstruction visualization (default: -1)
     --logs-home FILE      Log file directory (default: /Users/decarlo/logs)
     --magnification MAGNIFICATION
                           Lens magnification. Overwrite value to be used in case in missing from the hdf file (default: -1)
     --pixel-size PIXEL_SIZE
                           Detector pixel size. Overwrite value to be used in case in missing from the hdf file (default: -1)
     --save-format {tiff,h5}
                           Reconstruction save format (default: tiff)
     --token-home FILE     Token file directory (default: /Users/decarlo/tokens)
     --verbose             Verbose output (default: False)
     --zoom ZOOM           zoom for reconstruction, e.g. [1,2,4] (default: [1,2,4])

For other options::

   $ tomolog -h
   usage: tomolog [-h] [--config FILE]  ...

   optional arguments:
     -h, --help     show this help message and exit
     --config FILE  File name of configuration file

   Commands:
     
       init         Create configuration file
       run          Run data logging to google slides
       status       Show the tomolog status
