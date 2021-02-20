#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# exmvalue.py
# Description: Definition of an EXM CSP value
# -----------------------------------------------------------------------------
#
# Started on <sáb 06-02-2021 21:43:56.825695154 (1612644236)>
# Carlos Linares López <carlos.linares@uc3m.es>
#

"""
Definition of an EXM CSP value
"""

# imports
# -----------------------------------------------------------------------------
import datetime


# globals
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# EXMValue
#
# EXM CSP values are timedates
# -----------------------------------------------------------------------------
class EXMValue():
    """EXM CSP values are timedates

    """

    def __init__(self, exmdate, exmtime):
        """An EXM CSP value is the combination of a date and a time

        """

        # copy the attributes
        self._date, self._time = exmdate, exmtime

        # create a single datetime object to represent the value
        self._datetime = datetime.datetime.combine(exmdate, exmtime)

        # initialize the default value for the setup time of this value which is
        # always equal to 24 hours
        self._setup = 24

    def __str__(self):
        """Return a human readable version of this instance"""

        return "{0}".format(self._datetime)

    def get_date(self):
        """Return the date of this value"""

        return self._date

    def get_time(self):
        """Return the time of this value"""

        return self._time

    def get_value(self):
        """return the value of this instance"""

        return self._datetime

    def get_setup(self):
        """return the setup time of this instance"""

        return self._setup

    def set_setup(self, value):
        """set the setup time of this instance"""

        self._setup = value
        return self


# Local Variables:
# mode:python
# fill-column:80
# End:
