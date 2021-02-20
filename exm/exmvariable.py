#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# exmvariable.py
# Description: Definition of a CSP variable
# -----------------------------------------------------------------------------
#
# Started on <vie 05-02-2021 21:34:16.053032722 (1612557256)>
# Carlos Linares López <carlos.linares@uc3m.es>
#

"""
Definition of a CSP variable
"""

# imports
# -----------------------------------------------------------------------------
import datetime

if __package__ is None or __package__ == '':
    import exmconstraints
else:
    from . import exmconstraints

# globals
# -----------------------------------------------------------------------------

# errors
ERROR_UNKNOWN_EQ_TYPE = "{0} is not a legal type for eq comparisons with EXM Variables"

# -----------------------------------------------------------------------------
# EXMVariable
#
# Subjects are EXM CSP variables. They are just stored as ordinary instances of
# a subject which contain information about the name, course and semester.
#
# In addition, variables contain other relevant information:
#
#     + The user binary and unit data and time constraints
#     + The setup time
#     + The sheetname, column and row where this variable was declared in
#       the EXM master spreadsheet
# -----------------------------------------------------------------------------
class EXMVariable():
    """Subjects are EXM CSP variables. They are just stored as ordinary instances of
       a subject which contain information about the name, course and semester.

       In addition, variables contain other relevant information:

          + The user binary and unit data and time constraints
          + The setup time
          + The sheetname, column and row where this variable was declared in
            the EXM master spreadsheet

    """

    def __init__(self,
                 grade: str, name: str, course: int, semester: int,
                 exmdate: datetime.datetime, exmtime: datetime.time,
                 setup: int, sheetname: str, column: str, row: int):
        """An EXM CSP variable is characterized with the information used for
           characterizing subjects: grade, name, course and semester. All these
           fields are mandatory.

           In addition, EXM CSP variables are indexed by their location in the
           master spreadsheet ---so that all subjects are assumed to be
           different unless stated otherwise

        """

        # copy the attributes
        (self._grade, self._name, self._course, self._semester, self._date, self._time, self._setup) = \
            (grade, name, course, semester, exmdate, exmtime, setup)

        # compute now the cellname in the format used in the spreadsheet
        self._cellname = "$" + sheetname + "." + column + str(row)

        # now initialize sets for both unit and binary date and time constraints
        # of this EXM CSP variable
        self._date_uniconstraints = exmconstraints.EXMConstraints()
        self._time_uniconstraints = exmconstraints.EXMConstraints()
        self._date_biconstraints = exmconstraints.EXMConstraints()
        self._time_biconstraints = exmconstraints.EXMConstraints()

    def __eq__(self, other):
        """Return true if and only if this instance and other are the same and false
           otherwise

           If other is given as a string it returns true if and only if the
           cellname of this instance equals the given string; otherwise, if
           other is another EXM variable, then it returns true if and only if
           they hvae the same cellname. In any other case an exception is raised

        """

        # certainly, if two EXM CSP Variables are created with the same cellname
        # but different concepts then an inconsistency happens and as far as
        # this method is concerned, they are strictly the same

        # if other is given as a string:
        if isinstance(other, str):
            return self._cellname == other

        # if, on the other hand, it has been given as an EXM variable
        if isinstance(other, EXMVariable):
            return self._cellname == other.get_cellname()

        # here, raise an exception. No other comparisons are allowed
        raise TypeError(ERROR_UNKNOWN_EQ_TYPE.format(other))

    def __format__(self, format_spec):
        """Evaluates format string literals"""

        return "{0:{f}}".format(self.__str__(), f=format_spec)

    def __hash__(self):
        """Return a hash key of this instance"""

        return hash(self._cellname)

    def __lt__(self, other):
        """Return self < other"""

        return self._cellname < other.get_cellname()

    def __str__(self):
        """Provides a human readable version of the contents of this instance"""

        output = "[{0: <12}] {1: <90} [{2}.{3}] >{4: > 4} (".format(self._cellname,
                                                                    self._name,
                                                                    self._course,
                                                                    self._semester,
                                                                    self._setup)
        if self._date == datetime.datetime.fromordinal(1):
            output += "-"*10 + " "
        else:
            output += "{0} ".format(self._date.date())

        if self._time == datetime.time():
            output += "-"*8 + ")"
        else:
            output += "{0})".format(self._time)

        return output

    def get_grade(self):
        "Return the grade of this EXM CSP Variable"

        return self._grade

    def get_name(self):
        "Return the name of this EXM CSP Variable"

        return self._name

    def get_course(self):
        "Return the course of this EXM CSP Variable"

        return self._course

    def get_semester(self):
        "Return the semester of this EXM CSP Variable"

        return self._semester

    def get_date(self):
        """Return the user-predefined date for this variable"""

        return self._date

    def get_time(self):
        """Return the user-predefined time for this variable"""

        return self._time

    def get_setup(self):
        """Return the user-predefined setup time for this variable"""

        return self._setup

    def get_cellname(self):
        "Return the cellname of this EXM CSP Variable"

        return self._cellname

    def get_date_uniconstraints(self):
        """Return the set of unit date constraints of this EXM CSP variable"""

        return self._date_uniconstraints

    def get_time_uniconstraints(self):
        """Return the set of unit time constraints of this EXM CSP variable"""

        return self._time_uniconstraints

    def get_date_biconstraints(self):
        """Return the set of binary date constraints of this EXM CSP variable"""

        return self._date_biconstraints

    def get_time_biconstraints(self):
        """Return the set of binary time constraints of this EXM CSP variable"""

        return self._time_biconstraints

    def set_date(self, value: datetime.datetime):
        """set the date of this instance"""

        self._date = value

    def set_time(self, value: datetime.time):
        """set the time of this instance"""

        self._time = value

    def set_date_uniconstraints(self, value: list):
        """Add the constraints given in value as unit date constraints of this EXM CSP
           variable

        """

        # just simply add all constraints indexed by this variable
        for iconstraint in value:
            self._date_uniconstraints[self._cellname] = [iconstraint]

    def set_time_uniconstraints(self, value: list):
        """Add the constraints given in value as unit time constraints of this EXM CSP
           variable

        """

        # just simply add all constraints indexed by the variable they refer to
        for iconstraint in value:
            self._time_uniconstraints[self._cellname] = [iconstraint]

    def set_date_biconstraints(self, value: list):
        """Add the constraints given in value as binary date constraints of this EXM CSP
           variable

        """

        # just simply add all constraints indexed by the variable they refer to
        for iconstraint in value:
            self._date_biconstraints[iconstraint.get_var()] = [iconstraint]

    def set_time_biconstraints(self, value: list):
        """Add the constraints given in value as binary time constraints of this EXM CSP
           variable

        """

        # just simply add all constraints indexed by the variable they refer to
        for iconstraint in value:
            self._time_biconstraints[iconstraint.get_var()] = [iconstraint]

    def str_date_uniconstraints(self):
        """Return a string representing information about all unit date constraints"""

        output = '     {0}'.format("Unit date constraints:")
        for ikey in self._date_uniconstraints.keys():
            for ivalue in self._date_uniconstraints[ikey]:
                output += " {0}".format(ivalue)
        return output

    def str_time_uniconstraints(self):
        """Return a string representing information about all unit time constraints"""

        output = '     {0}'.format("Unit time constraints:")
        for ikey in self._time_uniconstraints.keys():
            for ivalue in self._time_uniconstraints[ikey]:
                output += " {0}".format(ivalue)
        return output

    def str_date_biconstraints(self):
        """Return a string representing information about all binary date constraints"""

        output = '     {0}'.format("Binary date constraints:")
        for ikey in self._date_biconstraints.keys():
            for ivalue in self._date_biconstraints[ikey]:
                output += " {0}".format(ivalue)
        return output

    def str_time_biconstraints(self):
        """Return a string representing information about all binary time constraints"""

        output = '     {0}'.format("Binary time constraints:")
        for ikey in self._time_biconstraints.keys():
            for ivalue in self._time_biconstraints[ikey]:
                output += " {0}".format(ivalue)
        return output


# mode:python
# fill-column:80
# End:
