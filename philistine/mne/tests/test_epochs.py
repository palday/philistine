# -*- coding: utf-8 -*-
# Copyright (C) 2018 Phillip Alday <phillip.alday@mpi.nl>
# License: BSD (3-clause)
"""Epoch manipulation tests."""

from __future__ import division, print_function

import mne

from nose.tools import assert_raises, assert_true

import numpy as np
from numpy.testing import assert_array_equal

import pandas as pd

from philistine.mne import abs_threshold, retrieve
from philistine.mne.utils import _generate_raw


def test_retrieve():
    """Test retrieval functionality."""
    raw = _generate_raw(n_chan=1, iaf=11.25)
    raw.add_events(np.array([[1, 0, 255], [10, 0, 255]]))
    epochs = mne.Epochs(raw, mne.find_events(raw), tmin=0.0, preload=True)

    # TODO: test multiple time windows
    # TODO: test different summary functions
    # TODO: test scale_times

    windows = dict(onset=(-50, 50))

    # without items
    df1 = retrieve(epochs, windows)
    df2 = pd.DataFrame({'channel': {0: '0', 1: 'STI 014', 2: '0', 3: 'STI 014'},  # noqa: E501
                        'condition': {0: '255', 1: '255', 2: '255', 3: '255'},  # noqa: E501
                        'epoch': {0: 0, 1: 0, 2: 1, 3: 1},
                        'mean': {0: 4.4267676108015275,
                         1: 39.23076923076923,
                         2: -9.852708759493767,
                         3: 19.615384615384617},
                        'win': {0: '-50..50', 1: '-50..50', 2: '-50..50', 3: '-50..50'},  # noqa: E501
                        'wname': {0: 'onset', 1: 'onset', 2: 'onset', 3: 'onset'}})  # noqa: E501

    assert_true(np.all(df1.eq(df2)))

    # with items
    items = np.array(['A', 'B'])
    df1 = retrieve(epochs, windows, items=items)
    df2 = pd.DataFrame({'channel': {0: '0', 1: 'STI 014', 2: '0', 3: 'STI 014'},  # noqa: E501
                        'condition': {0: '255', 1: '255', 2: '255', 3: '255'},  # noqa: E501
                        'epoch': {0: 0, 1: 0, 2: 1, 3: 1},
                        'item': {0: 'A', 1: 'A', 2: 'B', 3: 'B'},
                        'mean': {0: 4.4267676108015275,
                         1: 39.23076923076923,
                         2: -9.852708759493767,
                         3: 19.615384615384617},
                        'win': {0: '-50..50', 1: '-50..50', 2: '-50..50', 3: '-50..50'},  # noqa: E501
                        'wname': {0: 'onset', 1: 'onset', 2: 'onset', 3: 'onset'}})  # noqa: E501

    assert_true(np.all(df1.eq(df2)))

    # incorrect shape
    items = np.array(['A', 'B', 'too many'])
    assert_raises(ValueError, retrieve, epochs, windows, items=items)

    # incorrect type
    items = 'wrong'
    assert_raises(ValueError, retrieve, epochs, windows, items=items)


def test_abs_treshold():
    """Test absolute-valued based thresholding."""
    raw = _generate_raw(n_chan=1, iaf=11.25)
    raw.add_events(np.array([[1, 0, 255], [10, 0, 255]]))
    epochs = mne.Epochs(raw, mne.find_events(raw), tmin=0.0, preload=True)

    # guarantee that the first epoch doesn't exceed threshold
    epochs._data[0, ...] = 0

    threshold = 1e-6
    target_mask = [False, True]
    # general functionality
    assert_array_equal(abs_threshold(epochs, threshold), target_mask)

    # catch positive values exceeding threshold
    epochs._data = np.abs(epochs._data)
    assert_array_equal(abs_threshold(epochs, threshold), target_mask)

    # catch negative values exceeding threshold
    epochs._data = -np.abs(epochs._data)
    assert_array_equal(abs_threshold(epochs, threshold), target_mask)
