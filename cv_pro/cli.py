# -*- coding: utf-8 -*-
"""
Run ``cv_pro`` from the command line.

With the ``cv_pro`` package installed, this script can be called directly from
the command line with::

    cvp p myfile.bin

The accepted commands and their options are given below. The shorthand for commands
are given in parenthesis.

Commands
========

process (p, proc)
-----------------
Usage: ``cvp p <path> <options>``, ``cvp proc <path> <options>``, or ``cvp process <path> <options>``

Positional (required) Args
^^^^^^^^^^^^^^^^^^^^^^^^^^
path : str, required
    The path to a .bin file. Paths containing spaces should be wrapped in double
    quotes "". The script will first look for the file inside the current
    working directory, then look at the absolute path, and lastly
    inside the root directory (if a root directory has been set).

Optional Args
^^^^^^^^^^^^^
-v : flag, optional
    Enable view only mode. No data processing is performed and a plot of
    the data set is shown. Default is False.
-ne, --no-export : flag, optional
    Bypass the "export data" prompt at the end of the script.
-tr, --trim : int int, optional
    Use ``trim`` to select a specific portion of the CV data. The first value
    ``trim[0]`` is the first segment to plot or export, and the second value
    ``trim[1]`` is the total number of segments to plot or export. For example,
    to show the data starting from the 2nd segment and show 2 segments, use
    ``-t 2 2``.
-fc, --ferrocenium : float, optional
    The relative potential (given in V) of the Fc+/Fc redox couple used to
    correct the x-axis values.
-sep, --peak-sep-limit : float, optional
    The maximum distance (given in V) between two peaks for them to be considered
    "reversible". If the distance between two peaks if within the limit, E_half
    calculations will be attempted (see :meth:`~cv_pro.process.Voltammogram.find_Ehalfs`).
-pub, --pub-quality : flag, optional
    Generate a publication-quality plot. (BETA)

multiview (mv)
--------------
Usage: ``cvp multiview <options>`` or ``cvp mv <options>``

View multiple .bin files from the command line.

Optional Args
^^^^^^^^^^^^^
-f, --filters : arbitrary number of strings, optional
    A sequence of search filter strings. For example, passing ``-f copper A``
    will open .bin files which contain 'copper' OR 'A' in their filename.
    Passing no filters opens all .bin files in the current working directory.
-a, --and-filter: flag, optional
    Enable AND filter mode. For example, passing ``-f copper A -a`` will open
    .bin files which contain both 'copper' AND 'A' in their filename. Default is OR filter mode.

config (cfg)
------------
Usage: ``cvp config <option>`` or ``cvp cfg <option>``

List, edit, reset, or delete the script configuration settings.

Optional Args
^^^^^^^^^^^^^
-l, --list : flag, optional
    Print the current configuration settings to the console.
-e, --edit : flag, optional
    Edit configuration settings. Will prompt the user for a selection of
    configuration settings to edit.
-r, --reset : flag, optional
    Reset configuration settings back to their default value. Will prompt the user
    for a selection of configuration settings to reset.
-delete : flag, optional
    Delete the config file and directory. The config directory will only be deleted
    if it is empty.

tree
----
Usage: ``cvp tree``

Print the root directory file tree to the console.

Created on Sat May 27 2023

@author: David Hebert
"""

import sys

from rich import print

from cv_pro import __author__, __version__
from cv_pro.commands import get_args
from cv_pro.utils.config import CONFIG, PRIMARY_COLOR

sys.tracebacklimit = 0


class CLI:
    """
    Command line interface class.

    Attributes
    ----------
    args : :class:`argparse.Namespace`
        Parsed command-line arguments.
    """

    def __init__(self):
        self.args = get_args()
        self.args.config = CONFIG
        self.apply_config()

        if hasattr(self.args, 'func'):
            self.args.func(args=self.args)

        else:
            print(self._splash())

    def apply_config(self):
        for arg_name, value in self.args.config.broadcast():
            setattr(self.args, arg_name, value)

    def _splash(self) -> str:
        splash = [
            '                                                      ',
            '  ███████ ███   ███         ███████   ██████  ██████  ',
            ' ███      ███   ███         ███  ███ ███     ███  ███ ',
            ' ███       ███ ███          ███  ███ ███     ███  ███ ',
            '  ███████   █████   ███████ ███████  ███      ██████  ',
            '                            ███                       ',
            '                            ███                       ',
        ]

        splash = [f'[{PRIMARY_COLOR}]{line}[/{PRIMARY_COLOR}]' for line in splash]
        splash.append(f'Version: {__version__}\nAuthor: {__author__}')
        splash.append('\nFor help with commands, type: cvp -h')

        return '\n'.join(splash)


def main() -> None:
    CLI()
