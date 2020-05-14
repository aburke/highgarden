"""
General helper functions for singer related processes
"""

import glob
import os

from utils.venv_tool import pipeline_home
from typing import List


def get_io_modules() -> List[str]:
    ''' Get list singer io modules
    (following modules should have corresponding template files) '''
    path_desc = os.path.join(
        pipeline_home,
        'singer_io',
        '*.py'
    )
    modules = [os.path.split(m)[-1].replace('.py', '')
               for m in glob.glob(path_desc)]
    exclusions = [
        '__init__',
        'singer_device'
    ]
    return [m for m in modules if m not in exclusions]

