# -*- coding: utf-8 -*-
"""
Methods to plot CV data.

Created on Fri May 26 2023

@author: David Hebert
"""
import matplotlib.pyplot as plt

class CV_Plot:
    """
    A class for plotting cyclic voltammetry data.

    Attributes
    ----------
    voltammogram : :class:`~cv_pro.process.Voltammogram`
        The Voltammogram to plot.
    reference : float
        The reference potential value.
    name : str
        The name of the voltammogram.
    data : dict
        The voltammogram data.
    peaks : list
        List of peak indices for each segment.
    E_halfs : list
        List of E1/2 values for each segment.
    peak_separations : list
        List of peak separations for each segment.
    """

    def __init__(self, voltammogram, plot_start=1, plot_segments=0, view_only=False):
        """
        Initialize the CV_Plot object.

        Parameters
        ----------
        voltammogram : :class:`~cv_pro.process.Voltammogram`
            The voltammogram data.

        """
        self.voltammogram = voltammogram
        self.reference = voltammogram.reference
        self.name = voltammogram.name
        self.data = voltammogram.voltammogram
        self.peaks = voltammogram.peaks
        self.E_halfs = voltammogram.E_halfs
        self.peak_separations = voltammogram.peak_separations

        self.plot_CV(plot_start, plot_segments, view_only)

    def create_plot(self):
        """
        Create the plot figure and axes.

        Returns
        -------
        fig : :class:`matplotlib.figure.Figure`
            The created figure.
        ax : matplotlib.axes.Axes
            The created axes.

        """
        fig, ax = plt.subplots()
        ax.set_xlabel('Potential (V)')
        ax.set_ylabel('Current (A)')
        plt.title(f'{self.name}', fontweight='bold')
        ax.invert_xaxis()
        return fig, ax

    def plot_cv_curves(self, ax, plot_start, plot_segments):
        """
        Plot the CV curves.

        Parameters
        ----------
        ax : :class:`matplotlib.axes.Axes`
            The axes to plot on.
        plot_start : int
            The first segment to plot.
        plot_segments : int
            The total number of segments to plot.

        """
        for i in range(plot_start - 1, plot_start + plot_segments - 1):
            ax.plot(self.data[i]['Potential (V)'] - self.reference,
                    self.data[i]['Current (A)'])

    def plot_peaks(self, ax, plot_segments):
        """
        Plot the peaks on the CV curves.

        Parameters
        ----------
        ax : :class:`matplotlib.axes.Axes`
            The axes to plot on.
        plot_segments : int
            The total number of segments to plot.

        """
        for i in range(plot_segments):
            ax.scatter(self.data[i]['Potential (V)'][self.peaks[i][0]] - self.reference,
                       self.data[i]['Current (A)'][self.peaks[i][0]],
                       color=ax.get_lines()[i].get_color())

            if plot_segments == 1:
                for peak in self.peaks[i][0]:
                    label = f"{round(self.data[i]['Potential (V)'][peak] - self.reference, 3)}"
                    ax.annotate(label, (self.data[i]['Potential (V)'][peak], self.data[i]['Current (A)'][peak]),
                                xytext=(5, 5), textcoords='offset points')

    def plot_e_half_labels(self, ax, plot_start, plot_segments):
        """
        Plot the E1/2 labels and lines.

        Parameters
        ----------
        ax : :class:`matplotlib.axes.Axes`
            The axes to plot on.
        plot_start : int
            The first segment to plot.
        plot_segments : int
            The total number of segments to plot.

        """
        for i in range(plot_start - 1, plot_start + plot_segments - 2):
            for e_half in self.E_halfs[i]:
                raw_e_half = round(e_half + self.reference, 3)
                index1 = self.data[i]['Potential (V)'][self.data[i]['Potential (V)'] == raw_e_half].index
                index2 = self.data[i + 1]['Potential (V)'][self.data[i + 1]['Potential (V)'] == raw_e_half].index

                try:
                    y1 = self.data[i]['Current (A)'][index1[0]]
                    y2 = self.data[i + 1]['Current (A)'][index2[0]]
                except IndexError:
                    pass
                else:
                    vertical_mid_point = 0.5 * (y1 - y2) + y2
                    label = f"{e_half} V"
                    point = (e_half, vertical_mid_point)

                    ax.annotate(label, point,
                                xytext=(5, 0),
                                textcoords='offset points')

                    if y1 > y2:
                        ax.vlines(e_half, y2, y1, color='lightgray', linestyle=":")
                    else:
                        ax.vlines(e_half, y1, y2, color='lightgray', linestyle=":")

    def add_reference_text(self, ax):
        """
        Add the ferrocenium reference text to the plot.

        Parameters
        ----------
        ax : :class:`matplotlib.axes.Axes`
            The axes to add the text to.

        """
        if self.reference != 0:
            ax.text(0.99, 0.01, f'Fc/Fc+ = {self.reference} V',
                    verticalalignment='bottom',
                    horizontalalignment='right',
                    transform=ax.transAxes,
                    color='gray',
                    fontsize=8)

    def add_e_half_text(self, fig, text_x, text_y, vertical_offset):
        """
        Add the E1/2 and peak separation text to the plot.

        Parameters
        ----------
        fig : :class:`matplotlib.figure.Figure`
            The figure to add the text to.
        text_x : float
            The x-coordinate of the text.
        text_y : float
            The y-coordinate of the text.
        vertical_offset : float
            The vertical offset for each line of text.

        """
        text = 'E' + r'$_{1/2}$' + ' [V] (peak separation [V])'
        fig.text(text_x, text_y, text, ha='left', fontweight='bold')

        for i, (e_half, peak_sep) in enumerate(zip(self.E_halfs, self.peak_separations)):
            if e_half:
                text_y += vertical_offset
                segment_text = f'Segment {i + 1}→{i + 2}: '
                e_half.sort(reverse=True)
                value_text = ', '.join([f'{value} ({round(peak_sep, 3)})'
                                        for value, peak_sep in zip(e_half, peak_sep)])
                segment_text += value_text
                fig.text(text_x, text_y, segment_text, ha='left')

    def plot_CV(self, plot_start, plot_segments, view_only):
        """
        Primary method to plot the cyclic voltammetry data.

        Parameters
        ----------
        plot_start : int, optional
            The first segment to plot. The default is 1.
        plot_segments : int, optional
            The total number of segments to plot. The default is 0 (all segments plotted).
        view_only : bool, optional
            Specify if peaks and E1/2s are also plotted. The default is False. If
            True, `plot_start` and `plot_segments` will have no effect.

        """
        fig, ax = self.create_plot()

        if view_only:
            self.plot_cv_curves(ax, plot_start, plot_segments)
        else:
            self.plot_cv_curves(ax, plot_start, plot_segments)
            self.plot_peaks(ax, plot_segments)
            self.plot_e_half_labels(ax, plot_start, plot_segments)
            self.add_reference_text(ax)
            # self.add_e_half_text(fig, 0.1, -0.05, -0.05)

        print('Close plot window to continue...')
        plt.show()