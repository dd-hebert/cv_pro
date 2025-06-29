"""
Config mapping and default values for cv_pro.

@author: David Hebert
"""

from pathlib import Path

from cv_pro.utils._validate import (
    validate_primary_color,
    validate_root_dir,
)
from cv_pro.utils.paths import cleanup_path

CONFIG_MAP = {
    'root_directory': {
        'section': 'Settings',
        'type': Path,
        'default_str': '',
        'default_val': None,
        'cleanup_func': cleanup_path,
        'validate_func': validate_root_dir,
    },
    'primary_color': {
        'section': 'Settings',
        'type': str,
        'default_str': 'cyan',
        'default_val': 'cyan',
        'cleanup_func': str.strip,
        'validate_func': validate_primary_color,
    },
}
