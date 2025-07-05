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
    voltammogram : :class:`~cv_pro.voltammogram.Voltammogram`
        The Voltammogram to plot.
    reference : float
        The reference potential value.
    name : str
        The name of the voltammogram.
    data : :class:`pandas.DataFrame`
        The voltammogram data.
    peaks : list
        List of peak indices for each segment.
    E_halfs : list
        List of E1/2 values for each segment.
    peak_separations : list
        List of peak separations for each segment.
    """

    def __init__(
        self,
        voltammogram,
        segments,
        view_only=False,
        pub_quality=False,
    ):
        """
        Initialize the CV_Plot object.

        Parameters
        ----------
        voltammogram : :class:`~cv_pro.process.Voltammogram`
            The voltammogram data.
        plot_start : int, optional
            The first segment to plot. The default is 1 (first segment).
        plot_segments : int, optional
            The total number of segments to plot. The default is 0 (all segments plotted).
        view_only : bool, optional
            Specify if peaks and E1/2s are also plotted. The default is False. If
            True, `plot_start` and `plot_segments` will have no effect.
        pub_quality : bool, optional
            Generate a publicatoin-quality plot. The default is False.
        """
        self.segments = segments
        self.reference = voltammogram.reference
        self.name = voltammogram.name
        # self.raw_data = voltammogram.raw_data
        # self.processed_data = voltammogram.processed_data

        if view_only:
            self.plot_CV(view_only=view_only)
        else:
            self.peaks = voltammogram.peaks
            self.E_halfs = voltammogram.E_halfs
            self.peak_separations = voltammogram.peak_separations

            if pub_quality:
                self.plot_CV_publication_quality()
            else:
                self.plot_CV()

    def plot_CV(self, view_only=False):
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
        fig, ax = self._create_plot()

        if view_only:
            self._plot_cv_curves(ax)
        else:
            self._plot_cv_curves(ax)
            self._plot_peaks(ax)
            self._plot_e_half_labels(ax)
            self._add_reference_text(ax)

        plt.show()

    def plot_CV_publication_quality(self):
        """
        Generate a publication-quality plot.

        Parameters
        ----------
        plot_start : int, optional
            The first segment to plot. The default is 1.
        plot_segments : int, optional
            The total number of segments to plot. The default is 0 (all segments plotted).
        """
        fig, ax = self._create_plot()
        plt.title(None)
        plt.xticks(fontsize='small')
        if self.reference != 0:
            plt.xlabel('${{E}}$ (V vs. Fc$^{{0/+}}$)', fontsize='small')
        else:
            plt.xlabel('${{E}}$ (V)', fontsize='small')

        self._plot_cv_curves(ax)
        [line.set(linewidth=2, color='black') for line in ax.get_lines()]

        self._add_sweep_direction_arrow(ax)

        ax.get_yaxis().set_visible(False)
        [ax.spines[side].set_visible(False) for side in ['top', 'left', 'right']]

        ax.set_ylim(ax.get_ylim()[0] * 1.5, ax.get_ylim()[1] * 1.5)
        ax.set_xlim(round(ax.get_xlim()[0], 1), round(ax.get_xlim()[1], 1))

        plt.show()

    def _create_plot(self):
        fig, ax = plt.subplots()
        ax.set_xlabel('Potential (V)')
        ax.set_ylabel('Current (A)')
        plt.title(f'{self.name}', fontweight='bold')
        ax.invert_xaxis()
        return fig, ax

    def _plot_cv_curves(self, ax):
        for segment in self.segments:
            seg = segment.processed.dropna()
            ax.plot(seg)

    def _plot_peaks(self, ax):
        for segment, line in zip(self.segments, ax.get_lines()):
            potentials = segment.processed.index[segment.peaks]
            currents = segment.processed.iloc[segment.peaks]
            color = line.get_color()
            ax.scatter(potentials, currents, color=color)

            if len(self.segments) == 1:
                segment = self.segments[0]
                for peak in segment.peaks:
                    potential = segment.processed.index[peak]
                    current = segment.processed.iloc[peak]
                    label = f'{round(potential, 3)}'
                    point = (potential, current)
                    ax.annotate(label, point, xytext=(5, 5), textcoords='offset points')

    def _plot_e_half_labels(self, ax):
        for current_segment, next_segment in zip(self.segments, self.segments[1:]):
            for ehalf in current_segment.ehalfs:
                e = round(ehalf, 3)

                try:
                    y1 = current_segment.processed.loc[e]
                    y2 = next_segment.processed.loc[e]
                except KeyError:
                    pass
                else:
                    vertical_mid_point = 0.5 * (y1 - y2) + y2
                    label = f'{ehalf} V'
                    point = (ehalf, vertical_mid_point)

                    ax.annotate(label, point, xytext=(5, 0), textcoords='offset points')

                    if y1 > y2:
                        ax.vlines(ehalf, y2, y1, color='lightgray', linestyle=':')
                    else:
                        ax.vlines(ehalf, y1, y2, color='lightgray', linestyle=':')

    def _add_reference_text(self, ax):
        if self.reference != 0:
            ax.text(
                0.99,
                0.01,
                f'Fc/Fc+ = {self.reference} V',
                verticalalignment='bottom',
                horizontalalignment='right',
                transform=ax.transAxes,
                color='gray',
                fontsize=8,
            )

    def _add_sweep_direction_arrow(self, ax):
        segment = self.segments[0]
        segment_midpoint = len(segment.processed) // 2
        arrow_length = 20
        arrow_width = 0.5
        arrow_headwidth = 8
        arrow_headlength = 8

        arrow_x1 = segment.processed.index[segment_midpoint + arrow_length]
        arrow_x2 = segment.processed.index[segment_midpoint]

        arrow_y1 = segment.processed.iloc[segment_midpoint + arrow_length]
        arrow_y2 = segment.processed.iloc[segment_midpoint]

        ax.annotate(
            '',
            xy=(arrow_x1, arrow_y1),
            xytext=(arrow_x2, arrow_y2),
            arrowprops=dict(
                width=arrow_width,
                headwidth=arrow_headwidth,
                headlength=arrow_headlength,
                color='black',
            ),
        )
