# -*- coding: utf-8 -*-
"""
Helper functions for cv_pro

Created on Thu March 21 2024

@author: David Hebert
"""


def check_start_and_segments(voltammogram, data_start, num_segments):
    """
    Check that the given start and number of segments are within the
    bounds of the data. For example, if `data_start` = 2 and
    `num_segments` = 4, then the selected CV data will include 4 CV
    segments starting from the 2nd CV segment.

    Parameters
    ----------
    voltammogram : list
        A list of :class:`pandas.DataFrame` objects containing the CV data for
        each segment.
    data_start : int
        The first CV segment of interest.
    num_segments : int
        The number of CV segments of interest.

    Returns
    -------
    data_start : int
        The first CV segment of interest.
    num_segments : int
        The number of CV segments of interest.
    """
    if data_start > len(voltammogram.columns):
        data_start = len(voltammogram.columns)
    elif data_start <= 0:
        data_start = 1
    if data_start + num_segments > len(voltammogram.columns) or num_segments <= 0:
        num_segments = len(voltammogram.columns) - (data_start - 1)
    return data_start, num_segments
