# -*- coding: utf-8 -*-
"""
Export CV data from .bin format to .csv format.

Created on Sat May 27 2023

@author: David Hebert
"""
import os


def export_csv(voltammogram, data_start=1, segments=0):
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
    name = voltammogram.name
    path = voltammogram.path

    if voltammogram.reference != 0:
        cv_data = voltammogram.corrected_voltammogram
    else:
        cv_data = voltammogram.voltammogram

    # If path is a file, create output folder in {path} named
    # {name} without file extension.
    if os.path.isfile(path) is True:
        output_dir = os.path.splitext(path)[0]
        n = 1
        # If a folder named {name} exists, add a number after.
        while os.path.exists(output_dir) is True:
            output_dir = os.path.splitext(path)[0] + f' ({n})'
            n += 1

    # Otherwise create folder in {path} named {name}.
    else:
        output_dir = os.path.join(path, f'{name}')
        n = 1
        # If a folder named {name} already exists, add a number after.
        while os.path.exists(output_dir) is True:
            output_dir = os.path.join(path, f'{name}') + f' ({n})'
            n += 1

    os.mkdir(output_dir)

    # Get number of digits to use for leading zeros.
    digits = len(str(len(cv_data)))

    for i in range(data_start - 1, data_start + segments - 1):
        cv_data[i].to_csv(os.path.join(output_dir, f'{str(i+1).zfill(digits)}.csv'), index=False)

    print(f'Finished export: {output_dir}', end='\n')
