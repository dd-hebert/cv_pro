# -*- coding: utf-8 -*-
"""
Export CV data from .bin format to .csv format.

Created on Sat May 27 2023

@author: David Hebert
"""

from pathlib import Path

from cv_pro.utils.paths import get_unique_filename


def export_csv(
    data, output_dir: str | Path, base_filename: str, suffix: str | None = None
) -> str:
    """
    Export CV segments to .csv format.

    Data is exported to the same directory as the parent \
    .bin file.

    Parameters
    ----------
    data : :class:`pandas.DataFrame`
        The data to be exported. A :class:`pandas.DataFrame`
        such as :attr:`~cv_pro.voltammogram.Voltammogram.raw_data`
    suffix : str or None
        A suffix to append to the end of the file name \
        (before the file extension).

    Returns
    -------
    str
        The name of the exported .csv file.
    """
    if suffix:
        base_filename += f'_{suffix}'

    filename = get_unique_filename(output_dir, base_filename, '.csv')
    data.to_csv(output_dir.joinpath(filename), index=True)
    return filename


def export_figure(fig, output_dir: Path, filename: str) -> str:
    """Save a figure with `filename` as .png to the `output_dir`."""
    filename = get_unique_filename(output_dir, filename, '.png')
    fig.savefig(fname=output_dir.joinpath(filename), format='png', dpi=600)
    return filename
