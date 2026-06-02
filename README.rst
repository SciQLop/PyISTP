==================
Python ISTP loader
==================


.. image:: https://img.shields.io/pypi/v/pyistp.svg
        :target: https://pypi.python.org/pypi/pyistp

.. image:: https://readthedocs.org/projects/pyistp/badge/?version=latest
        :target: https://pyistp.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status




An easy to use loader for ISTP-compliant CDF and NetCDF files, as commonly
distributed by CDAWeb, AMDA and other space-physics data archives.

Rather than exposing raw variables, PyISTP reads the ISTP metadata
conventions (``VAR_TYPE``, ``DEPEND_n``, ``*_PTR``, ``LABLAXIS``, ...) and
hands you each data variable together with its resolved axes (time and other
support variables), labels and attributes.


* Free software: GNU General Public License v3
* Documentation: https://pyistp.readthedocs.io.


Features
--------

* Loads ISTP-compliant **CDF** files (via pycdfpp_ by default, or spacepy_).
* Loads ISTP-compliant **NetCDF** files (via netCDF4_).
* Reads from a file path or directly from an in-memory ``bytes`` buffer
  (handy for data fetched over HTTP).
* Supports a separate **master/skeleton file** holding the metadata while the
  values come from the data file.
* Automatically resolves ``DEPEND_n`` support variables into axes, with
  fallback to the master file.
* Converts CDF epoch types and NetCDF CF/Unix time variables to
  ``numpy.datetime64[ns]``.
* Lazily materializes variable values (the array is read on first access).
* Tolerates many non-ISTP-compliant files (CDAWeb, Cluster/CSA) with
  warnings rather than failures.


Installation
------------

.. code-block:: console

    pip install pyistp

The default CDF backend is pycdfpp_; spacepy_ is used as a fallback if
available. NetCDF support requires netCDF4_. To force a specific CDF backend,
set the ``PYISTP_CDFLIB`` environment variable to ``pycdfpp`` or ``spacepy``.


Usage
-----

Load a file and inspect its data variables:

.. code-block:: python

    import pyistp

    istp = pyistp.load(file="wi_k0_mfi_20220101_v01.cdf")

    istp.data_variables()          # -> ['BGSEc', 'BF1', 'PGSM', ...]
    istp.attributes()              # global attribute names

    var = istp.data_variable("BGSEc")
    var.values                     # numpy array of values (read lazily)
    var.axes[0].values             # the time axis (numpy.datetime64[ns])
    var.attributes                 # variable attributes
    var.labels                     # component labels, if any

Load directly from a buffer, for instance data fetched over HTTP:

.. code-block:: python

    import requests, pyistp

    raw = requests.get(
        "https://spdf.gsfc.nasa.gov/pub/data/themis/thc/l2/efi/2020/"
        "thc_l2_efi_20200101_v01.cdf").content
    istp = pyistp.load(buffer=raw)

    var = istp.data_variable("thc_eff_dot0_gsm")
    import matplotlib.pyplot as plt
    plt.plot(var.axes[0].values, var.values)

Use a separate master/skeleton file for the metadata:

.. code-block:: python

    istp = pyistp.load(file="data.cdf", master_file="skeleton.cdf")
    # or from buffers:
    istp = pyistp.load(buffer=data_bytes, master_buffer=skeleton_bytes)


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _pycdfpp: https://github.com/SciQLop/pycdfpp
.. _spacepy: https://github.com/spacepy/spacepy
.. _netCDF4: https://unidata.github.io/netcdf4-python/
