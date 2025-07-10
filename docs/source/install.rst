============
Installation
============

First, you must have `Conda <https://docs.conda.io/en/latest/miniconda.html>`_
installed and create a dedicated conda environment::

    (base)$ conda create -n tomolog python=3.9

and::

    (base)$ conda activate tomolog
    (tomolog)$ 

Requirements
============

Install all `required package <https://github.com/xray-imaging/mosaic/blob/main/requirements.txt>`_ with 

::

    (tomolog)$ conda install  -c conda-forge numpy google-auth-oauthlib google-api-python-client matplotlib matplotlib-scalebar h5py tifffile dxfile 


install meta 
::

    (tomolog)$ git clone https://github.com/xray-imaging/meta.git
    (tomolog)$ cd meta
    (tomolog)$ pip install .

and install tomolog
::

    (tomolog)$ git clone https://github.com/xray-imaging/tomolog-cli.git
    (tomolog)$ cd tomolog
    (tomolog)$ pip install .

Google
------

**tomolog** uses Google services to publish experiment metadata and images to public Google Slides. To enable this functionality, you need to create a Google Cloud project by following these steps:

Open a web browser and login as ...@gmail.com then go to `google developer site <https://console.cloud.google.com/>`_ and press "Select a project" to create a new project

.. image:: img/google_01.png
   :width: 480px
   :alt: project

.. image:: img/google_02.png
   :width: 480px
   :alt: project

Once the project is selected go to the project dashboard:

.. image:: img/google_03.png
   :width: 480px
   :alt: project

and select API & Services / Credentials

.. image:: img/google_04.png
   :width: 480px
   :alt: project

select it and then go to Create Credentials / Service account

.. image:: img/google_05.png
   :width: 480px
   :alt: project

where you enter the service account name, i.e. tomolog

.. image:: img/google_06.png
   :width: 480px
   :alt: project

Grant this service account access to project: Owner

Grant users access to this service account:: 
   
   service account user role: Google Account email: ....@gmail.com
   service account admin role: Google Account email: ....@gmail.com

Once the service account is selected you need to create the authorization key:

.. image:: img/google_07.png
   :width: 480px
   :alt: project

.. image:: img/google_08.png
   :width: 480px
   :alt: project

open the json file and copy the authorization token in a file called::

    $ ~/tokens/google_token.json

Go back to the project dashboard

.. image:: img/google_09.png
   :width: 256px
   :alt: project

and select "Go to the API overview"

.. image:: img/google_10.png
   :width: 256px
   :alt: project

and select "Enable API and Services"

.. image:: img/google_11.png
   :width: 480px
   :alt: project

search and add the "google slide api"

.. image:: img/google_12.png
   :width: 480px
   :alt: project

.. image:: img/google_13.png
   :width: 480px
   :alt: project

**tomolog** can now publish experiment metadata and images to any public Google Slides presentation.
