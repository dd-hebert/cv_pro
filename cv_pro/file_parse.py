# -*- coding: utf-8 -*-
"""
Created on Fri May 26 20:35:57 2023

@author: David Hebert
"""
import struct
import pandas as pd

def parse_bin_file(path):
    print('Reading bin file...')
    with open(path, 'rb') as bin_file:
        file_bytes = bin_file.read()  # Bytes from binary file

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
        init_sweep_direction = 'Positive'
        sweep_direction = 1
    elif parameters['init_scan_polarity'] == 0:
        init_sweep_direction = 'Negative'
        sweep_direction = -1

    print(f'Init E (V): {parameters["init_E"]}')
    print(f'Final E (V): {parameters["final_E"]}')
    print(f'High E (V): {parameters["high_E"]}')
    print(f'Low E (V): {parameters["low_E"]}')
    print(f'Scan Rate (V/s): {parameters["scan_rate"]}')
    print(f'Initial Scan Polarity: {init_sweep_direction}')

    potential = []
    current = []
    segment_indices = [0]
    v = parameters['init_E']

    print('\nUnpacking data...')
    for i in range(1445, len(file_bytes), 4):
        current.append(struct.unpack('<f', file_bytes[i: i + 4])[0])
        potential.append(round(v, 3))
    
        # Change sweep direction when v = to the high or low limit
        if round(v, 3) == parameters['high_E'] or round(v, 3) == parameters['low_E']:
            sweep_direction *= -1
            segment_indices.append(len(potential) - 1)
        v += round(parameters['sample_interval'] * sweep_direction, 3)
    
    # Add end index of final segment
    segment_indices.append(len(potential) - 1)

    # Build voltammogram
    voltammogram = []
    for i, _ in enumerate(segment_indices):
        if i < len(segment_indices) - 1:
            pot = potential[segment_indices[i]: segment_indices[i + 1]]
            cur = current[segment_indices[i]: segment_indices[i + 1]]
            voltammogram.append(pd.DataFrame({'Potential (V)': pot,
                                              'Current (A)': cur}))
    print('Success.')

    return parameters, voltammogram