# -*- coding: utf-8 -*-
"""
Read CV binary files.

Created on Thu May 25 2023

@author: David Hebert
"""

import os
import scipy
from cv_pro.file_parse import parse_bin_file


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
        each sweep.
    peaks : list
        A list of :func:`scipy.signal.find_peaks()` results giving the peaks
        detected in each CV sweep.
    E_halfs : list
        A list of lists containing the E1/2s for each sweep.
    """

    def __init__(self, path, reference=0, peak_sep_limit=0.2, view_only=False):
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
        self.path = path
        self.name = os.path.basename(self.path)
        self.parameters, self.voltammogram = parse_bin_file(self.path)
        self.reference = reference
        self.peak_sep_limit = peak_sep_limit

        if view_only is False:
            self.peaks = self.find_peaks()
            self.E_halfs = self.find_Ehalfs()

    def find_peaks(self):
        """
        Find peaks in the CV sweep.

        Returns
        -------
        peaks : list
            Returns a list of :func:`scipy.signal.find_peaks()` results.

        """
        peaks = []

        for segment in self.voltammogram:
            peaks.append(scipy.signal.find_peaks(abs(segment['Current (A)']), width=20))

        return peaks

    def find_Ehalfs(self):
        """
        Find E1/2s of peaks that are within the ``peak_sep_limit``.

        Returns
        -------
        E_halfs : list
            List of lists containing the E1/2s for each sweep.

        """
        print('\nFinding E1/2s...')
        E_halfs = []
        peak_separations = []

        for i, _ in enumerate(self.voltammogram):
            if i < len(self.voltammogram) - 1:
                e12 = []  # Temp list to hold E1/2s
                pk_sp = []  # Temp list to hold peak separations

                # Check peaks of sweep i against the peaks of sweep i + 1
                for pks1 in self.peaks[i][0]:
                    pk_pot1 = self.voltammogram[i]['Potential (V)'][pks1] - self.reference
                    pk_cur1 = self.voltammogram[i]['Current (A)'][pks1]
                    for pks2 in self.peaks[i + 1][0]:
                        pk_pot2 = self.voltammogram[i + 1]['Potential (V)'][pks2] - self.reference
                        pk_cur2 = self.voltammogram[i + 1]['Current (A)'][pks2]
                        if abs(pk_pot1 - pk_pot2) <= self.peak_sep_limit:
                            # Check if peaks are in the correct order
                            if pk_cur1 > pk_cur2 and pk_pot1 < pk_pot2:
                                e12.append(round(0.5 * (pk_pot1 - pk_pot2) + pk_pot2, 2))
                                pk_sp.append(abs(pk_pot1 - pk_pot2))
                            elif pk_cur1 < pk_cur2 and pk_pot1 > pk_pot2:
                                e12.append(round(0.5 * (pk_pot1 - pk_pot2) + pk_pot2, 2))
                                pk_sp.append(abs(pk_pot1 - pk_pot2))

                E_halfs.append(e12)
                peak_separations.append(pk_sp)

        for i, waves in enumerate(E_halfs):
            if i < len(E_halfs):
                print(f'Sweep {i + 1} to {i + 2}:')
                waves.sort()
                waves.reverse()
                for j, wave in enumerate(waves):
                    peak_sep = round(peak_separations[i][j], 3)
                    print(f'\tE1/2 (V): {wave} ({peak_sep})')
        print('\n')

        return E_halfs
