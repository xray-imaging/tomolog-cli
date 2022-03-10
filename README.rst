===========
tomolog-cli
===========

**tomolog-cli** is a command-line-interface for logging experiment data in a Google slides

.. image:: docs/source/img/slide_00.png
    :width: 60%
    :align: center

Installation
============

::

    $ git clone https://github.com/nikitinvv/tomolog-cli.git
    $ cd meta
    $ python setup.py install

in a prepared virtualenv or as root for system-wide installation.

Usage
=====

To publish experiment log information to a google page::

	$ tomolog run --file-name /local/data/2022-03/Peters/B4_Pb_03_c_10keV_892.h5 --presentation-url https://docs.google.com/presentation/d/128c8JYiJ5EjbQhAtegYYetwDUVZILQjZ5fUIoWuR_aI/edit#slide=id.p
