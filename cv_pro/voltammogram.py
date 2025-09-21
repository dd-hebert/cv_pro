# -*- coding: utf-8 -*-
"""
Process CV data.

Created on Thu May 25 2023

@author: David Hebert
"""

from pathlib import Path
from typing import Literal

import pandas as pd

from cv_pro.ehalf import find_ehalfs
from cv_pro.io.export_csv import export_csv
from cv_pro.io.parse_bin import parse_bin_file
from cv_pro.segment import Segment
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
        self.segments, self.parameters = parse_bin_file(self.path)

        self.trimmed_segments = self.segments.copy()
        self.peaks = None
        self.E_halfs = None
        self.peak_separations = None
        self.processed_segments = None
        self.is_processed = False

        if not view_only:
            self.process_data()

    def __rich__(self):
        return ProcessingOutput(self)

    def process_data(self) -> None:
        """Apply processing (trimming, x-axis correction, E1/2 calculation) to CV data."""
        if self.trim is not None:
            self._check_trim_values()
            self.trimmed_segments = self.trim_data(self.trimmed_segments)

        if self.reference != 0:
            self.apply_correction(self.trimmed_segments)

        self.find_peaks(self.trimmed_segments)
        find_ehalfs(self.trimmed_segments, self.peak_sep_limit)

        self.is_processed = True

    def trim_data(self, segments: list[Segment]) -> list[Segment]:
        """Remove traces outside the given range of trace indices."""
        trim_before = self.trim[0] - 1  # Convert to 0-based indexing
        trim_after = self.trim[1]
        return segments[trim_before:trim_after]

    def find_peaks(self, segments: list[Segment]) -> None:
        """Find peaks in the CV segment traces."""
        for segment in segments:
            segment.find_peaks()

    def apply_correction(self, segments: list[Segment]) -> None:
        """Apply a correction to the x-axis of the CV segment traces."""
        for segment in segments:
            segment.apply_correction(self.reference)

    def _check_trim_values(self) -> None:
        start, end = self.trim
        start = max(start, 1)

        if end >= len(self.segments) or end == -1:
            end = len(self.segments)

        if start > end:
            raise ValueError(
                f"Invalid trim indices: start={start}, end={end}. "
                "Start must be <= end. Did you mean --trim "
                f"{end} {start}?"
            )

        self.trim = (start, end)

    def export_csv(
        self,
        segments: list[Segment],
        data_type: Literal['raw', 'processed'] = 'processed',
        suffix: str | None = None,
    ) -> None:
        ser = pd.concat([getattr(segment, data_type) for segment in segments], axis=0)
        ser.name = 'Current (A)'
        return export_csv(ser, self.path.parent, Path(self.name).stem, suffix=suffix)
