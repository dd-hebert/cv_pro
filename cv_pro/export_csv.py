# -*- coding: utf-8 -*-
"""
Export CV data from .bin format to .csv format.

Created on Sat May 27 2023

@author: David Hebert
"""
import os


def export_csv(voltammogram, data_start=1, segments=0):
    """
    Export to .csv format.

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
    cv_data = voltammogram.voltammogram

    # If path is a file, create output folder in {voltammogram.path} named
    # {voltammogram.name} without file extension.
    if os.path.isfile(voltammogram.path) is True:
        output_dir = os.path.splitext(voltammogram.path)[0]
        n = 1
        # If a folder named {voltammogram.name} exists, add a number after.
        while os.path.exists(output_dir) is True:
            output_dir = os.path.splitext(voltammogram.path)[0] + f' ({n})'
            n += 1

    # Otherwise create folder in {voltammogram.path} named {voltammogram.name}.
    else:
        output_dir = os.path.join(voltammogram.path, f'{voltammogram.name}')
        n = 1
        # If a folder named {voltammogram.name} already exists, add a number after.
        while os.path.exists(output_dir) is True:
            output_dir = os.path.join(voltammogram.path, f'{voltammogram.name}') + f' ({n})'
            n += 1

    os.mkdir(output_dir)

    # Get number of digits to use for leading zeros.
    digits = len(str(len(cv_data)))

    # Export all CV data, name files by index in given list of CV data
    if data_start == 1 and segments == 0:
        for i, segment in enumerate(cv_data):
            segment.to_csv(os.path.join(output_dir, f'{str(i+1).zfill(digits)}.csv'), index=False)

    # Export chosen CV data, name files by segment # in given list of CV data
    else:
        for i in range(data_start - 1, data_start + segments - 1):
            cv_data[i].to_csv(os.path.join(output_dir, f'{str(i+1).zfill(digits)}.csv'), index=False)

    print(f'Finished export: {output_dir}', end='\n')
