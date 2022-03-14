============
Installation
============

First, you must have `Conda <https://docs.conda.io/en/latest/miniconda.html>`_
installed and create a dedicated conda environment::

    (base)$ conda create -n tomolog

and::

    (base)$ conda activate tomolog
    (tomolog)$ 

then install all `requirements <https://github.com/xray-imaging/mosaic/blob/main/requirements.txt>`_ with::

    (tomolog)$ conda install  -c conda-forge dxchange dxfile

and install tomolog
::

    (tomolog)$ git clone https://github.com/nikitinvv/tomolog-cli.git
    (tomolog)$ cd tomolog
    (tomolog)$ python setup.py install


Requirements
============

Please install all the packases listed in `requirements file <https://github.com/nikitinvv/tomolog-cli/blob/main/env/requirements.txt>`_. 

