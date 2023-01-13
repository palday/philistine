# -*- coding: utf-8 -*-
# Copyright (C) 2018, 2023 Phillip Alday <me@phillipalday.com>
# License: BSD (3-clause)
"""Epoch manipulation tests."""

from nose.tools import assert_dict_equal, assert_raises

from philistine import invert_dict


def test_invert_dict():
    """Test that dictionary inversion works."""
    d = dict(A='hot', B='cool')

    di = invert_dict(d)

    assert_dict_equal(di, dict(hot='A', cool='B'))

    d['B'] = 'hot'

    assert_raises(ValueError, invert_dict, d)
