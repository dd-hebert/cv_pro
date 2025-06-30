# -*- coding: utf-8 -*-
"""
Parse CV data .bin files from CH Instruments CHI760e electrochemical workstation.

Created on Fri May 26 2023

@author: David Hebert
"""

import struct
from dataclasses import dataclass

import pandas as pd


@dataclass
class Parameters:
    init_E: float
    final_E: float
    high_E: float
    low_E: float
    scan_rate: float
    init_sweep_direction: tuple[int, str]
    num_segments: int
    sample_interval: float
    sensitivity: float
    quiet_time: float


def parse_bin_file(path) -> tuple[pd.DataFrame, Parameters]:
    """
    Parse CV data .bin file.

    Parameters
    ----------
    path : str or Path
        A file path to a .bin file containing CV data.

    Returns
    -------
    voltammogram : list
        A :class:`pandas.DataFrame` containing the CV data.
    parameters : Parameters
        A :class:`~cv_pro.io.parse_bin.Parameters` object containing the experimental parameters.

    """
    file_bytes = _read_bin(path)
    parameters = _get_parameters(file_bytes)
    current = _unpack_data(file_bytes)
    potential, segment_indices = _build_segments(file_bytes, parameters)
    voltammogram = _build_voltammogram(potential, current, segment_indices)

    return voltammogram, parameters


def _read_bin(path):
    with open(path, 'rb') as bin_file:
        file_bytes = bin_file.read()
    return file_bytes


def _get_parameters(file_bytes):
    parameters = {}
    # Little endian float mode
    parameters['init_E'] = round(struct.unpack('<f', (file_bytes[845:849]))[0], 3)  # V
    parameters['final_E'] = round(struct.unpack('<f', (file_bytes[849:853]))[0], 3)  # V
    parameters['high_E'] = round(struct.unpack('<f', (file_bytes[853:857]))[0], 3)  # V
    parameters['low_E'] = round(struct.unpack('<f', (file_bytes[857:861]))[0], 3)  # V
    parameters['scan_rate'] = round(
        struct.unpack('<f', (file_bytes[861:865]))[0], 5
    )  # V/s
    # unknown_var1 = struct.unpack('<f', (file_bytes[865: 869]))[0]  # unknown
    init_scan_polarity = int(struct.unpack('<f', (file_bytes[869:873]))[0])  # 1 or 0
    parameters['num_segments'] = int(
        struct.unpack('<f', (file_bytes[873:877]))[0]
    )  # no units
    parameters['sample_interval'] = round(
        struct.unpack('<f', (file_bytes[877:881]))[0], 5
    )  # V
    # unknown_var3 = struct.unpack('<f', (file_bytes[881: 885]))[0]  # unknown
    parameters['sensitivity'] = struct.unpack('<f', (file_bytes[885:889]))[0]  # A/V
    parameters['quiet_time'] = struct.unpack('<f', (file_bytes[889:893]))[0]  # sec

    if init_scan_polarity == 1:
        parameters['init_sweep_direction'] = (1, 'Positive')
    elif init_scan_polarity == 0:
        parameters['init_sweep_direction'] = (-1, 'Negative')

    return Parameters(**parameters)


def _unpack_data(file_bytes: bytes) -> list[float]:
    data_start = 1445  # CV data begins at this byte
    cv_data = file_bytes[data_start:]
    current = [value for (value,) in struct.iter_unpack('<f', cv_data)]
    return current


def _build_segments(
    file_bytes: bytes, parameters: Parameters
) -> tuple[list[float], list[int]]:
    data_start = 1445  # CV data begins at this byte
    sweep_direction = parameters.init_sweep_direction[0]
    v = parameters.init_E
    tol = 1e-4
    segment_indices = [0]
    potential = []

    for i in range(data_start, len(file_bytes), 4):
        potential.append(round(v, 3))
        v += round(parameters.sample_interval * sweep_direction, 3)

        # Change sweep direction when v = the high or low limit
        if abs(v - parameters.high_E) < tol or abs(v - parameters.low_E) < tol:
            sweep_direction *= -1
            segment_indices.append(len(potential))

    return potential, segment_indices


def _build_voltammogram(
    potential: list[float], current: list[float], segment_indices: list[int]
) -> pd.DataFrame:
    if segment_indices[-1] != len(potential):
        segment_indices.append(len(potential))

    segments = []

    for i in range(len(segment_indices) - 1):
        start = segment_indices[i]
        end = segment_indices[i + 1]

        pot = potential[start:end]
        cur = current[start:end]

        df = pd.DataFrame({f'Segment_{i + 1}': cur}, index=pot)
        segments.append(df)

    voltammogram = pd.concat(segments, axis=1)
    voltammogram.sort_index(inplace=True)

    return voltammogram
