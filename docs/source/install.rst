============
Installation
============

First, you must have `Conda <https://docs.conda.io/en/latest/miniconda.html>`_
installed and create a dedicated conda environment::

    (base)$ conda create -n tomolog python=3.9

and::

    (base)$ conda activate tomolog
    (tomolog)$ 

then install all `requirements <https://github.com/xray-imaging/mosaic/blob/main/requirements.txt>`_ with::

    (tomolog)$ conda install  -c conda-forge python=3.9 dropbox google-api-python-client matplotlib dxchange dxfile python-dotenv opencv matplotlib-scalebar


install meta 
::

    (tomolog)$ git clone https://github.com/xray-imaging/meta.git
    (tomolog)$ cd meta
    (tomolog)$ python setup.py install


and install tomolog
::

    (tomolog)$ git clone https://github.com/xray-imaging/tomolog-cli.git
    (tomolog)$ cd tomolog
    (tomolog)$ python setup.py install


Requirements
============

Please install all the packages listed in `requirements file <https://github.com/xray-imaging/tomolog-cli/blob/main/envs/requirements.txt>`_. 

**tomolog** also requires access tokens from dropbox and google services.

Dropbox
-------

Go to `dropbox developer site <https://www.dropbox.com/lp/developers>`_ , login using your google credentials and select "Create an App":


.. image:: img/dropbox_00.png
   :width: 720px
   :alt: project

Take the App key and App secret from the Settings tab:

.. image:: img/dropbox_01.png
   :width: 720px
   :alt: project

an copy them in a file in your home directory called:

::

    $ ~/.tomologenv 

    APP_KEY=....
    APP_SECRET=....


Set the following permissions:

.. image:: img/dropbox_01.png
   :width: 720px
   :alt: project

Google
------

https://developers.google.com/workspace/guides/create-project

go to: 
https://developers.google.com/workspace/guides/enable-apis

and enable google slides

got to: https://developers.google.com/workspace/guides/auth-overview


Go to `google developer site <https://console.cloud.google.com/>`_ and 

- create a new project

.. image:: img/google_01.png
   :width: 720px
   :alt: project

.. image:: img/google_02.png
   :width: 720px
   :alt: project

- select it and then go to Create Credentials / Service Management API / User data

.. image:: img/google_03.png
   :width: 720px
   :alt: project

.. image:: img/google_04.png
   :width: 720px
   :alt: project

.. image:: img/google_05.png
   :width: 720px
   :alt: project

.. image:: img/google_06.png
   :width: 720px
   :alt: project


- copy the authorization token in a file called::

    $ ~/tokens/google_token.json

