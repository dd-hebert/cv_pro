# -*- coding: utf-8 -*-
"""
Parse CV data .bin files from CH Instruments CHI760e electrochemical workstation.

Created on Fri May 26 2023

@author: David Hebert
"""
import struct
import pandas as pd


def parse_bin_file(path):
    """
    Parse CV data .bin file.

    Parameters
    ----------
    path : str
        A file path to a .bin file containing CV data.

    Returns
    -------
    parameters : dict
        A dictionary containing the experimental parameters.
    voltammogram : list
        A list of :class:`pandas.DataFrame` objects containing the CV data.

    """
    print('Reading bin file...')
    file_bytes = _open_bin_file(path)
    parameters = _get_experimental_parameters(file_bytes)
    _print_experimental_parameters(parameters)
    current = _unpack_data(file_bytes, parameters)
    potential, segment_indices = _build_segments(file_bytes, parameters)
    voltammogram = _build_voltammogram(potential, current, segment_indices)
    print('Success.')

    return parameters, voltammogram


def _open_bin_file(path):
    with open(path, 'rb') as bin_file:
        file_bytes = bin_file.read()

    return file_bytes


def _get_experimental_parameters(file_bytes):
    parameters = {}
    # Little endian float mode
    parameters['init_E'] = round(struct.unpack('<f', (file_bytes[845: 849]))[0], 3)  # V
    parameters['final_E'] = round(struct.unpack('<f', (file_bytes[849: 853]))[0], 3)  # V
    parameters['high_E'] = round(struct.unpack('<f', (file_bytes[853: 857]))[0], 3)  # V
    parameters['low_E'] = round(struct.unpack('<f', (file_bytes[857: 861]))[0], 3)  # V
    parameters['scan_rate'] = round(struct.unpack('<f', (file_bytes[861: 865]))[0], 5)  # V/s
    # unknown_var1 = struct.unpack('<f', (file_bytes[865: 869]))[0]  # unknown
    parameters['init_scan_polarity'] = int(struct.unpack('<f', (file_bytes[869: 873]))[0])  # 1 or 0
    parameters['num_segments'] = int(struct.unpack('<f', (file_bytes[873: 877]))[0])  # no units
    parameters['sample_interval'] = round(struct.unpack('<f', (file_bytes[877: 881]))[0], 5)  # V
    # unknown_var3 = struct.unpack('<f', (file_bytes[881: 885]))[0]  # unknown
    parameters['sensitivity'] = struct.unpack('<f', (file_bytes[885: 889]))[0]  # A/V
    parameters['quiet_time'] = struct.unpack('<f', (file_bytes[889: 893]))[0]  # sec

    if parameters['init_scan_polarity'] == 1:
        parameters['init_sweep_direction'] = (1, 'Positive')
    elif parameters['init_scan_polarity'] == 0:
        parameters['init_sweep_direction'] = (-1, 'Negative')

    return parameters


def _print_experimental_parameters(parameters):
    print(f'Init E (V): {parameters["init_E"]}')
    print(f'Final E (V): {parameters["final_E"]}')
    print(f'High E (V): {parameters["high_E"]}')
    print(f'Low E (V): {parameters["low_E"]}')
    print(f'Scan Rate (V/s): {parameters["scan_rate"]}')
    print(f'Initial Scan Polarity: {parameters["init_sweep_direction"][1]}')


def _unpack_data(file_bytes, parameters):
    data_start = 1445  # CV data begins at this byte
    cv_data = file_bytes[data_start:]

    current = [value for value, in struct.iter_unpack('<f', cv_data)]

    return current


def _build_segments(file_bytes, parameters):
    data_start = 1445  # CV data begins at this byte
    segment_indices = [0]
    sweep_direction = parameters['init_sweep_direction'][0]
    v = parameters['init_E']
    potential = []

    for i in range(data_start, len(file_bytes), 4):
        potential.append(round(v, 3))

        # Change sweep direction when v = to the high or low limit
        if round(v, 3) == parameters['high_E'] or round(v, 3) == parameters['low_E']:
            sweep_direction *= -1
            segment_indices.append(len(potential) - 1)
        v += round(parameters['sample_interval'] * sweep_direction, 3)

    # Add end index of final segment
    segment_indices.append(len(potential) - 1)

    return potential, segment_indices


def _build_voltammogram(potential, current, segment_indices):
    voltammogram = []

    for i in range(len(segment_indices) - 1):
        pot = potential[segment_indices[i]:segment_indices[i + 1]]
        cur = current[segment_indices[i]:segment_indices[i + 1]]
        df = pd.DataFrame({'Potential (V)': pot, 'Current (A)': cur})
        voltammogram.append(df)

    return voltammogram
