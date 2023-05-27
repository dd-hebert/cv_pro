# -*- coding: utf-8 -*-
"""
Read CV binary files.

Created on Thu May 25 13:26:11 2023

@author: David Hebert
"""

# TODO: Add csv exporting
#       Add CLI
#       Package app

import os
import struct
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import scipy
from plots import plot_CV
from file_parse import parse_bin_file

class Voltammogram:

    def __init__(self, path, reference=0, peak_sep_limit=0.2):
        self.path = path
        self.name = os.path.basename(self.path)
        self.reference = reference
        self.peak_sep_limit = peak_sep_limit
        self.parameters, self.voltammogram = parse_bin_file(self.path)
        self.peaks = self.find_peaks()
        self.E_halfs = self.find_Ehalfs()


    def find_peaks(self):
        # Find peaks
        peaks = []

        for segment in self.voltammogram:
            peaks.append(scipy.signal.find_peaks(abs(segment['Current (A)']), width=20))

        return peaks


    def find_Ehalfs(self):
        # Find E-halfs
        print('\nFinding E1/2s...')
        E_halfs = []
        for i, _ in enumerate(self.voltammogram):
            if i < len(self.voltammogram) - 1:
                e12 = []
                for pks1 in self.peaks[i][0]:
                    pk_pot1 = self.voltammogram[i]['Potential (V)'][pks1] - self.reference
                    pk_cur1 = self.voltammogram[i]['Current (A)'][pks1]
                    for pks2 in self.peaks[i + 1][0]:
                        pk_pot2 = self.voltammogram[i + 1]['Potential (V)'][pks2] - self.reference
                        pk_cur2 = self.voltammogram[i + 1]['Current (A)'][pks2]
                        if abs(pk_pot1 - pk_pot2) <= self.peak_sep_limit:
                            if pk_cur1 > pk_cur2 and pk_pot1 < pk_pot2:
                                e12.append(round(0.5 * (pk_pot1 - pk_pot2) + pk_pot2, 2))
                            elif pk_cur1 < pk_cur2 and pk_pot1 > pk_pot2:
                                e12.append(round(0.5 * (pk_pot1 - pk_pot2) + pk_pot2, 2))
                E_halfs.append(e12)

        for i, waves in enumerate(E_halfs):
            if i < len(E_halfs):
                print(f'Sweep: {i + 1} to {i + 2}')
                waves.sort()
                waves.reverse()
                print(f'\tE1/2: {waves} V')

        return E_halfs


if __name__ == '__main__':
    file_path = r"H:\Documents\Lab Notebook\CV Data\DHN3P49\(ONOsq)Cu(NEt3)_C.bin"
    FcPF6 = 0.06  # Set Fc/Fc+ correction factor
    peak_sep_limit = 0.2
    plot_start = 2
    plot_segments = 2

    # Get CV data
    data = Voltammogram(file_path,
                        reference=FcPF6,
                        peak_sep_limit=peak_sep_limit)

    # Plot CV data
    plot_CV(data, plot_start, plot_segments)