"""
Setup argparse parsers.

@author: David Hebert
"""

import argparse

main_parser = argparse.ArgumentParser(description='Process CV Data Files')
subparsers = main_parser.add_subparsers(help='Commands')
