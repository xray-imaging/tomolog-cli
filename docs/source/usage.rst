=====
Usage
=====

To publish experiment log information to a google page::

   $ tomolog run --file-name /local/data/2022-03/Peters/B4_Pb_03_c_10keV_892.h5 --presentation-url https://docs.google.com/presentation/d/128c8JgsiJ5EjbQhAtegYYetwDUVZILQjZ5fUIoWuR_aI/edit#slide=id.p


For help::

   $ tomolog run -h
   usage: tomolog run [-h] [--beamline {None,2-bm,7-bm,32-id}] [--doc-dir DOC_DIR] [--file-name PATH] [--cloud-service {imgur,globus}] [--count COUNT] [--max MAX]
                      [--min MIN] [--presentation-url PRESENTATION_URL] [--config FILE] [--config-update] [--idx IDX]
                      [--idy IDY] [--idz IDZ] [--logs-home FILE] [--magnification MAGNIFICATION] [--nproc NPROC] [--pixel-size PIXEL_SIZE] [--public]
                      [--save-format {tiff,h5}] [--token-home FILE] [--verbose] [--zoom ZOOM]

   optional arguments:
     -h, --help            show this help message and exit
     --beamline {None,2-bm,7-bm,32-id}
                           When set adds the beamline name as a prefix to the slack channel name (default: None)
     --doc-dir DOC_DIR     sphinx/readthedocs documentation directory where the meta data table extracted from the hdf5 file should be saved, e.g. docs/source/...
                           (default: .)
     --file-name PATH      Name of the hdf file (default: .)
     --cloud-service {imgur,globus}
                           cloud service where generated images will be uploaded. Google API retrieves images by url before publishing on slides (default: imgur)
     --count COUNT         counter is incremented at each google slide generated. Conter is appended to the url to generate a unique url as required by some
                           service (default: 0)
     --max MAX             Maximum threshold value for reconstruction visualization (default: 0.0)
     --min MIN             Minimum threshold value for reconstruction visualization (default: 0.0)
     --presentation-url PRESENTATION_URL
                           Google presention. Create a public google slide presentation. (default: None)
     --config FILE         File name of configuration file (default: /home/beams/2BMB/logs/tomolog.conf)
     --config-update       When set, the content of the config file is updated using the current params values (default: False)
     --idx IDX             Id of x slice for reconstruction visualization (default: -1)
     --idy IDY             Id of y slice for reconstruction visualization (default: -1)
     --idz IDZ             Id of z slice for reconstruction visualization (default: -1)
     --logs-home FILE      Log file directory (default: /home/beams/2BMB/logs)
     --magnification MAGNIFICATION
                           Lens magnification. Overwrite value to be used in case in missing from the hdf file (default: -1)
     --nproc NPROC         Number of threads to read tiff (default: 8)
     --pixel-size PIXEL_SIZE
                           Detector pixel size. Overwrite value to be used in case in missing from the hdf file (default: -1)
     --public              Set to run tomolog on a public network computer. When not set the assumption is that tomolog is running on a private network (default:
                           False)
     --save-format {tiff,h5}
                           Reconstruction save format (default: tiff)
     --token-home FILE     Token file directory (default: /home/beams/2BMB/tokens)
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
