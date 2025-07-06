import numpy as np
import pandas as pd

from cv_pro.segment import Segment


def find_ehalfs(segments: list[Segment], peak_sep_limit: float = 0.2) -> None:
    """
    Find E1/2 values for peak pairs between consecutive segments that are within `peak_sep_limit`.

    For cyclic voltammetry, E1/2 is calculated as the midpoint between oxidation and reduction
    peaks that form a reversible couple.

    Parameters
    ----------
    segments : list[:class:`~cv_pro.segment.Segment`]
        The CV segment traces to find E1/2 values for.
    peak_sep_limit : float
        The maximum separation between peaks (in V) to calculate E1/2 for.

    Notes
    -----
    Peaks are considered a valid pair if:
    1. Their separation is within peak_sep_limit
    2. They follow the correct electrochemical order (oxidation precedes reduction or vice versa)
    """
    for segment_pair in zip(segments, segments[1:]):
        ehalfs, peak_separations = _process_segment_pair(segment_pair, peak_sep_limit)
        segment_pair[0].ehalfs = ehalfs
        segment_pair[0].peak_separations = peak_separations


def _process_segment_pair(
    segment_pair: tuple[Segment, Segment], peak_sep_limit: float = 0.2
) -> tuple[list[float], list[float]]:
    """
    Process a pair of consecutive segments to find E1/2 values.

    Parameters
    ----------
    segment_pair : tuple[:class:`~cv_pro.segment.Segment`, :class:`~cv_pro.segment.Segment`]
        A pair of CV segment traces to find E1/2 values with.

    Returns
    -------
    tuple[list[float], list[float]]
        E1/2 values and peak separations for this segment pair
    """
    current_segment, next_segment = segment_pair

    current_peaks = current_segment.peaks
    next_peaks = next_segment.peaks

    if len(current_peaks) == 0 or len(next_peaks) == 0:
        return [], []

    current_peak_data = _extract_peak_coordinates(current_segment, current_peaks)
    next_peak_data = _extract_peak_coordinates(next_segment, next_peaks)

    return _find_matching_peaks(current_peak_data, next_peak_data, peak_sep_limit)


def _extract_peak_coordinates(
    segment: pd.Series, peak_indices: list[int] | np.ndarray
) -> list[tuple[float, float]]:
    """
    Extract potential and current coordinates for peaks in a segment.

    Parameters
    ----------
    segment : :class:`pandas.Series`
        CV segment data
    peak_indices : list[int] or :class:`numpy.ndarray`
        Indices of peaks in the segment
    reference : float
        A reference value to correct the potentials (x-axis) of
        the CV segment.

    Returns
    -------
    list[tuple[float, float]]
        List of (potential, current) tuples for each peak
    """
    return [
        (segment.processed.index[peak_idx], segment.processed.iloc[peak_idx])
        for peak_idx in peak_indices
    ]


def _find_matching_peaks(
    current_peaks: list[tuple[float, float]],
    next_peaks: list[tuple[float, float]],
    peak_sep_limit: float = 0.2,
) -> tuple[list[float], list[float]]:
    """
    Find matching peak pairs and calculate E1/2 values.

    Parameters
    ----------
    current_peaks : list[tuple[float, float]]
        (potential, current) pairs for current segment peaks
    next_peaks : list[tuple[float, float]]
        (potential, current) pairs for next segment peaks

    Returns
    -------
    tuple[list[float], list[float]]
        E1/2 values and peak separations for matched pairs
    """
    ehalfs = []
    separations = []

    for potential_a, current_a in current_peaks:
        for potential_b, current_b in next_peaks:
            separation = abs(potential_a - potential_b)

            if separation <= peak_sep_limit:
                if _is_valid_peak_pair(potential_a, current_a, potential_b, current_b):
                    ehalf = _calculate_e_half(potential_a, potential_b)
                    ehalfs.append(ehalf)
                    separations.append(separation)

    return ehalfs, separations


def _is_valid_peak_pair(
    pot_a: float, curr_a: float, pot_b: float, curr_b: float
) -> bool:
    """
    Check if two peaks form a valid electrochemical pair.

    For a valid reversible couple:
    - If current_a > current_b, then potential_a < potential_b (oxidation before reduction)
    - If current_a < current_b, then potential_a > potential_b (reduction before oxidation)

    Parameters
    ----------
    pot_a, curr_a : float
        Potential and current of first peak
    pot_b, curr_b : float
        Potential and current of second peak

    Returns
    -------
    bool
        True if peaks form a valid pair
    """
    return (curr_a > curr_b and pot_a < pot_b) or (curr_a < curr_b and pot_a > pot_b)


def _calculate_e_half(potential_a: float, potential_b: float) -> float:
    """
    Calculate E1/2 as the midpoint between two peak potentials.

    Parameters
    ----------
    potential_a, potential_b : float
        Peak potentials

    Returns
    -------
    float
        E1/2 value rounded to 2 decimal places
    """
    return round(0.5 * (potential_a + potential_b), 2)
