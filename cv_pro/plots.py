# -*- coding: utf-8 -*-
"""
Created on Fri May 26 23:00:38 2023

@author: David Hebert
"""
import matplotlib.pyplot as plt

def plot_CV(voltammogram, plot_start=0, plot_segments=1):
    reference = voltammogram.reference
    name = voltammogram.name
    peaks = voltammogram.peaks
    E_halfs = voltammogram.E_halfs
    data = voltammogram.voltammogram

    # Plot
    _, ax = plt.subplots()
    ax.set(xlabel='Potential (V)', ylabel='Current (A)')
    plt.title(f'{name}', fontweight='bold')
    ax.invert_xaxis()

    if plot_start > len(data):
        plot_start = len(data) - 1

    if plot_start + plot_segments > len(data):
        plot_segments = len(data) - plot_start

    # Plot CV curves
    for i in range(plot_start - 1, plot_start + plot_segments - 1):
        plt.plot(data[i]['Potential (V)'] - reference,
                 data[i]['Current (A)'])

        # Add markers at peaks
        plt.scatter(data[i]['Potential (V)'][peaks[i][0]] - reference,
                    data[i]['Current (A)'][peaks[i][0]], color='r')

        if plot_segments == 1:
            # Add peak labels if only 1 sweep is plotted
            for peak in peaks[i][0]:
                label = f"{round(data[i]['Potential (V)'][peak] - reference, 3)}"
                point = (data[i]['Potential (V)'][peak],
                          data[i]['Current (A)'][peak])
                text_offset = (data[i]['Potential (V)'][peak],
                                data[i]['Current (A)'][peak])
                plt.annotate(label, point, xytext=text_offset)

        # Plot E1/2 labels and lines
        if i < plot_start + plot_segments - 2:
            for wave in E_halfs[i]:
                # Get raw (uncorrected) E1/2
                raw_e12 = round(wave + reference, 3)
                # Get index where potential = raw E1/2 in sweep i
                index1 = data[i]['Potential (V)'][data[i]['Potential (V)'] == raw_e12].index
                # Get current at raw E1/2 in sweep
                cur1 = data[i]['Current (A)'][index1[0]]
                # Get index where potential = raw E1/2 in next sweep
                index2 = data[i + 1]['Potential (V)'][data[i + 1]['Potential (V)'] == raw_e12].index
                # Get current at raw E1/2 in next sweep
                cur2 = data[i + 1]['Current (A)'][index2[0]]

                vertical_mid_point = 0.5 * (cur1 - cur2) + cur2

                label = f"{wave} V"
                point = (wave, vertical_mid_point)
                plt.annotate(label, point)

                # Check if sweep i is above or below following sweep
                if cur1 > cur2:
                    ax.vlines(wave, cur2, cur1, color='lightgray', linestyle=":")
                else:
                    ax.vlines(wave, cur1, cur2, color='lightgray', linestyle=":")

    ax.text(0.99, 0.01, f'Fc/Fc+ = {reference} V',
             verticalalignment='bottom',
             horizontalalignment='right',
             transform=ax.transAxes,
             color='gray',
             fontsize=8)

    plt.show()
