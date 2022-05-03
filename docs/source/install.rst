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

Please install all the packages listed in `requirements file <https://github.com/nikitinvv/tomolog-cli/blob/main/envs/requirements.txt>`_. 

**tomolog** also requires access tokens from dropbox and google services.

Dropbox
-------

Go to `dropbox developer site <https://www.dropbox.com/lp/developers>`_ and select "Create an App". Login using your google credentials and create a new App with the following permissions:

.. image:: img/dropbox_01.png
   :width: 720px
   :alt: project

the go to the setting tab and copy the App key and App secret in a file in your home directory called:

::

    $ ~/.tomologenv 

    APP_KEY=....
    APP_SECRET=....

Google
------

Go to `google developer site <https://console.cloud.google.com/apis/dashboard?pli=1&project=usr32idc>`_ and 

- create a new project  
- select it and then go to Service Accounts/Create service account
- copy the authorization token in a file called::

    $ ~/tokens/google_token.json

