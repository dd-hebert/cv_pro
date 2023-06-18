# -*- coding: utf-8 -*-
"""
View multiple .bin files from the command line.

Navigate to a directory containing .bin files and run the command::

    cvpmv -f some search filters

The script will open .bin files which contain any of the supplied search filters
in ``view_only`` mode.

The default search behavior is an `OR` search. You can use supply the ``-a`` or
``--and_filter`` argument to perform an `AND` search::

    cvpmv -f some search filters -a

Now only .bin files with contain all of the search filters in their name will be
opened.

Created on Sat Jun 17 2023

@author: David
"""

import glob
import subprocess
import argparse
from concurrent.futures import ThreadPoolExecutor


def get_args():
    """
    Create an ``ArgumentParser`` and parse command line arguments.

    Returns
    -------
    parser : :class:`argparse.ArgumentParser`

    """
    parser = argparse.ArgumentParser(description='View Multiple CV Data Files')
    help_msg = {
        'search_filters': '''An arbitrary number of search filters''',
        'and_filter': '``and`` filter mode.',
        'or_filter': '``or`` filter mode.'}

    parser.add_argument('-f',
                        '--search_filters',
                        action='store',
                        nargs='*',
                        default='*',
                        metavar='',
                        help=help_msg['search_filters'])

    arg_group = parser.add_mutually_exclusive_group(required=False)
    arg_group.add_argument('-a', '--and_filter', dest='filter_mode', action='store_const',
                           const='and', help=help_msg['and_filter'])
    arg_group.add_argument('-o', '--or_filter', dest='filter_mode', action='store_const',
                           const='or', help=help_msg['or_filter'])

    parser.set_defaults(filter_mode='or')

    return parser.parse_args()


def run_cvp_script(file):
    """
    Run the cvp script in parallel.

    Parameters
    ----------
    file : str
        A file name.

    Returns
    -------
    None.

    """
    try:
        subprocess.run(['cvp', '-p', file, '-v'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except Exception as e:
        print(f"An error occurred while processing the file: {str(e)}")


def filter_files(search_filters, mode='or'):
    """
    Filter a list of files into a set.

    Parameters
    ----------
    search_filters : list
        A list of search filter strings.
    mode : str, optional
        The filter mode, can be ``'and'`` or ``'or'``. The default is ``'or'``.

    Returns
    -------
    files : set
        The filtered files.

    """
    search_patterns = [f'*{pattern}*.bin' for pattern in search_filters]

    if mode == 'and':
        files = set(glob.glob(search_patterns[0]))
        for pattern in search_patterns[1:]:
            files &= set(glob.glob(pattern))
    else:
        files = set([matches for pattern in search_patterns for matches in glob.glob(pattern)])

    if len(files) == 0:
        print("No files found with the specified filter.")
        return

    return files


def multiview(files):
    """
    Run the ``cvp`` script on a list of files in parallel using ThreadPoolExecutor.

    Parameters
    ----------
    files : set
        A set of file names.

    Returns
    -------
    None.

    """
    try:
        with ThreadPoolExecutor(max_workers=50) as executor:
            executor.map(run_cvp_script, files)
    except Exception as e:
        print(f"An error occurred while processing the files: {str(e)}")


def main():
    """
    Get command line args and run :func:`~cv_pro.scripts.multiview.multiview()`.

    Returns
    -------
    None.

    """
    args = get_args()

    multiview(filter_files(args.search_filters, mode=args.filter_mode))
