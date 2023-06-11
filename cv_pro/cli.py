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
-rd, --root_dir : string, optional
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
    ``trim[0]`` is the first segment to plot or export, and the second value
    ``trim[1]`` is the total number of segments to plot or export. For example,
    to show the data starting from the 2nd segment and show 2 segments, use
    ``-t 2 2``.
-tr, --tree : flag, optional
    Print the ``root_directory`` file tree to the console.
-fp, --file_picker : flag, optional
    Interactively pick a .bin file from the console. The file is opened in view
    only mode.
-pub, --pub_quality : flag, optional
    Generate a publication-quality plot.

Created on Sat May 27 2023

@author: David Hebert
"""

import argparse
import os
import pickle
from cv_pro.process import Voltammogram
from cv_pro.plots import CV_Plot
from cv_pro.file_picker import FilePicker
from cv_pro.export_csv import export_csv


def handle_test_mode(args):
    r"""
    Handle the test mode functionality. NOT YET IMPLEMENTED.

    `-qq`

    Test mode only works from inside the repo \...\cv_pro\cv_pro.

    Parameters
    ----------
    args : :class:`argparse.Namespace`
        Parsed command-line arguments.

    Returns
    -------
    None.

    """
    pass


def get_root_pickle():
    """
    Return the path to the root directory pickle file.

    Returns
    -------
    str
        The path to the root directory pickle file.

    """
    parent_directory = os.path.abspath(os.path.join(__file__, os.pardir))
    root_pickle = os.path.normpath(os.path.join(parent_directory, 'root_directory.pickle'))

    return root_pickle


def save_root_directory(args, root_pickle):
    """
    Save a new root directory.

    `-rd`

    Parameters
    ----------
    args : :class:`argparse.Namespace`
        Parsed command-line arguments.
    root_pickle : str
        The path to the root directory pickle file.

    Returns
    -------
    None.

    """
    if os.path.exists(os.path.normpath(args.root_dir)):
        with open(root_pickle, 'wb') as f:
            pickle.dump(args.root_dir, f)
        print(f'New root directory: {args.root_dir}')
    else:
        print('Error: Directory does not exist.')


def handle_root_directory(args, root_pickle):
    """
    Load or clear the root directory from the root directory pickle file.

    `-grd`, `-crd`

    Parameters
    ----------
    args : :class:`argparse.Namespace`
        Parsed command-line arguments.
    root_pickle : str
        The path to the root directory pickle file.

    Returns
    -------
    str or None
        The root directory or None if the pickle file doesn't exist.

    """
    if os.path.exists(root_pickle):
        if args.clear_root_dir is True:  # [-crd]
            os.remove(root_pickle)
            root_dir = None
            print('Cleared root directory.')
        else:
            with open(root_pickle, 'rb') as f:
                root_dir = pickle.load(f)
    else:
        root_dir = None

    return root_dir


def handle_file_picker(args, root_dir):
    """
    Handle the file picker functionality.

    `-fp`

    Parameters
    ----------
    args : :class:`argparse.Namespace`
        Parsed command-line arguments.
    root_dir : str or None
        The root directory.

    Returns
    -------
    None.

    """
    if root_dir is not None:
        if args.file_picker is True:
            args.path = FilePicker(root_dir, '.bin').pick_file()
            args.view = True
    
        if args.tree is True:  # [-tr]
            FilePicker(root_dir, '.bin').tree()


def handle_path(args, root_dir):
    """
    Path handling and runs the proc script.

    Parameters
    ----------
    args : :class:`argparse.Namespace`
        Parsed command-line arguments.
    root_dir : str or None
        The root directory.

    Raises
    ------
    FileNotFoundError
        Raised if the given file path cannot be found.

    Returns
    -------
    None.

    """
    if args.path is not None:
        current_dir = os.getcwd()
        path_exists = os.path.exists(os.path.join(current_dir, args.path))

        if path_exists:
            args.path = os.path.join(current_dir, args.path)
            proc(args)
        elif root_dir is not None and os.path.exists(os.path.join(root_dir, args.path)):
            args.path = os.path.join(root_dir, args.path)
            proc(args)
        else:
            raise FileNotFoundError(f'No such file or directory could be found: "{args.path}"')


def main():
    """
    Prehandles command line args.

    Handles the args ``-qq``, ``-crd``, ``-rd``, ``-grd``, ``-tr``, and ``-fp``
    before starting the processing routine :func:`~cv_pro.cli.proc()`.

    Raises
    ------
    FileNotFoundError
        Raised if the given file path cannot be found.

    Returns
    -------
    None.

    """
    args = get_args()

    # Test mode [-qq]
    if args.test_mode is True:
        handle_test_mode(args)
        return

    root_pickle = get_root_pickle()

    if args.root_dir is not None:
        # Root dir [-rd]
        save_root_directory(args, root_pickle)

    # Load or clear [-crd] root dir
    root_dir = handle_root_directory(args, root_pickle)

    # Print root directory [-gdr]
    if args.get_root_dir is True:
        print(f'root directory: {root_dir}')

    # File picker [-fp] and tree [-tr]
    handle_file_picker(args, root_dir)

    handle_path(args, root_dir)


def proc(args):
    """
    Process data.

    Initializes a :class:`~cv_pro.process.Voltammogram` with the
    given ``args``, plots the result, and prompts the user for exporting.

    Parameters
    ----------
    args : :class:`argparse.Namespace`
        Holds the arguments given at the command line.

    Returns
    -------
    None.

    """
    if args.view is True:
        data = Voltammogram(args.path, view_only=True)
        data_start, segments = _check_trim_values(args, data)

        print('\nPlotting data...')

        CV_Plot(data,
                plot_start=data_start,
                plot_segments=segments, view_only=True)

    else:
        data = Voltammogram(args.path,
                            reference=args.ferrocenium,
                            peak_sep_limit=args.peak_sep_limit)
        data_start, segments = _check_trim_values(args, data)

        CV_Plot(data,
                plot_start=data_start,
                plot_segments=segments,
                pub_quality=args.pub_quality)

        def prompt_for_export():
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
        'trim': '''2 args: Trim data from segment __ and show __ total segments.
                    The first value is the first segment to plot and the second
                    value is the value is the total number of segments to plot.''',
        'root_dir': '''Set a root directory where data files are located so you
                       don't have to type a full path every time.''',
        'get_root_dir': '''Print the root directory to the console.''',
        'clear_root_dir': '''Clear the current root directory.''',
        'view': '''Enable view only mode (no data processing).''',
        'tree': 'Show the root directory file tree.',
        'file_picker': 'Choose a .bin file interactively from the command line instead of using -p.',
        'pub_quality': 'Generate a publication-quality plot.',
        'test_mode': 'For testing purposes.'}

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

    parser.add_argument('-pub',
                        '--pub_quality',
                        action='store_true',
                        default=False,
                        help=help_msg['pub_quality'])

    parser.add_argument('-qq',
                        '--test_mode',
                        action='store_true',
                        default=False,
                        help=help_msg['test_mode'])

    return parser.parse_args()


def _check_trim_values(args, voltammogram):
    data_start, segments = args.trim

    if data_start > len(voltammogram.voltammogram):
        data_start = len(voltammogram.voltammogram) - 1

    if data_start + segments > len(voltammogram.voltammogram) or segments == 0:
        segments = len(voltammogram.voltammogram) - (data_start - 1)

    return data_start, segments
