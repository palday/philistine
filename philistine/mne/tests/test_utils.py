# -*- coding: utf-8 -*-
# Copyright (C) 2018 Phillip Alday <phillip.alday@mpi.nl>
# License: BSD (3-clause)
"""Internal utility tests."""

from __future__ import division, print_function

from mne.channels import read_montage

from nose.tools import assert_equal, assert_sequence_equal, assert_true

import numpy as np

from philistine.mne.utils import _generate_raw

# TODO: events of all types (stim channel, extra events, no events,
#       various methods of passing events)
# TODO: filter the generated raw and test high and lowpass
# TODO: non-integer sfreq, sfreq in powers of 2 (256,512,1024,2048)


def test_gen_raw_sfreq():
    """Test that _generate_raw responds to sfreq."""
    raw = _generate_raw(sfreq=100.)

    assert_equal(raw.info['sfreq'], 100.)

    raw = _generate_raw(sfreq=256.)

    assert_equal(raw.info['sfreq'], 256.)


def test_gen_raw_ch():
    """Test that _generate_raw responds to channel settings."""
    raw = _generate_raw(duration=1, n_chan=1)

    assert_sequence_equal(raw.ch_names, ['0', 'STI 014'])

    raw = _generate_raw(duration=1, n_chan=1, ch_names=['bob'])

    assert_sequence_equal(raw.ch_names, ['bob', 'STI 014'])

    raw = _generate_raw(duration=1, n_chan=1, ch_names='standard_1020')
    montage = read_montage('standard_1020')
    raw = raw.pick_types(eeg=True)
    assert_true(np.all([ch in montage.ch_names for ch in raw.ch_names]))
