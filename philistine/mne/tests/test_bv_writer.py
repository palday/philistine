# -*- coding: utf-8 -*-
# Copyright (C) 2018 Phillip Alday <phillip.alday@mpi.nl>
# License: BSD (3-clause)
"""BrainVision Writer tests."""

from __future__ import division, print_function

import os
from shutil import rmtree

import mne

from nose.tools import assert_equal

from numpy.testing import assert_allclose

from philistine.mne.io import write_raw_brainvision
from philistine.mne.utils import _generate_raw, _mktmpdir

# TODO: events of all types (stim channel, extra events, no events,
#       various methods of passing events)
# TODO: filter the generated raw and test high and lowpass
# TODO: non-integer sfreq, sfreq in powers of 2 (256,512,1024,2048)


def test_bv_writer_events():
    """Test that a write-read cycle produces identical Raws."""
    raw = _generate_raw()
    tmpdir = _mktmpdir()

    fname = os.path.join(tmpdir, "philistine.vhdr")

    write_raw_brainvision(raw, fname, events=True)
    write_raw_brainvision(raw, fname, events=False)

    rmtree(tmpdir)


def test_bv_writer_oi_cycle():
    """Test that a write-read cycle produces identical Raws."""
    raw = _generate_raw()
    tmpdir = _mktmpdir()

    fname = os.path.join(tmpdir, "philistine.vhdr")

    write_raw_brainvision(raw, fname)

    raw_written = mne.io.read_raw_brainvision(fname, preload=True)

    # sfreq
    assert_equal(raw.info['sfreq'], raw_written.info['sfreq'])
    # events
    # currently disabled as events aren't created ....
    # assert_equal(mne.find_events(raw), mne.find_events(raw_written))

    # ditch the stim channel
    raw_written = raw_written.copy().pick_types(eeg=True, stim=False)

    # data
    assert_allclose(raw._data, raw_written._data)
    # channels
    assert_equal(raw.ch_names, raw_written.ch_names)
    # filters
    assert_equal(raw.info['lowpass'], raw_written.info['lowpass'])
    assert_equal(raw.info['highpass'], raw_written.info['highpass'])

    rmtree(tmpdir)
