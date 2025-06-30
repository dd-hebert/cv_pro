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
        cv_traces,
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
        self.cv_traces = cv_traces
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
            # self._add_e_half_text(fig, 0.1, -0.05, -0.05)

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
        for _, segment in self.cv_traces.items():
            seg = segment.dropna()
            ax.plot(seg.index, seg)

    def _plot_peaks(self, ax):
        for (segment, peaks), line in zip(self.peaks.items(), ax.get_lines()):
            potentials = self.cv_traces.index[peaks]
            currents = self.cv_traces[segment].iloc[peaks]
            color = line.get_color()
            ax.scatter(potentials, currents, color=color)

            if len(self.cv_traces.columns) == 1:
                for peak in peaks:
                    potential = self.cv_traces.index[peak]
                    current = self.cv_traces[segment].iloc[peak]
                    label = f'{round(potential, 3)}'
                    point = (potential, current)
                    ax.annotate(label, point, xytext=(5, 5), textcoords='offset points')

    def _plot_e_half_labels(self, ax):
        for i in range(len(self.E_halfs)):
            for e_half in self.E_halfs[i]:
                column = self.cv_traces.columns[i]
                seg = self.cv_traces[column]

                next_column = self.cv_traces.columns[i + 1]
                next_seg = self.cv_traces[next_column]

                raw_e_half = round(e_half, 3)

                try:
                    y1 = seg.loc[raw_e_half]
                    y2 = next_seg.loc[raw_e_half]
                except KeyError:
                    pass
                else:
                    vertical_mid_point = 0.5 * (y1 - y2) + y2
                    label = f'{e_half} V'
                    point = (e_half, vertical_mid_point)

                    ax.annotate(label, point, xytext=(5, 0), textcoords='offset points')

                    if y1 > y2:
                        ax.vlines(e_half, y2, y1, color='lightgray', linestyle=':')
                    else:
                        ax.vlines(e_half, y1, y2, color='lightgray', linestyle=':')

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

    def _add_e_half_text(self, fig, text_x, text_y, vertical_offset):
        text = 'E' + r'$_{1/2}$' + ' [V] (peak separation [V])'
        fig.text(text_x, text_y, text, ha='left', fontweight='bold')

        for i, (e_half, peak_sep) in enumerate(
            zip(self.E_halfs, self.peak_separations)
        ):
            if e_half:
                text_y += vertical_offset
                segment_text = f'Segment {i + 1}→{i + 2}: '
                e_half.sort(reverse=True)
                value_text = ', '.join(
                    [
                        f'{value} ({round(peak_sep, 3)})'
                        for value, peak_sep in zip(e_half, peak_sep)
                    ]
                )
                segment_text += value_text
                fig.text(text_x, text_y, segment_text, ha='left')

    def _add_sweep_direction_arrow(self, ax):
        segment_midpoint = len(self.data[self.plot_start - 1]) // 2
        arrow_x1 = (
            self.data[self.plot_start - 1]['Potential (V)'].iloc[segment_midpoint + 20]
            - self.reference
        )
        arrow_x2 = (
            self.data[self.plot_start - 1]['Potential (V)'].iloc[segment_midpoint]
            - self.reference
        )

        arrow_y1 = self.data[self.plot_start - 1]['Current (A)'].iloc[
            segment_midpoint + 20
        ]
        arrow_y2 = self.data[self.plot_start - 1]['Current (A)'].iloc[segment_midpoint]

        arrow_width = 0.5
        arrow_headwidth = 6
        arrow_headlength = 6
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
