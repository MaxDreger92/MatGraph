"""
| Author: Mike Werezak <mike.werezak@nrcan-rncan.gc.ca>
| Created: 2024/02/22
"""

from __future__ import annotations

import os.path
from typing import TYPE_CHECKING

import kbio.c_utils

if TYPE_CHECKING:
    pass

__all__ = (
    'BIN_PATH',
    'ECLIB_PATH',
    'BLFIND_PATH',
    'ECLIB_NAME',
    'BLFIND_NAME',
)


BIN_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'bin'))

if kbio.c_utils.c_is_64b:
    ECLIB_NAME  = "EClib64.dll"
    BLFIND_NAME = "blfind64.dll"
else:
    ECLIB_NAME = "EClib.dll"
    BLFIND_NAME = "blfind.dll"

ECLIB_PATH  = os.path.join(BIN_PATH, ECLIB_NAME)
BLFIND_PATH = os.path.join(BIN_PATH, BLFIND_NAME)
