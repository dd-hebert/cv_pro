# -*- coding: utf-8 -*-
"""
cv_pro main script.

Created on Sat May 27 2023

@author: David Hebert
"""

import sys
import cv_pro.scripts.cli


def main():
    """Run cv_pro from cli script entry point."""
    cli = cv_pro.scripts.cli.CLI()
    return 0


if __name__ == '__main__':
    sys.exit(main())
