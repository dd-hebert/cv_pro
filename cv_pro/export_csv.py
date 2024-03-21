# -*- coding: utf-8 -*-
"""
Export CV data from .bin format to .csv format.

Created on Sat May 27 2023

@author: David Hebert
"""
import os
from cv_pro.utils.helpers import check_start_and_segments


def _get_unique_dirname(path):
    output_dir = os.path.splitext(path)[0]
    n = 1
    # If a folder named {output_dir} exists, add a number after.
    while os.path.exists(output_dir) is True:
        output_dir = os.path.splitext(path)[0] + f' ({n})'
        n += 1
    return output_dir


def export_csv(voltammogram, data_start=1, num_segments=0):
    """
    Export CV segments to .csv format.

    Parameters
    ----------
    voltammogram : :class:`~cv_pro.process.Voltammogram`
        The voltammogram to export.
    data_start : int, optional
        The first segment to export. The default is 1.
    segments : int, optional
        The total number of segments to export. The default is 0 (all segments).

    Returns
    -------
    None. Exports .csv files.
    """
    if voltammogram.reference != 0:
        cv_data = voltammogram.corrected_voltammogram
    else:
        cv_data = voltammogram.voltammogram

    data_start, num_segments = check_start_and_segments(cv_data, data_start, num_segments)

    output_dir = _get_unique_dirname(voltammogram.path)
    os.mkdir(output_dir)

    # Get number of digits to use for leading zeros.
    digits = len(str(len(cv_data)))

    for i in range(data_start - 1, (data_start - 1) + num_segments):
        cv_data[i].to_csv(os.path.join(output_dir, f'{str(i + 1).zfill(digits)}.csv'), index=False)
    print(f'Finished export: {output_dir}', end='\n')
