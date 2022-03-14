=====
Usage
=====

To publish experiment log information to a google page::

   $ tomolog run --file-name /local/data/2022-03/Peters/B4_Pb_03_c_10keV_892.h5 --presentation-url https://docs.google.com/presentation/d/128c8JYiJ5EjbQhAtegYYetwDUVZILQjZ5fUIoWuR_aI/edit#slide=id.p


For help::

   $ tomolog run -h
   usage: tomolog run [-h] [--file-name PATH] [--PV-prefix PV_PREFIX] [--beamline {None,2-bm,7-bm,32-id}] [--idx IDX] [--idy IDY] [--idz IDZ] [--max MAX] [--min MIN]
                      [--presentation-url PRESENTATION_URL] [--rec-type {recgpu,rec}] [--config FILE] [--config-update] [--double-fov] [--logs-home FILE] [--token-home FILE]
                      [--verbose]

   optional arguments:
     -h, --help            show this help message and exit
     --file-name PATH      Name of the hdf file (default: .)
     --PV-prefix PV_PREFIX
                           PV prefix for camera (default: 32idcSP1:)
     --beamline {None,2-bm,7-bm,32-id}
                           Customized the goodle slide to the beamline selected (default: 32-id)
     --idx IDX             Id of x slice for reconstruction visualization (default: -1)
     --idy IDY             Id of y slice for reconstruction visualization (default: -1)
     --idz IDZ             Id of z slice for reconstruction visualization (default: -1)
     --max MAX             Maximum threshold value for reconstruction visualization (default: 0.0)
     --min MIN             Minimum threshold value for reconstruction visualization (default: 0.0)
     --presentation-url PRESENTATION_URL
                           Google presention url (default: None)
     --rec-type {recgpu,rec}
                           Specify the prefix of the recon folder (default: recgpu)
     --config FILE         File name of configuration file (default: /home/beams/FAST/logs/tomolog.conf)
     --config-update       When set, the content of the config file is updated using the current params values (default: False)
     --double-fov          Set to true for 0-360 data sets (default: False)
     --logs-home FILE      Log file directory (default: /home/beams/FAST/logs)
     --token-home FILE     Token file directory (default: /home/beams/FAST/tokens)
     --verbose             Verbose output (default: False)

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
