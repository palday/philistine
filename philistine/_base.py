#! /usr/bin/env python
#
# Copyright (C) 2018 Phillip Alday <phillip.alday@mpi.nl>

from __future__ import print_function, division

def invert_dict(d):
    """Return an 'inverted' dictionary, swapping keys against values

    Parameters
    ----------
    d : dict-like
    The dictionary to invert

    Returns
    --------
    inv_d : dict()
    The inverted dictionary.

    Notes
    ------
    If the key-mapping is not one-to-one, then the dictionary is not unvertible and a ValueError is thrown.
    """

    if len(set(d.keys())) != len(set(d.values())):
        raise ValueError('Key-value mapping is not one-to-one.')

    return {d[key] for key in d}