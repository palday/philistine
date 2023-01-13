# -*- coding: utf-8 -*-
# Copyright (C) 2017-2023 Phillip Alday <me@phillipalday.com>
# License: BSD (3-clause)
"""MNE-based functions for manipulating EEG data."""

from ._base import (savgol_iaf, attenuation_iaf,
                    abs_threshold, retrieve)

from .io import (write_raw_brainvision, )
