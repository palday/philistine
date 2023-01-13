# -*- coding: utf-8 -*-
# Copyright (C) 2023 Phillip Alday <me@phillipalday.com>
# License: BSD (3-clause)
"""BrainVision Writer tests."""

import os
from shutil import rmtree

import mne

from nose.tools import assert_equal, assert_raises

import numpy as np
from numpy.testing import assert_allclose, assert_array_equal

from philistine.mne.io import _write_bveeg_file
from philistine.mne.io import _write_vhdr_file
from philistine.mne.io import write_raw_brainvision
from philistine.mne.utils import _generate_raw, _mktmpdir

# TODO: events of all types (stim channel, extra events, no events,
#       various methods of passing events)
# TODO: filter the generated raw and test high and lowpass
# TODO: non-integer sfreq, sfreq in powers of 2 (256,512,1024,2048)


def test_bv_writer_events():
    """Test that all event options work without throwing an error."""
    raw = _generate_raw()
    tmpdir = _mktmpdir()

    fname = os.path.join(tmpdir, "philistine.vhdr")

    assert_raises(ValueError, write_raw_brainvision, raw, fname, events=[])

    write_raw_brainvision(raw, fname, events=True)
    write_raw_brainvision(raw, fname, events=False)
    write_raw_brainvision(raw, fname, events=np.array([[10, 0, 31]]))
    write_raw_brainvision(raw.pick_types(eeg=True, stim=False), fname,
                          events=True)

    rmtree(tmpdir)


def test_bv_bad_format():
    """Test that bad formats cause an error."""
    raw = _generate_raw()
    tmpdir = _mktmpdir()

    vhdr_fname = os.path.join(tmpdir, "philistine.vhdr")
    vmrk_fname = os.path.join(tmpdir, "philistine.vmrk")
    eeg_fname = os.path.join(tmpdir, "philistine.eeg")
    # events = np.array([[10, 0, 31]])

    assert_raises(ValueError, _write_vhdr_file, vhdr_fname, vmrk_fname,
                  eeg_fname, raw, orientation='bad')
    assert_raises(ValueError, _write_vhdr_file, vhdr_fname, vmrk_fname,
                  eeg_fname, raw, format='bad')

    assert_raises(ValueError, _write_bveeg_file, eeg_fname, raw,
                  orientation='bad')
    assert_raises(ValueError, _write_bveeg_file, eeg_fname, raw,
                  format='bad')

    rmtree(tmpdir)


def test_bv_writer_oi_cycle():
    """Test that a write-read cycle produces identical Raws."""
    raw = _generate_raw()
    raw.add_events(np.array([[1, 0, 82], [10, 0, 56]]))
    tmpdir = _mktmpdir()

    fname = os.path.join(tmpdir, "philistine.vhdr")

    write_raw_brainvision(raw, fname)

    raw_written = mne.io.read_raw_brainvision(fname, preload=True)

    # sfreq
    assert_equal(raw.info['sfreq'], raw_written.info['sfreq'])
    # events
    # we created events when simulating
    # but new BV reader behavior returns annotations
    read_events, _ = mne.events_from_annotations(raw_written,
                                                 event_id=lambda x: int(x[-2:]),  # noqa: E501
                                                 regexp="Stimulus")
    read_events[:, 0] += 1
    assert_array_equal(mne.find_events(raw), read_events)

    # ditch the stim channel
    raw = raw.copy().pick_types(eeg=True, stim=False)
    raw_written = raw_written.copy().pick_types(eeg=True, stim=False)

    # data
    assert_allclose(raw._data, raw_written._data)
    # channels
    assert_equal(raw.ch_names, raw_written.ch_names)
    # filters
    assert_equal(raw.info['lowpass'], raw_written.info['lowpass'])
    assert_equal(raw.info['highpass'], raw_written.info['highpass'])

    rmtree(tmpdir)
