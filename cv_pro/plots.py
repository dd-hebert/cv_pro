# -*- coding: utf-8 -*-
"""
Methods to plot CV data.

Created on Fri May 26 2023

@author: David Hebert
"""
import matplotlib.pyplot as plt


def plot_CV(voltammogram, plot_start=1, plot_segments=0, view_only=False):
    """
    Primary :class:`~cv_pro.process.Voltammogram` plotting function.

    Parameters
    ----------
    voltammogram : :class:`~cv_pro.process.Voltammogram`
        The voltammogram to be plotted.
    plot_start : int, optional
        The first sweep to plot. The default is 1.
    plot_segments : int, optional
        The total number of sweeps to plot. The default is 0 (all sweeps plotted).
    view_only : True or False, optional
        Specify if peaks and E1/2s are also plotted. The default is False. If
        True, ``plot_start`` and ``plot_segments`` will have no effect.

    Returns
    -------
    None. Shows a plot.

    """
    reference = voltammogram.reference
    name = voltammogram.name
    data = voltammogram.voltammogram

    # Plot
    _, ax = plt.subplots()
    ax.set(xlabel='Potential (V)', ylabel='Current (A)')
    plt.title(f'{name}', fontweight='bold')
    ax.invert_xaxis()

    if view_only is True:
        # Just plot CV curves
        for i in range(plot_start - 1, len(data)):
            plt.plot(data[i]['Potential (V)'] - reference,
                     data[i]['Current (A)'])
    else:
        # Plot CV curves and extra labels and lines
        peaks = voltammogram.peaks
        E_halfs = voltammogram.E_halfs

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

        if reference != 0:
            ax.text(0.99, 0.01, f'Fc/Fc+ = {reference} V',
                    verticalalignment='bottom',
                    horizontalalignment='right',
                    transform=ax.transAxes,
                    color='gray',
                    fontsize=8)

    print('Close plot window to continue...')
    plt.show()
