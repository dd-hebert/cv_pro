"""
Functions for the ``process`` command.

@author: David Hebert
"""

import argparse

from rich import print

from cv_pro.commands import Argument, command
from cv_pro.plots import CV_Plot
from cv_pro.utils.paths import cleanup_path, handle_args_path
from cv_pro.utils.prompts import checkbox
from cv_pro.voltammogram import Voltammogram

HELP = {
    'path': 'Process .bin CV data file at the given path.',
    'view': 'Enable view only mode (no data processing).',
    'no-export': 'Skip the "export data" prompt at the end of the script.',
    'ferrocenium': 'Set the relative potential of the Fc+/Fc couple.',
    'peak-sep-limit': 'Set the peak separation limit in V when finding E1/2s.',
    'trim': '2 integers: Trim the data, keeping segment START through segment END.',
    'pub-quality': 'Generate a publication-quality plot.',
}
ARGS = [
    Argument(
        'path',
        action='store',
        type=cleanup_path,
        nargs='?',
        default=None,
        help=HELP['path'],
    ),
    Argument(
        '-v',
        '--view',
        action='store_true',
        default=False,
        help=HELP['view'],
    ),
    Argument(
        '-ne',
        '--no-export',
        action='store_true',
        default=False,
        help=HELP['no-export'],
    ),
    Argument(
        '-fc',
        '--ferrocenium',
        action='store',
        type=float,
        default=0,
        metavar='',
        help=HELP['ferrocenium'],
    ),
    Argument(
        '-sep',
        '--peak-sep-limit',
        action='store',
        type=float,
        default=0.2,
        metavar='',
        help=HELP['peak-sep-limit'],
    ),
    Argument(
        '-tr',
        '--trim',
        action='store',
        type=int,
        nargs=2,
        default=None,
        metavar=('START', 'END'),
        help=HELP['trim'],
    ),
    Argument(
        '-pub',
        '--pub-quality',
        action='store_true',
        default=False,
        help=HELP['pub-quality'],
    ),
]


@command(args=ARGS, aliases=['p', 'proc'])
def process(args: argparse.Namespace) -> None:
    """
    Process data.

    Initializes a :class:`~cv_pro.voltammogram.Voltammogram` with the
    given ``args``, plots the result, and prompts the user
    for exporting.

    Parser Info
    -----------
    *aliases : p, proc
    *desc : Process a .bin CV data file with the given args, \
        plot the result, and export data (optional).
    *help : Process .bin CV data files.
    """
    handle_args_path(args)

    if args.view is True:
        voltammogram = Voltammogram(args.path, view_only=True)

    else:
        voltammogram = Voltammogram(
            args.path,
            args.trim,
            reference=args.ferrocenium,
            peak_sep_limit=args.peak_sep_limit,
        )

    print('', voltammogram, sep='\n')
    _plot_and_export(args, voltammogram)


def prompt_for_export(voltammogram: Voltammogram) -> list[str]:
    """
    Prompt the user for data export.

    Parameters
    ----------
    voltammogram : :class:`~cv_pro.voltammogram.Voltammogram`
        The :class:`~cv_pro.voltammogram.Voltammogram` to be exported.

    Returns
    -------
    list[str]
        The names of the exported files.
    """
    options = ['Voltammogram (raw)']
    export_map = {'Voltammogram (raw)': [(voltammogram.segments, 'raw', None)]}

    if voltammogram.is_processed:
        key = 'Voltammogram (corrected)'
        options.append(key)
        export_map[key] = [(voltammogram.trimmed_segments, 'processed', 'corrected')]

    user_selection = checkbox('Choose data to export', options)

    if user_selection is None:
        return []

    return [
        voltammogram.export_csv(*file)
        for opt in user_selection
        for file in export_map[opt]
    ]


def _plot_and_export(args: argparse.Namespace, voltammogram: Voltammogram) -> None:
    """Plot a :class:`~cv_pro.voltammogram.Voltammogram` and prompt the user for export."""
    print('\nPlotting data...')
    print('Close plot window to continue...')
    if args.view is True:
        CV_Plot(voltammogram, voltammogram.segments, view_only=True)

    else:
        files_exported = []

        CV_Plot(
            voltammogram, voltammogram.trimmed_segments, pub_quality=args.pub_quality
        )

        if args.no_export is False:
            files_exported.extend(prompt_for_export(voltammogram))

        if files_exported:
            print(f'\nExport location: [repr.path]{args.path.parent}[/repr.path]')
            print('Files exported:')
            [
                print(f'\t[repr.filename]{file}[/repr.filename]')
                for file in files_exported
            ]
