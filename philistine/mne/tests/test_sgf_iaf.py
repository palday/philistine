# -*- coding: utf-8 -*-
# Copyright (C) 2023 Phillip Alday <me@phillipalday.com>
# License: BSD (3-clause)
"""Savitzky-Golaf IAF tests."""

from nose.tools import assert_raises, assert_sequence_equal

from philistine.mne import attenuation_iaf, savgol_iaf
from philistine.mne.utils import _generate_raw


def test_basic_sgf_iaf():
    """Test basic Savitzky-Golay filtered IAF functionality."""
    raw = _generate_raw(iaf=11.25)
    raw_flat = raw.copy()
    raw_flat._data *= 0

    # user set bounds
    iaf = savgol_iaf(raw, fmin=7., fmax=13., resolution=1., polyorder=4,
                     window_length=5)
    assert_sequence_equal(iaf, (11., 11., (7., 13.)))

    iaf = savgol_iaf(raw, fmin=7., fmax=13., resolution=1., polyorder=4,
                     window_length=5, pink_max_r2=0.)
    assert_sequence_equal(iaf, (None, None, (7., 13.)))

    iaf = savgol_iaf(raw_flat, fmin=7., fmax=13.)
    assert_sequence_equal(iaf, (None, None, (7., 13.)))

    # automatically determined bounds
    iaf = savgol_iaf(raw)
    assert_sequence_equal(iaf, (11.25, 11.25, (9.25, 13.)))

    iaf = savgol_iaf(raw, fmin=7.)
    assert_sequence_equal(iaf, (11.25, 11.25, (7., 12.75)))

    iaf = savgol_iaf(raw, fmax=10.)
    assert_sequence_equal(iaf, (10.0, 10.0, (9.5, 10.)))

    # should fail on a flat line ...
    assert_raises(ValueError, savgol_iaf, raw_flat, resolution=1.)


def test_attenuation_sgf_iaf():
    """Test attenuation Savitzky-Golay filtered IAF functionality."""
    raw = _generate_raw(iaf=11.25)
    raw2 = _generate_raw(iaf=35)
    # automatically determined bounds
    iaf = attenuation_iaf([raw, raw2])
    assert_sequence_equal(iaf, (11.25, 11.25, (9.25, 13.)))

    iaf = attenuation_iaf([raw, raw2], fmin=7.)
    assert_sequence_equal(iaf, (11.25, 11.25, (7., 12.75)))

    iaf = attenuation_iaf([raw, raw2], fmax=10.)
    # flat minima and argrel
    assert_sequence_equal(iaf, (10.0, 9.75, (9.5, 10.)))

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

    # flat line
    iaf = attenuation_iaf([raw, raw], fmin=7., fmax=13.)
    assert_sequence_equal(iaf, (None, None, (7., 13.)))

    iaf = attenuation_iaf([raw, raw2], fmin=7., fmax=13., flat_max_r=0)
    assert_sequence_equal(iaf, (None, None, (7., 13.)))
