Philistine
============

A Python package for Phillip's helper and utility functions, especially for EEG and statistics.

Status
--------

(tests not yet implemented)

Overview
--------

Philistine is a collection of hopefully useful functions in Python for statistics and analysis of EEG data using existing packages in the Python ecosystem. It is not intended to be a standalone package, but rather a convenient way to distribute manipulations that I (Phillip) find useful in my own work.


This is very much alpha software under active development and the API is subject to change in a rather volatile fashion as improvements, corrections, etc. are made. The idea is provide a convenient way to redistribute functions that I (Phillip) find useful. The hope is that many of these functions are eventually integrated into packages such as `MNE <https://mne-tools.github.io>`_, `bambi <https://github.com/bambinos/bambi>`_, etc. At that point, the functions will be changed into thin wrappers for those other packages, deprecated and eventually removed.


Installation
----------------

Philistine requires a working Python interpreter (either 2.7+ or 3+).

Assuming a standard Python environment is installed on your machine (including pip), Philistine itself can be installed in one line using pip:

    python -m pip install --user --upgrade philistine

Alternatively, if you want the bleeding edge version of the package, you can install from GitLab:

    python -m pip install --user --upgrade  git+https://gitlab.com/palday/philistine.git

Dependencies should be handled automatically by pip.

Development
----------------

The primary hosting for this project is on `GitLab <https://gitlab.com/palday/philistine>`_, and issues should be raised there. A `GitHub mirror <https://github.com/palday/philistine/>`_ is provided for convenience and redundancy. Pull requests can be made on either site.