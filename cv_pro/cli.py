# -*- coding: utf-8 -*-
"""
Run ``cv_pro`` from the command line. With the ``cv_pro`` package installed,
this script can be called directly from the command line with::

    cvp -p myfile.bin

Command Line Arguments
----------------------
-p, --path : string, required
    The path to the CV data, a .bin file.
    Paths containing spaces may need to be wrapped in double quotes "". The
    program will first look for the given path inside the current working
    directory, if not found it will then look at the absolute path and inside
    the root directory (if a root directory has been set).
-fc, --ferrocenium : float, optional
    The relative potential (given in V) of the Fc/Fc+ redox couple used to
    correct the x-axis values.
-sep, --peak_sep_limit : float, optional
    The maximum distance (given in V) between two peaks for them to be considered
    "reversible". If the distance between two peaks if within the limit, E_half
    calculations will be attempted (see :meth:`~cv_pro.process.Voltammogram.find_Ehalfs`).
-r, --root_dir : string, optional
    Set a root directory for where data files are located so you don't have to
    type a full file path every time. For example, if all your CV data is
    stored inside some main directory ``C:/mydata/CV Data/``, you can
    set this as the root directory so that the path given with ``-p`` is
    assumed to be located inside the root directory.
-grd, --get_root_dir : flag, optional
    Print the current root directory to the console.
-crd, --clear_root_dir : flag, optional
    Clear the current root directory.
-v : flag, optional
    Enable view only mode. No data processing is performed and a plot of
    the data set is shown. Default is False.
-t, --trim : int int, optional
    Use ``trim`` to select a specific portion of the CV data. The first value
    ``trim[0]`` is the first sweep to plot or export, and the second value
    ``trim[1]`` is the total number of sweeps to plot or export. For example,
    to show the data starting from the 2nd sweep and show 2 sweeps, use
    ``-t 2 2``.
-tr, --tree : flag, optional
    Print the ``root_directory`` file tree to the console.
-fp, --file_picker : flag, optional
    Interactively pick a .bin file from the console. The file is opened in view
    only mode.

Created on Sat May 27 2023

@author: David Hebert
"""

import argparse
import os
import pickle
from cv_pro.process import Voltammogram
from cv_pro.plots import plot_CV
from cv_pro.file_picker import FilePicker
from cv_pro.export_csv import export_csv


def main():
    """
    Prehandle command line args.

    Handles the args ``-qq``, ``-crd``, ``-r``, ``-grd``, ``-tr``, and ``-fp``
    before starting the processing routine :func:`~cv_pro.cli.proc()`.

    Raises
    ------
    FileNotFoundError
        Raised if the given file path cannot be found.

    Returns
    -------
    None.

    """
    __args = get_args()

    # Testing mode [-qq]
    # Not yet implemented
    if __args.test_mode is True:
        pass

    else:
        parent_directory = os.path.abspath(os.path.join(__file__, os.pardir))
        root_pickle = os.path.normpath(
            os.path.join(parent_directory, 'root_directory.pickle'))

        # Save new root directory [-rd]
        if __args.root_dir is not None:
            if os.path.exists(os.path.normpath(__args.root_dir)):
                with open(root_pickle, 'wb') as f:
                    pickle.dump(__args.root_dir, f)
                print(f'New root directory: {__args.root_dir}')
            else:
                print('Error: Directory does not exist.')

        # Handle loading or clearing root directory
        if os.path.exists(root_pickle):
            if __args.clear_root_dir is True:  # [-crd]
                os.remove(root_pickle)
                __root = None
                print('Cleared root directory.')
            else:  # Load root directory
                with open(root_pickle, 'rb') as f:
                    __root = pickle.load(f)
        else:
            __root = None

        # Print root directory [-gdr]
        if __args.get_root_dir is True:
            print(f'root directory: {__root}')

        # File picker [-fp]
        if __args.file_picker is True:
            if __root is not None:
                __args.path = FilePicker(__root).pick_file()
                __args.view = True

        if __args.tree is True:  # [-tr]
            FilePicker(__root).tree()

        # Path handling and run proc script
        if __args.path is not None:
            '''
            First check if the given path exists in the current working directory
            or by absolute path. The absolute path will be checked if the given
            path is in a different drive than the current working directory.
            '''
            if os.path.exists(os.path.join(os.getcwd(), __args.path)):
                __args.path = os.path.join(os.getcwd(), __args.path)
                proc(__args)
            # Secondly, check for given path inside root directory.
            elif __root is not None and os.path.exists(os.path.join(__root, __args.path)):
                __args.path = os.path.join(__root, __args.path)
                proc(__args)
            else:
                raise FileNotFoundError(
                    f'No such file or directory could be found: "{__args.path}"')


def proc(__args):
    """
    Process data.

    Initializes a :class:`~cv_pro.process.Voltammogram` with the
    given ``__args``, plots the result, and prompts the user for exporting.

    Parameters
    ----------
    __args : :class:`argparse.Namespace`
        Holds the arguments given at the command line.

    Returns
    -------
    None.

    """
    if __args.view is True:
        data = Voltammogram(__args.path, view_only=True)

        print('\nPlotting data...')

        plot_CV(data, view_only=True)

    else:
        # Get CV data
        data = Voltammogram(__args.path,
                            reference=__args.ferrocenium,
                            peak_sep_limit=__args.peak_sep_limit)

        # Plot CV data
        if __args.trim is None:
            plot_CV(data)
        else:
            data_start, segments = __args.trim

            # Check values
            if data_start > len(data.voltammogram):
                data_start = len(data.voltammogram) - 1

            if data_start + segments > len(data.voltammogram) or segments == 0:
                segments = len(data.voltammogram) - (data_start - 1)

            plot_CV(data, data_start, segments)

        def prompt_for_export():
            """
            Ask the user if they wish to export the processed data.

            Accepts a Y or N response.

            Returns
            -------
            None. Calls :func:`~cv_pro.export_csv.export_csv`.

            """
            # Ask user if data should be exported
            user_input = input('\nExport CV data? (Y/N): ')

            # Check user input is Y or N.
            while user_input.lower() not in ['y', 'n']:
                user_input = input('\nY/N: ')
            if user_input.lower() == 'y':
                pass
                export_csv(data, data_start, segments)
            elif user_input.lower() == 'n':
                pass

        prompt_for_export()


def get_args():
    """
    Initialize an ``ArgumentParser`` and parse command line arguments.

    Returns
    -------
    parser : :class:`argparse.ArgumentParser`

    """
    parser = argparse.ArgumentParser(description='Process CV Data Files')
    help_msg = {
        'path': 'Process .bin CV data file at the given path.',
        'ferrocenium': 'Set the relative potential of the Fc/Fc+ couple.',
        'peak_sep_limit': 'Set the peak separation limit in V when finding E1/2s.',
        'trim': '''2 args: Trim data from sweep __ and show __ total sweeps.
                    The first value is the first sweep to plot and the second
                    value is the value is the total number of sweeps to plot.''',
        'root_dir': '''Set a root directory where data files are located so you
                       don't have to type a full path every time.''',
        'get_root_dir': '''Print the root directory to the console.''',
        'clear_root_dir': '''Clear the current root directory.''',
        'view': '''Enable view only mode (no data processing).''',
        'tree': 'Show the root directory file tree.',
        'file_picker': 'Choose a .bin file interactively from the command line instead of using -p.',
        'test_mode': 'For testing purposes.'
                }

    parser.add_argument('-p',
                        '--path',
                        action='store',
                        default=None,
                        metavar='',
                        help=help_msg['path'])

    parser.add_argument('-fc',
                        '--ferrocenium',
                        action='store',
                        type=float,
                        default=0,
                        metavar='',
                        help=help_msg['ferrocenium'])

    parser.add_argument('-sep',
                        '--peak_sep_limit',
                        action='store',
                        type=float,
                        default=0.2,
                        metavar='',
                        help=help_msg['peak_sep_limit'])

    parser.add_argument('-t',
                        '--trim',
                        action='store',
                        type=int,
                        nargs=2,
                        default=(1, 0),
                        metavar='',
                        help=help_msg['trim'])

    parser.add_argument('-rd',
                        '--root_dir',
                        action='store',
                        default=None,
                        metavar='',
                        help=help_msg['root_dir'])

    parser.add_argument('-grd',
                        '--get_root_dir',
                        action='store_true',
                        default=False,
                        help=help_msg['get_root_dir'])

    parser.add_argument('-crd',
                        '--clear_root_dir',
                        action='store_true',
                        default=False,
                        help=help_msg['clear_root_dir'])

    parser.add_argument('-v',
                        '--view',
                        action='store_true',
                        default=False,
                        help=help_msg['view'])

    parser.add_argument('-tr',
                        '--tree',
                        action='store_true',
                        default=False,
                        help=help_msg['tree'])

    parser.add_argument('-fp',
                        '--file_picker',
                        action='store_true',
                        default=False,
                        help=help_msg['file_picker'])

    parser.add_argument('-qq',
                        '--test_mode',
                        action='store_true',
                        default=False,
                        help=help_msg['test_mode'])

    return parser.parse_args()
