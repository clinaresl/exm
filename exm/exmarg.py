#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# exmarg.py
# Description: Definition of command line arguments to invoke the main script
# -----------------------------------------------------------------------------
#
# Started on <jue 04-02-2021 20:58:36.711415238 (1612468716)>
# Carlos Linares López <carlos.linares@uc3m.es>
#

"""
Definition of command line arguments to invoke the main script
"""

# imports
# -----------------------------------------------------------------------------
import argparse
import sys

if __package__ is None or __package__ == '':
    import exmversion
else:
    from . import exmversion

# functions
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# EXMarg
#
# provides a minimum definition of arguments for scripts processing the exm
# -----------------------------------------------------------------------------
class EXMArg:
    """provides a minimum definition of arguments for exm"""

    def __init__(self):
        """defines the command argument parser"""

        # initialize a parser
        self._parser = argparse.ArgumentParser(description="Script used for processing exam dates")

        # now, add the arguments

        # Group of mandatory arguments
        self._mandatory = self._parser.add_argument_group("Mandatory arguments",
                                                          "The following arguments are required")
        self._mandatory.add_argument('-m', '--master',
                                     required=True,
                                     type=str,
                                     help="location and name of the spreadsheet with information of all subjects and timedates")

        # Group of optional arguments
        self._optional = self._parser.add_argument_group('Optional',
                                                         "The following arguments are optional")
        self._optional.add_argument('-x', '--load-indirects',
                                    action='store_true',
                                    help="By default, only those records matching the selection criteria given by --grade, --course and --semester are loaded. If this flag is enabled, then also those registers appearing in a binary constraint of any variable matching the selection criteria are loaded into the pool var as well")
        self._optional.add_argument('-g', '--grade',
                                    type=str,
                                    help="if given, only the subjects of the given grade are considered")
        self._optional.add_argument('-c', '--course',
                                    type=int,
                                    default=0,
                                    help="if given, only the subjects of the given course are considered")
        self._optional.add_argument('-s', '--semester',
                                    type=int,
                                    default=0,
                                    help="if given, only the subjects of the given semester are considered")
        self._optional.add_argument('-o', '--output',
                                    type=str,
                                    help="name of the output xlsx spreadsheet. If none is given, the name of the master file is extended with '-timetable'")
        self._optional.add_argument('-i', '--ical',
                                    type=str,
                                    help="name of the output ical file. If none is given, an icalendar with the solution is not generated")

        # Group of miscellaneous arguments
        self._misc = self._parser.add_argument_group('Miscellaneous')
        self._misc.add_argument('-v', '--verbose',
                                action='store_true',
                                help="shows additional information")
        self._misc.add_argument('-d', '--debug',
                                action='store_true',
                                help="shows even more information")
        self._misc.add_argument('-V', '--version',
                                action='version',
                                version=" %s %s" %(sys.argv[0], exmversion.__version__),
                                help="output version information and exit")


    def get_parser(self):
        """returns the parser"""

        return self._parser


    def parse(self):
        """parse the command line arguments and returns the result"""

        return self._parser.parse_args()

# Local Variables:
# mode:python
# fill-column:80
# End:
