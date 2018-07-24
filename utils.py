#! /usr/bin/env python
"""File for keywords with general utilities
"""

import datetime
import re
import os
import sys

# make a reference to path: ../../resources as a module to import libraries
path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
# insert path: "../../resources" (if not previously added)
if path not in sys.path:
    sys.path.insert(0, path)

################################################################################
#===================== Copyright by Continental Automotive GmbH  ===============
################################################################################
#
# Title        : utils.py
#
# Description  : File for keywords with general utilities
#
# Environment  : n/a
#
# Responsible  : Javier Ochoa (uidj5418)
#
# Guidelines   : n/a
#
# Template name: n/a
#
# CASE-Tool    : n/a
#
################################################################################

__author__ = 'Javier Ochoa (uidj5418)'
__version__ = 'See MKS'

# ===============
# Utils Keywords
# ===============

__all__ = [

    # --------------
    # Utils keywords
    # --------------
    'get_datetime'
]


# ================================================
# ==             COMMON UTILITIES               ==
# ================================================
def str_to_bool(string):
    """Converts a string to a boolean state( True / False )
    """
    # check if string is already boolean type to avoid analysis
    if isinstance(string, bool):
        return string
    elif string.strip() in ['True', 'true', 'Yes', 'yes']:
        return True
    elif string.strip() in ['False', 'false', 'No', 'no']:
        return False
    else:
        raise AssertionError("(str_to_bool) '{s}' is an invalid string for boolean conversion".format(s=string))


# ==============================
# [UTILS] KEYWORD: get datetime
# ==============================
def get_datetime(flat_format=False):
    """
    Returns the current Datetime in flat format.
    normal format example:
    flat format example: 04_22_2017__24_12_09

    Parameters:
    - [flat_format] - Flag to return datetime in flat format

    Returns:
    A string with the current Datetime

    Example:
    | ${date_time} = | get_datetime |
    | ${date_time} = | get_datetime | flat_format=True |
    """
    date_time = None
    # get current time from computer
    current_date = datetime.datetime.now()
    # regular expression template to retrieve each component from datetime
    RE_DATE_TEMPLATE = "(\d{4})-(\d{2})-(\d{2})\s{1}(\d{2}):(\d{2}):(\d{2})"
    date_match = re.search(RE_DATE_TEMPLATE, str(current_date))
    if date_match is not None:
        if str_to_bool(flat_format):
            # FLAT FORMAT: "04_22_2017__24_12_09"
            date_time = "{day}_{month}_{year}__{hour}_{min}_{sec}".format(
                day=date_match.group(3),
                month=date_match.group(2),
                year=date_match.group(1),
                hour=date_match.group(4),
                min=date_match.group(5),
                sec=date_match.group(6))
        else:
            # NORMAL FORMAT: "2017-04-20 10:23:06"
            date_time = "{day}-{month}-{year} {hour}:{min}:{sec}".format(
                day=date_match.group(3),
                month=date_match.group(2),
                year=date_match.group(1),
                hour=date_match.group(4),
                min=date_match.group(5),
                sec=date_match.group(6))
    return date_time