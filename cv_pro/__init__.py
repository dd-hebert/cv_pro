# -*- coding: utf-8 -*-
"""
cv_pro
======
A tool for processing CV data files (.bin format) exported from the CH Instruments
CHI760e electrochemical workstation. CV data files in either .bin formats can
be imported, processed, and exported as .csv.

You can run cv_pro directly from the command line using::

    cvp -p <"path"> <optional_args>

Or you can run cv_pro using runpy with::

    python -m cv_pro -p <"path"> <optional_args>

See the documentation or the cli.py docstring from more information on the
optional command line arguments.

github: https://github.com/dd-hebert/cv_pro

Created on Sat May 27 2023

@author: David Hebert
"""

__author__ = 'David Hebert'
__version__ = '0.0.10'
