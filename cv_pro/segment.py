"""
Methods for storing and processing CV segment traces.

Created on Sat July 5 2025

@author: David Hebert
"""

import pandas as pd


class Segment:
    """
    CV segment trace data.

    Attributes
    ----------
    raw : :class:`pandas.Series`
        The raw CV segment trace.
    processed : :class:`pandas.Series`
        The processed CV segment trace with x-axis correction (if applied).
    """

    def __init__(
        self,
        index: int,
        data: pd.Series,
        peaks: list[int] = [],
        ehalfs: list[float] = [],
        peak_separations: list[float] = [],
    ) -> None:
        """
        Store CV segment trace data.

        Parameters
        ----------
        index : int
            The index of the segment.
        data : pd.Series
            The potential and current data.
        peaks : list[int], optional
            A list of indices of peaks found in the CV segment, by default [].
        ehalfs : list[float], optional
            A list of calculated E1/2 values for the CV segment, by default [].
        peak_separations : list[float], optional
            A list of peak separations for the calculated E1/2 values, by default [].
        """
        self.index = index
        self.raw = data.copy()
        self.processed = data.copy()
        self.peaks = peaks
        self.ehalfs = ehalfs
        self.peak_separations = peak_separations

    def apply_correction(
        self, correction: float, reference_name: str = 'Fc+/0'
    ) -> None:
        """
        Correct the x-axis to be relative to a reference redox couple.

        Parameters
        ----------
        correction : float
            The correction to apply to the x-axis
        reference_name : str
            The name of the referenced redox couple. Default is 'Fc+/0'.
        """
        self.processed.index = (self.processed.index - correction).round(3)
        self.processed.index.rename(f'Potential (V) vs. {reference_name}', inplace=True)

    def find_peaks(self) -> None:
        """Find peaks in the CV segment."""
        from scipy.signal import find_peaks

        self.peaks = find_peaks(abs(self.processed), width=20)[0]
