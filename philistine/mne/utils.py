# -*- coding: utf-8 -*-
# Copyright (C) 2018 Phillip Alday <phillip.alday@mpi.nl>
# License: BSD (3-clause)
"""Utilities for (testing) MNE-based functionality."""

import warnings
from tempfile import mkdtemp

import mne

import numpy as np


def _mktmpdir():
    """Create a temporary directory for testing writers."""
    return mkdtemp(prefix='philistine_tmp_')


def _generate_raw(n_chan=16,
                  ch_names=None,
                  sfreq=250.,
                  duration=30,
                  seed=42,
                  iaf=10.141592):
    """Generate a Raw Object.

    Parameters
    ----------
    n_chan : int
        number of channels
    ch_names : list | array-like | str | None
        channel names (must have length n_chan) or montage to use for naming.
        If None, numeric channel names are generated automatically.
    sfreq : float
        sampling frequency (Hz)
    duration : float
        duration in seconds
    seed : int or array-like
        seed passed to `numpy.set_seed`
    iaf : float
        individual alpha frequency

    Notes
    ------
    The interface for this function should be considered unstable.
    There is a reason this function is private!
    """
    # TODO: events and stim channel
    # TODO: SNR for IAF
    np.random.seed(seed)

    times = np.arange(0, duration, 1. / sfreq)
    montage = None

    if ch_names is None:
        ch_names = [str(i) for i in range(n_chan)]
    elif isinstance(ch_names, str):
        montage = mne.channels.read_montage(ch_names)
        ch_names = list(np.random.choice(montage.ch_names, n_chan))

    # sine wave with a random phase offset by channel and Gaussian noise
    frequency = iaf

    phase = 2. * np.pi * np.random.rand(n_chan)
    phase /= frequency

    # get everything in the right shape
    data = np.tile(times, (n_chan, 1))
    phase = np.stack([phase] * times.shape[0], axis=1)

    # basic sine wave
    data = np.sin(2. * np.pi * frequency * data - phase)
    # put things on the (ten) microvolt scale
    data *= 10e-6
    # Gaussian noise
    data += np.random.normal(n_chan, times.shape[0])

    # add in stim channel
    data = np.vstack([data, np.zeros(shape=times.shape)])
    ch_names = ch_names + ["STI 014"]

    info = mne.create_info(ch_names, sfreq, ch_types="eeg", montage=montage)

    raw = mne.io.RawArray(data, info)
    # capture runtime warning about unit change
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        raw.set_channel_types({"STI 014": "stim"})

    return raw
