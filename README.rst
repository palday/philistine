Philistine
============

A Python package for Phillip's helper and utility functions, especially for EEG and statistics.

Status
--------

|pipeline status| |coverage report| |documentation status| |license| |pypi|

.. |pipeline status| image:: https://gitlab.com/palday/philistine/badges/master/pipeline.svg
   :target: https://gitlab.com/palday/philistine/commits/master
.. |coverage report|  image:: https://gitlab.com/palday/philistine/badges/master/coverage.svg
   :target: https://gitlab.com/palday/philistine/commits/master
.. |documentation status| image:: https://readthedocs.org/projects/philistine/badge/?version=latest
    :target: https://philistine.readthedocs.io/en/latest/?badge=latest
.. |license| image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg
    :target: https://opensource.org/licenses/BSD-3-Clause
.. |pypi| image:: https://img.shields.io/pypi/v/philistine.svg
   :target: https://pypi.org/project/philistine/

Overview
--------

Philistine is a collection of hopefully useful functions in Python for statistics and analysis of EEG data using existing packages in the Python ecosystem. It is not intended to be a standalone package, but rather a convenient way to distribute manipulations that I (Phillip) find useful in my own work.

This is very much aa hobby project developed in my free time (in a language I don't use much anymore) and the API is subject to change in a rather volatile fashion as improvements, corrections, etc. are made. The idea is provide a convenient way to redistribute functions that I (Phillip) find useful. The hope is that many of these functions are eventually integrated into packages such as `MNE <https://mne-tools.github.io>`_, `bambi <https://github.com/bambinos/bambi>`_, etc. At that point, the functions will be changed into thin wrappers for those other packages, deprecated and eventually removed.

The BV-writer functionality will likely be removed in a future release.
MNE now has an `export` module, which takes advantage of [`pybv`](https://pypi.org/project/pybv/), which in turn took the good parts of the writer here and added some active maintenance.

Installation
----------------

Philistine requires a working Python interpreter. As of version 0.2.0, this must be at least Python 3.7 for compatibility with MNE 1.3.

Assuming a standard Python environment is installed on your machine (including pip), Philistine itself can be installed in one line using pip:

::

    python -m pip install --user --upgrade philistine

Alternatively, if you want the bleeding edge version of the package, you can install from GitLab:

::

    python -m pip install --user --upgrade  git+https://gitlab.com/palday/philistine.git

Dependencies should be handled automatically by pip.

Development
----------------

The primary hosting for this project is on `GitLab <https://gitlab.com/palday/philistine>`_, and issues should be raised there. A `GitHub mirror <https://github.com/palday/philistine/>`_ is provided for convenience and redundancy. Pull requests can be made on either site.
