# -*- coding: utf-8 -*-
# Copyright (C) 2018 Phillip Alday <phillip.alday@mpi.nl>
# License: BSD (3-clause)
"""Utility functions not further classified."""

from __future__ import division, print_function


def invert_dict(d):
    """Return an 'inverted' dictionary, swapping keys against values.

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
    If the key-mapping is not one-to-one, then the dictionary is not
    invertible and a ValueError is thrown.
    """
    inv_d = dict((d[key], key) for key in d)
    if len(d) != len(inv_d):
        raise ValueError('Key-value mapping is not one-to-one.')

    return inv_d
