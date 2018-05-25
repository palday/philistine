# -*- coding: utf-8 -*-
# Copyright (C) 2018 Phillip Alday <phillip.alday@mpi.nl>
# License: BSD (3-clause)
"""Savitzky-Golaf IAF tests."""

from __future__ import division, print_function

from nose.tools import assert_sequence_equal

from philistine.mne import attenuation_iaf, savgol_iaf
from philistine.mne.utils import _generate_raw


def test_basic_sgf_iaf():
    """Test basic Savitzky-Golay filtered IAF functionality."""
    raw = _generate_raw(iaf=11.25)

    # automatically determined bounds
    iaf = savgol_iaf(raw)
    assert_sequence_equal(iaf, (11.25, 11.25, (9.25, 13.)))

    # user set bounds
    iaf = savgol_iaf(raw, fmin=7., fmax=13., resolution=1., polyorder=4,
                     window_length=5)
    assert_sequence_equal(iaf, (11., 11., (7., 13.)))


def test_attenuation_sgf_iaf():
    """Test attenuation Savitzky-Golay filtered IAF functionality."""
    raw = _generate_raw(iaf=11.25)
    raw2 = _generate_raw(iaf=35)
    # automatically determined bounds
    iaf = attenuation_iaf([raw, raw2])
    assert_sequence_equal(iaf, (11.25, 11.25, (9.25, 13.)))

    # user set bounds
    iaf = attenuation_iaf([raw, raw2], fmin=7., fmax=13., resolution=1.,
                          polyorder=4, window_length=5)
    assert_sequence_equal(iaf, (11., 11., (7., 13.)))

    # applying SGF at different times
    iaf = attenuation_iaf([raw, raw2], fmin=7., fmax=13., resolution=1.,
                          polyorder=4, window_length=5, savgol='each')
    assert_sequence_equal(iaf, (11., 11., (7., 13.)))

    iaf = attenuation_iaf([raw, raw2], fmin=7., fmax=13., resolution=1.,
                          polyorder=4, window_length=5, savgol='diff')
    assert_sequence_equal(iaf, (11., 11., (7., 13.)))
