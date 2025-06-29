# -*- coding: utf-8 -*-
"""
Process CV data.

Created on Thu May 25 2023

@author: David Hebert
"""

from pathlib import Path

import pandas as pd
import scipy

from cv_pro.io.export_csv import export_csv
from cv_pro.io.parse_bin import parse_bin_file
from cv_pro.utils._rich import ProcessingOutput


class Voltammogram:
    """
    A Voltammogram object. Contains methods to process CV data.

    Attributes
    ----------
    name : string
        The name of the .bin file that the :class:`Voltammogram` was created
        from.
    parameters : dict
        A dictionary containing the experimental parameters from the .bin file.
    voltammogram : list
        A list of :class:`pandas.DataFrame` objects containing the CV data for
        each segment.
    peaks : list
        A list of :func:`scipy.signal.find_peaks()` results giving the peaks
        detected in each CV segment.
    E_halfs : list
        A list of lists containing the E1/2s for each segment.
    corrected_voltammogram : list
        A list of :class:`pandas.DataFrame` objects containing the cCV data for
        each segment with the x-axis adjusted relative to the ferrocenium redox
        couple.
    """

    def __init__(self, path, reference=0.0, peak_sep_limit=0.2, view_only=False):
        """
        Initialize a :class:`~cv_pro.process.Voltammogram` object.

        Imports the specified data at ``path`` and processes the data to detect
        peaks, calculate E1/2s, and correct the x-axis to the given reference.

        Parameters
        ----------
        path : string
            A file path to a .bin file containing the data to be processed.
        reference : float, optional
            A redox couple reference value(given in V) to correct the x-axis
            for data reporting. The default is 0.
        peak_sep_limit : float, optional
            The maximum peak separation (given in V) to attempt E1/2 calculations.
            If peaks are separated by a distance greater than the given value,
            no E1/2 calculation will be performed. The default is 0.2.
        view_only : True or False, optional
            Indicate whether data processing (peak finding and E1/2 calculations)
            should be performed. Default is False (processing performed).

        Returns
        -------
        None.
        """
        self.path = Path(path)
        self.name = Path(self.path).name
        self.reference = reference
        self.peak_sep_limit = peak_sep_limit
        self.parameters, self.voltammogram = parse_bin_file(self.path)

        self.peaks = None
        self.E_halfs = None
        self.peak_separations = None
        self.corrected_voltammogram = None
        self.is_processed = False

        if not view_only:
            self.process_data()

    def __rich__(self):
        return ProcessingOutput(self)

    def process_data(self) -> None:
        self.peaks = self.find_peaks()
        self.E_halfs, self.peak_separations = self.find_Ehalfs()
        self._print_E_halfs(self.E_halfs, self.peak_separations)
        if self.reference != 0:
            self.corrected_voltammogram = self._relative_to_ferrocenium()
        self.is_processed = True

    def find_peaks(self):
        """
        Find peaks in the CV segment.

        Returns
        -------
        peaks : list
            Returns a list of :func:`scipy.signal.find_peaks()` results.
        """
        peaks = []

        for _, segment in self.voltammogram.items():
            peaks.append(scipy.signal.find_peaks(abs(segment), width=20))

        return peaks

    def find_Ehalfs(self):
        """
        Find E1/2s of peaks that are within the ``peak_sep_limit``.

        Returns
        -------
        E_halfs : list
            List of lists containing the E1/2s for each segment.
        """
        print('\nFinding E1/2s...')
        E_halfs = []
        peak_separations = []

        for i in range(len(self.voltammogram.columns) - 1):
            segment = self.voltammogram.iloc[:, i]
            next_segment = self.voltammogram.iloc[:, i + 1]
            e_halfs = []
            peak_sep = []

            for peak_a in self.peaks[i][0]:
                peak_a_x = segment.index[peak_a] - self.reference
                peak_a_y = segment.iloc[peak_a]
                for peak_b in self.peaks[i + 1][0]:
                    peak_b_x = next_segment.index[peak_b] - self.reference
                    peak_b_y = next_segment.iloc[peak_b]
                    if abs(peak_a_x - peak_b_x) <= self.peak_sep_limit:
                        # Check that peaks are in the correct order
                        if (peak_a_y > peak_b_y and peak_a_x < peak_b_x) or (
                            peak_a_y < peak_b_y and peak_a_x > peak_b_x
                        ):
                            e_halfs.append(
                                round(0.5 * (peak_a_x - peak_b_x) + peak_b_x, 2)
                            )
                            peak_sep.append(abs(peak_a_x - peak_b_x))

            E_halfs.append(e_halfs)
            peak_separations.append(peak_sep)

        return E_halfs, peak_separations

    def _print_E_halfs(self, E_halfs, peak_separations):
        for i, (e_half, peak_sep) in enumerate(zip(E_halfs, peak_separations)):
            if i < len(E_halfs):
                print(f'Segment {i + 1} to {i + 2}:')
                e_half.sort(reverse=True)
                for value, peak_sep in zip(e_half, peak_sep):
                    print(f'\tE1/2 (V): {value} ({round(peak_sep, 3)})')
        print('\n')

    def _relative_to_ferrocenium(self):
        """
        Convert the x-axis to be relative to the ferrocenium redox couple.

        Returns
        -------
        :class:`pandas.DataFrame`
            A :class:`pandas.DataFrame` containing the corrected CV data.
        """
        corrected_voltammogram = self.voltammogram
        corrected_voltammogram.index = corrected_voltammogram.index - self.reference
        return corrected_voltammogram

    def export_csv(self, data: pd.DataFrame, suffix: str | None = None) -> None:
        return export_csv(data, self.path.parent, Path(self.name).stem, suffix=suffix)
