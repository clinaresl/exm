#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# utils.py
# Description: Helper functions
# -----------------------------------------------------------------------------
#
# Started on <jue 04-02-2021 21:28:18.019659815 (1612470498)>
# Carlos Linares López <carlos.linares@uc3m.es>
#

"""
Helper functions
"""

# imports
# -----------------------------------------------------------------------------
import logging
import os

if __package__ is None or __package__ == '':
    import colors
else:
    from . import colors

# constants
# -----------------------------------------------------------------------------

# logging

LOG_FORMAT = '[%(color_lvlname_prefix)s %(levelname)-8s:%(color_suffix)s %(color_ascitime_prefix)s %(asctime)s | %(color_suffix)s %(color_name_prefix)s %(name)s%(color_suffix)s]: %(color_prefix)s %(message)s %(color_suffix)s'
LOG_COLOR_PREFIX = {
    "ASCITIME" : colors.insert_prefix(foreground="#008080"),
    "NAME" : colors.insert_prefix(foreground="#00a0a0", italic=True),
    "DEBUG" : colors.insert_prefix(foreground="#99ccff"),
    "INFO" : colors.insert_prefix(foreground="#a0a020"),
    "WARNING" : colors.insert_prefix(foreground="#20aa20", bold=True),
    "ERROR" : colors.insert_prefix(foreground="#ff2020", bold=True),
    "CRITICAL" : colors.insert_prefix(foreground="#ff0000", blink=True)
}


# functions
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# get_filename
#
# return the filename to use for the output xlsx spreadsheet. If the filename
# already ends in ".xlsx" then it uses it. If any other suffix is given, it is
# substituted by ".xlsx". If no suffix is given, "xlsx" is added
# -----------------------------------------------------------------------------
def get_filename(outputname):
    """return the filename to use for the output xlsx spreadsheet. If the filename
       already ends in ".xlsx" then it uses it. If any other suffix is given, it
       is substituted by ".xlsx". If no suffix is given, "xlsx" is added

    """

    split = os.path.splitext(outputname)

    # if ".xlsx" was given, then return the name directly
    if split[-1] == ".xlsx":
        return outputname

    # in any other case (either if no extension was given, or an extension
    # different than ".xlsx") was given, then add the suffix
    return outputname + ".xlsx"


# -----------------------------------------------------------------------------
# setup_logger
#
# setup and configure a logger
# -----------------------------------------------------------------------------
def setup_logger():
    """setup and configure a logger"""

    logger = logging.getLogger('exm')
    logger.addFilter(LoggerContextFilter())
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # and return the logger
    return logger


# -----------------------------------------------------------------------------
# LoggerContextFilter
#
# Creation of a context filter for the logger that adds color support
# -----------------------------------------------------------------------------
class LoggerContextFilter(logging.Filter):
    """
    Creation of a context filter for the logger that adds color support
    """

    def filter(self, record):

        # first inject the colors for all fields in the header
        record.color_lvlname_prefix = LOG_COLOR_PREFIX[record.levelname]
        record.color_ascitime_prefix = LOG_COLOR_PREFIX['ASCITIME']
        record.color_name_prefix = LOG_COLOR_PREFIX['NAME']

        # choose the color as a function of the level of the log message
        record.color_prefix = LOG_COLOR_PREFIX[record.levelname]
        record.color_suffix = colors.insert_suffix()

        return True

# Local Variables:
# mode:python
# fill-column:80
# End:
