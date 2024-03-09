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
-srd, --set_root_dir : string, optional
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
--tree : flag, optional
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
from cv_pro.process import Voltammogram
from cv_pro.plots import CV_Plot
from cv_pro.export_csv import export_csv
from cv_pro.utils.config import Config
from cv_pro.utils.filepicker import FilePicker


class CLI:
    """
    A command line interface class.

    Attributes
    ----------
    args : :class:`argparse.Namespace`
        Parsed command-line arguments.
    config : :class:`configparser.ConfigParser`
        The current CLI settings configuration.

    """

    def __init__(self):
        self.args = self.get_args()
        self.config = self.get_config()

        self.main()

    def get_args(self):
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
            'set_root_dir': '''Set a root directory where data files are located so you
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

        parser.add_argument('-srd',
                            '--set_root_dir',
                            action='store',
                            default=None,
                            metavar='',
                            help=help_msg['set_root_dir'])

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

        parser.add_argument('--tree',
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

    def get_config(self):
        """
        Get the CLI configuration.

        Returns
        -------
        Config : :class:`configparser.ConfigParser`
            The current configuration.

        """
        return Config()

    def get_root_dir(self):
        """
        Get the root directory from the config file.

        Returns
        -------
        str
            The path to the root directory.

        """
        return self.config.config['Settings']['root_directory']

    def modify_root_dir(self, directory):
        """
        Modify the root directory in the config file.

        Parameters
        ----------
        directory : str
            The path to the new root directory.

        Returns
        -------
        None.

        """
        self.config.modify('Settings', 'root_directory', directory)

    def reset_root_dir(self):
        """
        Reset the root directory to the default value.

        Returns
        -------
        None.

        """
        self.config.reset()

    def handle_test_mode(self):
        r"""
        Handle the test mode functionality. NOT YET IMPLEMENTED.

        `-qq`

        Test mode only works from inside the repo \...\cv_pro\cv_pro.

        Returns
        -------
        None.

        """
        pass

    def handle_file_picker(self, root_dir):
        """
        Handle the file picker functionality.

        `-fp`

        Parameters
        ----------
        root_dir : str or None
            The root directory.

        Returns
        -------
        None.

        """
        if root_dir is not None:
            if self.args.file_picker is True:
                self.args.path = FilePicker(root_dir, '.bin').pick_file()
                self.args.view = True

            if self.args.tree is True:  # [--tree]
                FilePicker(root_dir, '.bin').tree()

    def handle_path(self, root_dir):
        """
        Path handling.

        Parameters
        ----------
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
        current_dir = os.getcwd()
        path_exists = os.path.exists(os.path.join(current_dir, self.args.path))

        if path_exists:
            self.args.path = os.path.join(current_dir, self.args.path)
        elif root_dir is not None and os.path.exists(os.path.join(root_dir, self.args.path)):
            self.args.path = os.path.join(root_dir, self.args.path)
        else:
            raise FileNotFoundError(f'No such file or directory could be found: "{self.args.path}"')

    def main(self):
        """
        Prehandles command line args.

        Handles the args ``-qq``, ``-crd``, ``-srd``, ``-grd``, ``--tree``, and ``-fp``.
        Then handles the path before starting the processing routine
        :meth:`~cv_pro.scripts.cli.CLI.proc()`.

        Returns
        -------
        None.

        """
        if self.args.test_mode is True:
            self.handle_test_mode()  # [-qq]
            return

        if self.args.set_root_dir is not None:
            self.modify_root_dir(self.args.set_root_dir)  # [-srd]

        if self.args.clear_root_dir is True:
            self.reset_root_dir()  # [-crd]

        root_dir = self.get_root_dir()

        if self.args.get_root_dir is True:
            print(f'root directory: {root_dir}')  # [-gdr]

        self.handle_file_picker(root_dir)  # [-fp] [--tree]

        if self.args.path is not None:
            self.handle_path(root_dir)
            self.proc()

    def proc(self):
        """
        Process data.

        Initializes a :class:`~cv_pro.process.Voltammogram` with the
        given ``args``, plots the result, and prompts the user for exporting.

        Returns
        -------
        None.

        """
        if self.args.view is True:
            data = Voltammogram(self.args.path, view_only=True)
            data_start, segments = self._check_trim_values(data)

            print('\nPlotting data...')

            CV_Plot(data,
                    plot_start=data_start,
                    plot_segments=segments, view_only=True)

        else:
            data = Voltammogram(self.args.path,
                                reference=self.args.ferrocenium,
                                peak_sep_limit=self.args.peak_sep_limit)
            data_start, segments = self._check_trim_values(data)

            CV_Plot(data,
                    plot_start=data_start,
                    plot_segments=segments,
                    pub_quality=self.args.pub_quality)

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

    def _check_trim_values(self, voltammogram):
        data_start, segments = self.args.trim

        if data_start > len(voltammogram.voltammogram):
            data_start = len(voltammogram.voltammogram) - 1

        if data_start + segments > len(voltammogram.voltammogram) or segments == 0:
            segments = len(voltammogram.voltammogram) - (data_start - 1)

        return data_start, segments


def main():
    """Run the CLI."""
    CLI()
