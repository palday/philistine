# -*- coding: utf-8 -*-
# Copyright (C) 2023 Phillip Alday <me@phillipalday.com>
# License: BSD (3-clause)
"""Epoch manipulation tests."""

import mne

from nose.tools import assert_true

import numpy as np
from numpy.testing import assert_array_equal

import pandas as pd

from philistine.mne import abs_threshold, retrieve
from philistine.mne.utils import _generate_raw


def test_retrieve():
    """Test retrieval functionality."""
    raw = _generate_raw(n_chan=1, iaf=11.25)
    raw.add_events(np.array([[1, 0, 255], [10, 0, 255]]))
    epochs = mne.Epochs(raw,
                        mne.find_events(raw),
                        tmin=0.0,
                        preload=True, baseline=None)
    # TODO: test multiple time windows
    # TODO: test items
    # TODO: test different summary functions
    # TODO: test scale_times

    windows = dict(onset=(0, 50))
    means = epochs.copy().crop(0, 0.050, include_tmax=True).get_data().mean(axis=-1)  # noqa: E501
    means_vec = means.reshape(4, order='F')
    means_vec[:2] *= 1e6  # convert to µV

    df1 = retrieve(epochs, windows, time_format="ms")
    df2 = pd.DataFrame({'channel': {0: '0', 1: '0', 2: 'STI 014', 3: 'STI 014'},  # noqa: E501
                        'condition': {0: '255', 1: '255', 2: '255', 3: '255'},  # noqa: E501
                        'epoch': {0: 0, 1: 1, 2: 0, 3: 1},
                        'mean': {0: means_vec[0],
                                 1: means_vec[1],
                                 2: means_vec[2],
                                 3: means_vec[3]},
                        'win': {0: '0..50', 1: '0..50', 2: '0..50', 3: '0..50'},  # noqa: E501
                        'wname': {0: 'onset', 1: 'onset', 2: 'onset', 3: 'onset'}})  # noqa: E501

    # the split-apply-combine apparently isn't sort-order stable
    # across Pandas/Python versions?
    df1 = df1.sort_values(by=["channel", "epoch"])
    # oh floating point
    assert_true(np.all(np.isclose(df1["mean"], df2["mean"])))

    df1 = df1.drop("mean", axis=1).reset_index(inplace=False, drop=True)
    df2 = df2.drop("mean", axis=1).reset_index(inplace=False, drop=True)
    assert_true(np.all(df1.eq(df2)))


def test_abs_treshold():
    """Test absolute-valued based thresholding."""
    raw = _generate_raw(n_chan=1, iaf=11.25)
    raw.add_events(np.array([[1, 0, 255], [10, 0, 255]]))
    epochs = mne.Epochs(raw, mne.find_events(raw),
                        tmin=0.0, preload=True, baseline=None)

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
