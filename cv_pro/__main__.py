# -*- coding: utf-8 -*-
"""
cv_pro main script.

Created on Sat May 27 2023

@author: David Hebert
"""

import sys
import cv_pro.cli


def main():
    """Run cv_pro from cli script entry point."""
    return cv_pro.cli.main()


if __name__ == '__main__':
    sys.exit(main())
