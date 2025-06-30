# -*- coding: utf-8 -*-
"""
Process CV data.

Created on Thu May 25 2023

@author: David Hebert
"""

from pathlib import Path

import pandas as pd

from cv_pro.ehalf import find_ehalfs
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
    parameters : Parameters
        A :class:`~cv_pro.io.parse_bin.Parameters` object containing the experimental parameters.
    raw_data : :class:`pandas.DataFrame`
        A :class:`pandas.DataFrame` containing the raw CV data.
    peaks : list
        A list of :func:`scipy.signal.find_peaks()` results giving the peaks
        detected in each CV segment.
    E_halfs : list[list[float]]
        A list of lists containing the E1/2s for each segment.
    peak_separations : list[list[float]]
        A list of lists containing the peak separations for each E1/2 value.
    processed_data : :class:`pandas.DataFrame`
        A :class:`pandas.DataFrame` containing the processed (corrected and trimmed)
        CV data.
    """

    def __init__(
        self,
        path: str | Path,
        trim: tuple[int, int] | None = None,
        reference: float = 0.0,
        peak_sep_limit: float = 0.2,
        view_only: bool = False,
    ) -> None:
        """
        Initialize a :class:`~cv_pro.process.Voltammogram` object.

        Imports the specified data at ``path`` and processes the data to detect
        peaks, calculate E1/2s, and correct the x-axis to the given reference.

        Parameters
        ----------
        path : string or Path
            A file path to a .bin file containing the data to be processed.
        trim : tuple[int, int] or None
            Trim the data to keep the segments with indices in the range of the
            given values `(start, end)`. Default is None (no trimming).
        reference : float, optional
            A redox couple reference value (given in V) to correct the x-axis
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
        self.trim = trim
        self.reference = reference
        self.peak_sep_limit = peak_sep_limit
        self.raw_data, self.parameters = parse_bin_file(self.path)

        self.peaks = None
        self.E_halfs = None
        self.peak_separations = None
        self.processed_data = None
        self.is_processed = False

        if not view_only:
            self.process_data()

    def __rich__(self):
        return ProcessingOutput(self)

    def process_data(self) -> None:
        self.processed_data = self.raw_data.copy()

        if self.trim is not None:
            self._check_trim_values()
            self.processed_data = self.trim_data(self.processed_data)

        if self.reference != 0:
            self.processed_data = self._apply_correction(self.processed_data)

        self.peaks = self.find_peaks(self.processed_data)
        self.E_halfs, self.peak_separations = find_ehalfs(
            self.processed_data, self.peaks, self.peak_sep_limit
        )

        self.is_processed = True

    def trim_data(self, cv_traces: pd.DataFrame) -> pd.DataFrame:
        before = f'Segment_{self.trim[0]}'
        after = f'Segment_{self.trim[1]}'
        return cv_traces.truncate(before, after, axis='columns', copy=True)

    def find_peaks(self, cv_traces: pd.DataFrame) -> list:
        """
        Find peaks in the CV segments.

        Parameters
        ----------
        cv_traces : :class:`pandas.DataFrame`
            The CV traces to find peaks with.

        Returns
        -------
        peaks : list
            Returns a list of :func:`scipy.signal.find_peaks()` results.
        """
        from scipy.signal import find_peaks

        peaks = {
            name: find_peaks(abs(segment), width=20)[0]
            for name, segment in cv_traces.items()
        }
        return peaks

    def _apply_correction(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Correct the x-axis to be relative to the reference redox couple.

        Parameters
        ----------
        data: :class:`pandas.DataFrame`
            The CV data to apply a correction to.

        Returns
        -------
        :class:`pandas.DataFrame`
            A :class:`pandas.DataFrame` containing the corrected CV data.
        """
        corrected_data = data
        corrected_data.index = corrected_data.index - self.reference
        return corrected_data

    def _check_trim_values(self) -> None:
        start, end = self.trim
        start = max(start, 1)

        if end >= len(self.raw_data.columns) or end == -1:
            end = len(self.raw_data.columns)

        self.trim = (start, end)

    def export_csv(self, data: pd.DataFrame, suffix: str | None = None) -> None:
        return export_csv(data, self.path.parent, Path(self.name).stem, suffix=suffix)
