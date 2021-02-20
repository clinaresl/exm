#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# exm.py
# Description: script for computing the timedates of a collection of exams
# -----------------------------------------------------------------------------
#
# Started on <jue 04-02-2021 21:25:05.882834450 (1612470305)>
# Carlos Linares López <carlos.linares@uc3m.es>
#

"""
script for computing the timedates of a collection of exams
"""

# imports
# -----------------------------------------------------------------------------
import copy
import datetime
import os.path
import re
import sys

import constraint

if __package__ is None or __package__ == '':
    # uses current directory visibility
    import exmarg
    import exmconstraint
    import exmvalue
    import exmvariable
    import exmpoolvar

    import spsreader
    import utils
else:
    # uses current package visibility
    from . import exmarg
    from . import exmconstraint
    from . import exmvalue
    from . import exmvariable
    from . import exmpoolvar

    from . import spsreader
    from . import utils

# globals
# -----------------------------------------------------------------------------

# default logger
LOGGER = utils.setup_logger()

# default setup time measured in hours
DEFAULT_SETUP_TIME = 24

# regular expression used to split constraints
RE_SEP_CONSTRAINT = re.compile(",")

# regular expression used to process cell names
RE_CELLNAME = re.compile(r'^\s*\$((?P<sheet>.*))\.(?P<column>[a-zA-Z]+)(?P<row>\d+)')

# regular expressions used to process unit date and time constraints
RE_UNI_DATE_CONSTRAINT = re.compile(r'^\s*(?P<operator>(=|!=|<|<=|>|>=)?)\s*(?P<year>\d{4})[/-](?P<month>\d{1,2})[/-](?P<day>\d{1,2})')
RE_UNI_TIME_CONSTRAINT = re.compile(r'^\s*(?P<operator>(=|!=|<|<=|>|>=)?)\s*(?P<hour>\d{1,2}):(?P<minutes>\d{1,2})(?P<seconds>(:\d{1,2})?)\s*(?P<qualifier>(AM|PM)?)')

# regular expression used to process binary constraints individually
RE_BICONSTRAINT = re.compile(r'^\s*(?P<operator>(=|!=|<|<=|>|>=)?)\s*((?P<sheet>\$.+)\.)?(?P<cell>[a-zA-Z]+\d+)')

# debug
DEBUG_DOMAIN_LENGTH = "[{0}] {1}: {2} feasible values"

# info
INFO_NEWVAR = "{0}"
INFO_NEW_INDIRECT_VAR = "{0}"
INFO_VARS_PROCESSED = "'{0}' processed ({1} total variables generated)"
INFO_INDIRECT_VARS_PROCESSED = "{0} new indirect variables have been generated ({1} total variables generated)"
INFO_NO_INDIRECT_VARS_PROCESSED = "No new indirect variables have been generated"
INFO_VARS_LENGTH = "{0} values generated"
INFO_CONSTRAINTS_LENGTH = "{0} constraints posted"
INFO_SOLUTION_FOUND = "Solution found ..."

# warning
WARNING_SKIP = "'{0}' skipped"

# errors
ERROR_OUTPUT_SPREADSHEET = "Either the output spreadsheet '{0}' already exists or it can not be created"
ERROR_OUTPUT_ICAL = "Either the ical file '{0}' already exists or it can not be created"
ERROR_UNKNOWN_TYPE = "Unknown type of '{0}'"
ERROR_UNI_DATE_CONSTRAINT = "'{0}' is not a legal unit date constraint specification"
ERROR_UNI_TIME_CONSTRAINT = "'{0}' is not a legal unit time constraint specification"
ERROR_BICONSTRAINT = "'{0}' is not a legal binary constraint specification"
ERROR_CONSTRAINT = "Syntax error: The content '{0}' found in the register '${1}.{2}' is not a valid constraint specification"
ERROR_UNKNOWN_TYPE_DATE = "Syntax error: Unknown type of '{0}' found in the date of record {1}"
ERROR_UNKNOWN_TYPE_TIME = "Syntax error: Unknown type of '{0}' found in the time of record {1}"
ERROR_TIME_IN_DATE = "Syntax error: Cell {0} contains a time specification but it is a date cell: {1}"
ERROR_DATE_IN_TIME = "Syntax error: Cell {0} contains a time specification but it is a time cell: {1}"
ERROR_SYNTAX_ERROR_REGISTER = "Syntax error in the register name '{0}'"
ERROR_UNKNOWN_REGISTER = "The register ${0}.{1} has not been found in {2}"
ERROR_EMPTY_DOMAIN = "Empty domain for variable '{0}'"
ERROR_SOLUTION_NOT_FOUND = "No solution found!"


# functions
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# compute the normalized absolute path of the given filename making sure it ends
# in the specified suffix
# -----------------------------------------------------------------------------
def normalize_filename(filename: str, suffix: str):
    """compute the normalized absolute path of the given filename making sure it ends
       in the specified suffix

    """

    # first, compute the filename making sure it ends in the given suffix
    filename = os.path.join(os.path.dirname(filename),
                            os.path.basename(os.path.splitext(filename)[0]) + suffix)

    # expand user variables and return the absolute path of the resulting filename
    return os.path.abspath(os.path.expanduser(filename))


# -----------------------------------------------------------------------------
# return the name of the output spreadsheet. If an output name is given, then it
# is selected; otherwise, the input name is extended with '-timetable'. It also
# verifies that the output name ends with the right suffix.
#
# If either the resulting file already exists, or it is not possible to create
# it, then an error is issued and execution is halted
# -----------------------------------------------------------------------------
def get_output_spreadsheet(inputname, outputname):
    """return the name of the output spreadsheet. If an output name is given, then
       it is selected; otherwise, the input name is extended with '-timetable'.
       It also verifies that the output name ends with the right suffix.

       If either the resulting file already exists, or it is not possible to
       create it, then an error is issued and execution is halted

    """

    # if an output name has not been specified
    if not outputname:
        outputname = normalize_filename(inputname, "-timetable.xlsx")

    # and, in any case, make sure the outputname ends in ".xlsx"
    outputname = normalize_filename(outputname, ".xlsx")

    # verify now whether it is possible to create a file with this name
    if os.path.exists(outputname) or \
       not os.access(os.path.dirname(outputname), os.W_OK):

        # then immediately show an error and exit
        LOGGER.error(ERROR_OUTPUT_SPREADSHEET.format(outputname))
        exit()

    # at this point return the name of the output spreadsheet
    return outputname


# -----------------------------------------------------------------------------
# return the name of a file for storing the icalendar. If an output name is
# given, then it is selected; otherwise, none is generated and this function
# returns None. It also verifies that the ical filename ends with the right
# suffix
#
# If either the resulting file already exists, or it is not possible to create
# it, then an error is issued and execution is halted
# -----------------------------------------------------------------------------
def get_output_ical(outputname):
    """return the name of a file for storing the icalendar. If an output name is
       given, then it is selected; otherwise, none is generated and this
       function returns None. It also verifies that the ical filename ends with
       the right suffix

       If either the resulting file already exists, or it is not possible to
       create it, then an error is issued and execution is halted

    """

    # only if an output name has been provided make sure it ends in the right
    # suffix and compute the absolute path
    if outputname:
        outputname = normalize_filename(outputname, ".ics")

        # verify now whether it is possible to create a file with this name
        if os.path.exists(outputname) or \
           not os.access(os.path.dirname(outputname), os.W_OK):

            # then immediately show an error and exit
            LOGGER.error(ERROR_OUTPUT_ICAL.format(outputname))
            exit()

        # at this point return the name of the output ical file
        return outputname

    # if no outputname was provided then return None ---I know, a little bit
    # redundant but I do like doing things this way. Most likely even Donald
    # Knuth recommends somewhere to be redundant ;)
    return None


# -----------------------------------------------------------------------------
# return datetime and time as strings. In case the argument is neither a
# datetime, nor a time, nor a string, an error is immediately raised
# -----------------------------------------------------------------------------
def stringize(instr):
    """return datetime and time as strings. In case the argument is neither a
       datetime, nor a time, nor a string, an error is immediately raised

    """

    # in case the argument is a datetime, return a string representing only the
    # date
    if isinstance(instr, datetime.datetime):
        return str(instr.date())

    # in case the argument is either a date or a time, return a string
    # representing it
    if isinstance(instr, (datetime.date, datetime.time)):
        return str(instr)

    # in case it is a string, return it right away
    if isinstance(instr, str):
        return instr

    # in any other case raise an error
    raise TypeError(ERROR_UNKNOWN_TYPE.format(instr))


# -----------------------------------------------------------------------------
# try to process the given instruction as a unit date constraint. In case of
# failure, a ValueError is raised; otherwise, a legal instance of a unit
# constraint using a datetime.datetime is returned
# -----------------------------------------------------------------------------
def get_uni_date_constraint(instr: str):
    """try to process the given instruction as a unit date constraint. In case of
       failure, a ValueError is raised; otherwise, a legal instance of a
       datetime.datetime is returned

    """

    # if not recognized as a date, immediately raise an error
    m = RE_UNI_DATE_CONSTRAINT.match(instr)
    if not m:
        raise ValueError(ERROR_UNI_DATE_CONSTRAINT.format(instr))

    # In case no operator is given, '=' is taken by default
    op = '=' if not m.group('operator') else m.group('operator')

    # and return a unit constraint with the processed date
    return exmconstraint.EXMUniConstraint(op,
                                          datetime.datetime(int(m.group('year')),
                                                            int(m.group('month')),
                                                            int(m.group('day'))))


# -----------------------------------------------------------------------------
# try to process the given instruction as a unit time constraint. In case of
# failure, a ValueError is raised; otherwise, a legal instance of a unit
# constraint using a datetime.time is returned
# -----------------------------------------------------------------------------
def get_uni_time_constraint(instr: str):
    """try to process the given instruction as a unit time constraint. In case of
       failure, a ValueError is raised; otherwise, a legal instance of a
       datetime.time is returned

    """

    # if not recognized as a time, immediately raise an error
    m = RE_UNI_TIME_CONSTRAINT.match(instr)
    if not m:
        raise ValueError(ERROR_UNI_TIME_CONSTRAINT.format(instr))

    # In case no operator is given, '=' is taken by default
    op = '=' if not m.group('operator') else m.group('operator')

    # also, compute the right hours taking into account the qualifier, and make
    # seconds to be zero by default. Note that when casting the seconds, the
    # heading ':' is intentionally removed
    hour = int(m.group('hour'))
    if m.group('qualifier') == 'PM' and hour < 12:
        hour += 12
    seconds = 0 if not m.group('seconds') else int(m.group('seconds')[1:])

    # and return a unit constraint with the processed time
    return exmconstraint.EXMUniConstraint(op,
                                          datetime.time(hour,
                                                        int(m.group('minutes')),
                                                        seconds))


# -----------------------------------------------------------------------------
# return a list of EXM CSP binary constraints with all records found in the
# given string. Note that variables bound by a constraint might not contain a
# sheet name. In that case, use the current sheetname
# -----------------------------------------------------------------------------
def get_biconstraint(instr: str, sheetname: str):
    """return a list of EXM CSP binary constraints with all records found in the
       given string. Note that variables bound by a constraint might not contain
       a sheet name. In that case, use the current sheetname

    """

    # if not recognized as a binary constraint
    m = RE_BICONSTRAINT.match(instr)
    if not m:
        raise ValueError(ERROR_BICONSTRAINT.format(instr))

    # In case no operator is given, '=' is taken by default
    op = '=' if not m.group('operator') else m.group('operator')

    # get the cellname this constraint refers to. Note that sheetnames might
    # be given or not
    cellname = m.group('sheet')+'.'+m.group('cell') if m.group('sheet') \
        else '$'+sheetname+'.'+m.group('cell')

    # and return the binary constraint
    return exmconstraint.EXMBiConstraint(op, cellname)


# -----------------------------------------------------------------------------
# return three lists of EXM CSP constraints with all records found in the string
# given in cellname. The lists are given in the following order: unit date, unit
# time and binary
# -----------------------------------------------------------------------------
def get_constraints(instr: str, sheetname: str, cellname: str):
    """return three lists of EXM CSP constraints with all records found in the
       string cellname. The lists are given in the following order: unit date,
       unit time and binary

    """

    # initialization ---create three different lists to return all constraints
    exm_uni_date, exm_uni_time, exm_bi = [], [], []

    # if and only if this is not an empty string
    if instr:

        # first things first, split the whole string
        for iconstraint in RE_SEP_CONSTRAINT.split(instr):

            # ignore empty constraints
            if not iconstraint.strip():
                continue

            # try first to process this as a unit date constraint
            try:
                exm_uni_date.append(get_uni_date_constraint(iconstraint))
            except ValueError:

                # next, try as a unit time constraint
                try:
                    exm_uni_time.append(get_uni_time_constraint(iconstraint))
                except ValueError:

                    # finally, try as a binary constraint
                    try:
                        exm_bi.append(get_biconstraint(iconstraint, sheetname))
                    except ValueError:

                        # at this point, this specific content could not be
                        # interpreted as a constraint
                        LOGGER.error(ERROR_CONSTRAINT.format(iconstraint, sheetname, cellname))
                        sys.exit()

    # and return all constraints found so far
    return exm_uni_date, exm_uni_time, exm_bi


# -----------------------------------------------------------------------------
# return the sheetname, column and row of any binary constraint (either date or
# time) of an EXM variable in the given pool, which is not found in it.
# Otherwise, it returns None
# -----------------------------------------------------------------------------
def get_next_indirect(poolvar: exmpoolvar.EXMPoolVar):
    """return the sheetname, column and row of any binary constraint (either date or
       time) of an EXM variable in the given pool, which is not found in it.
       Otherwise, it returns None

    """

    # for all variables in the pool
    for ivar in poolvar:

        # and for all binary date constraints of this variable
        for ikey in ivar.get_date_biconstraints().keys():

            # if this constraint refers to a variable which does not exist in
            # the pool
            if ikey not in poolvar:

                # get the location of this register
                m = re.match(RE_CELLNAME, ikey)
                if not m:
                    LOGGER.error(ERROR_SYNTAX_ERROR_REGISTER.format(ikey))

                # and return its full location
                return (m.group('sheet'), m.group('column'), int(m.group('row')))

    # at this point, all variables appearing in all binary constraints are
    # loaded into the poolvar
    return None


# -----------------------------------------------------------------------------
# return an EXM CSP variable with all records found in the given
# spreadsheet/sheetname in the cell (column, row)
# -----------------------------------------------------------------------------
def get_variable(spreadsheet: str, sheetname: str, column: str, row: int, verbose: bool):
    """return an EXM CSP variable with all records found in the given
       spreadsheet/sheetname in the cell (column, row)"""

    # create a sps reader
    master = spsreader.SpsReader(spreadsheet, sheetname)

    # for all entries in this specific spreadsheet
    for irow in master:

        # get the cell name of the key 'Asignatura' to record its location
        # within this sheet and skip it unless this is precisely the same row
        # and column required
        (exmcolumn, exmrow) = spsreader.get_columnrow(master.get_cellname('Asignatura'))
        if exmcolumn != column or exmrow != row:
            continue

        # get the date and time constraints for this record. These might have
        # been casted as datetime/time respectively but they should be
        # manipulated as ordinary strings
        try:
            exmdate = stringize(irow['Fecha'])
        except:
            LOGGER.error(ERROR_UNKNOWN_TYPE_DATE.format(irow['Fecha'],
                                                        '$' + sheetname + '.' + column + str(row)))
        try:
            exmtime = stringize(irow['Hora'])
        except:
            LOGGER.error(ERROR_UNKNOWN_TYPE_TIME.format(irow['Hora'],
                                                        '$' + sheetname + '.' + column + str(row)))

        # check both the date and time fields and retrieve all constraints found
        # there
        date_uni_date, date_uni_time, date_bi = get_constraints(exmdate,
                                                                sheetname,
                                                                column + str(row))
        time_uni_date, time_uni_time, time_bi = get_constraints(exmtime,
                                                                sheetname,
                                                                column + str(row))

        # verify that unit constraints are in place
        if date_uni_time:
            LOGGER.error(ERROR_TIME_IN_DATE.format(column + str(row), date_uni_time))
        if time_uni_date:
            LOGGER.error(ERROR_DATE_IN_TIME.format(column + str(row), time_uni_date))

        # get the setup time of this record. If none is given, use the default
        # value
        setup = int(irow['Setup']) if "Setup" in master and irow['Setup'] else DEFAULT_SETUP_TIME

        # create a new EXM CSP variable with the information of this record and
        # add it to the list with arbitrary values for the date and time
        newvar = exmvariable.EXMVariable(sheetname,
                                         irow['Asignatura'],
                                         irow['Curso'],
                                         irow['Cuatrimestre'],
                                         datetime.datetime.fromordinal(1),
                                         datetime.time(),
                                         setup,
                                         sheetname, column, row)

        # and add the unit and binary date and time constraints, if any were
        # given
        newvar.set_date_uniconstraints(date_uni_date)
        newvar.set_date_biconstraints(date_bi)
        newvar.set_time_uniconstraints(time_uni_time)
        newvar.set_time_biconstraints(time_bi)

        # and show this variable, in case verbose output was requested
        if verbose:
            LOGGER.info(INFO_NEW_INDIRECT_VAR.format(newvar))

        # and return the new variable
        return newvar

    # at this point the register required has not been found. Raise an exception
    raise ValueError(ERROR_UNKNOWN_REGISTER.format(sheetname, column + str(row), spreadsheet))


# -----------------------------------------------------------------------------
# return a list of EXM CSP variables with all records found in the given
# spreadsheet. If a combination of a grade, course and semester is given, only
# variables related to those subjects are created
# -----------------------------------------------------------------------------
def get_variables(spreadsheet: str, sheetname: str,
                  grade: str, course: int, semester: int,
                  verbose: bool):
    """return a list of EXM CSP variables with all records found in the given
       spreadsheet"""

    # create a sps reader
    master = spsreader.SpsReader(spreadsheet, sheetname)

    # and now populate a list with instances of EXM CSP variables from the
    # contents obtained from the master spreadsheet
    exmvars = []
    for irow in master:

        # get the grade, course and semester
        exmgrade, exmcourse, exmsemester = sheetname, irow['Curso'], irow['Cuatrimestre']

        # now, accept this record if and only if it matches the selection
        # criteria given by the user
        if (grade and grade != exmgrade) or \
           (course and course != exmcourse ) or \
           (semester and semester != exmsemester):
            continue

        # get the cell name of the key 'Asignatura' to record its location
        # within this sheet
        (column, row) = spsreader.get_columnrow(master.get_cellname('Asignatura'))

        # get the date and time constraints for this record. These might have
        # been casted as datetime/time respectively but they should be
        # manipulated as ordinary strings
        try:
            exmdate = stringize(irow['Fecha'])
        except:
            LOGGER.error(ERROR_UNKNOWN_TYPE_DATE.format(irow['Fecha'],
                                                        '$' + sheetname + '.' + column + str(row)))
        try:
            exmtime = stringize(irow['Hora'])
        except:
            LOGGER.error(ERROR_UNKNOWN_TYPE_TIME.format(irow['Hora'],
                                                        '$' + sheetname + '.' + column + str(row)))

        # check both the date and time fields and retrieve all constraints found
        # there
        date_uni_date, date_uni_time, date_bi = get_constraints(exmdate,
                                                                sheetname,
                                                                column + str(row))
        time_uni_date, time_uni_time, time_bi = get_constraints(exmtime,
                                                                sheetname,
                                                                column + str(row))

        # verify that unit constraints are in place
        if date_uni_time:
            LOGGER.error(ERROR_TIME_IN_DATE.format(column + str(row), date_uni_time))
        if time_uni_date:
            LOGGER.error(ERROR_DATE_IN_TIME.format(column + str(row), time_uni_date))

        # get the setup time of this record. If none is given, use the default
        # value
        setup = int(irow['Setup']) if "Setup" in master and irow['Setup'] else DEFAULT_SETUP_TIME

        # create a new EXM CSP variable with the information of this record and
        # add it to the list with arbitrary values for the date and time
        newvar = exmvariable.EXMVariable(sheetname,
                                         irow['Asignatura'],
                                         irow['Curso'],
                                         irow['Cuatrimestre'],
                                         datetime.datetime.fromordinal(1),
                                         datetime.time(),
                                         setup,
                                         sheetname, column, row)

        # and add the unit and binary date and time constraints, if any were
        # given
        newvar.set_date_uniconstraints(date_uni_date)
        newvar.set_date_biconstraints(date_bi)
        newvar.set_time_uniconstraints(time_uni_time)
        newvar.set_time_biconstraints(time_bi)

        # and show this variable, in case verbose output was requested
        if verbose:
            LOGGER.info(INFO_NEWVAR.format(newvar))

        # and add the new variable to the list of variables to return
        exmvars.append(newvar)

    # and return all the EXM CSP variables processed so far
    return exmvars


# -----------------------------------------------------------------------------
# return true if and only if the given value satisfies all unit constraints in
# the specified variable
# -----------------------------------------------------------------------------
def uni_is_compatible(variable: exmvariable.EXMVariable, value: exmvalue.EXMValue):
    """return true if and only if the given value satisfies all unit constraints in
the specified variable

    """

    # -- unit date constraints

    # in case any unit date constraints were defined over this variable
    uni_date_constraints = variable.get_date_uniconstraints()
    if len(uni_date_constraints) > 0:

        # then for all unit date constraints defined for this variable
        for ikey in uni_date_constraints.keys():
            for iconstraint in uni_date_constraints[ikey]:

                # if any constraint is not satisfied, return false
                if not {'=': uni_equal_date,
                        '!=': uni_not_equal_date,
                        '<' : uni_lt_date,
                        '<=': uni_le_date,
                        '>' : uni_gt_date,
                        '>=': uni_ge_date}[iconstraint.get_operator()](value.get_value(),
                                                                       iconstraint.get_const()):
                    return False

    # -- unit time constraints

    # in case any unit time constraints were defined over this variable
    uni_time_constraints = variable.get_time_uniconstraints()
    if len(uni_time_constraints) > 0:

        # then for all unit date constraints defined for this variable
        for ikey in uni_time_constraints.keys():
            for iconstraint in uni_time_constraints[ikey]:

                # if any constraint is not satisfied, return false
                if not {'=': uni_equal_time,
                        '!=': uni_not_equal_time,
                        '<' : uni_lt_time,
                        '<=': uni_le_time,
                        '>' : uni_gt_time,
                        '>=': uni_ge_time}[iconstraint.get_operator()](value.get_value(),
                                                                       iconstraint.get_const()):
                    return False

    # if all constraints are satisfied, return True. Note that if no constraint
    # is given then any value is compatible
    return True


# -----------------------------------------------------------------------------
# return a list of EXM CSP values with all records found in the timeslots of the
# specified spreadsheet
# -----------------------------------------------------------------------------
def get_values(spreadsheet: str):
    """return a list of EXM CSP values with all records found in the timeslots of
       the specified spreadsheet

    """

    # create a sps reader
    master = spsreader.SpsReader(spreadsheet, "Timeslots")

    # and now populate a list with instances of EXM CSP values from the contents
    # obtained from the master spreadsheet
    exmvals = []
    for irow in master:

        # all fields in this record are times but one of them 'Fecha' which is a
        # date, so just combine the date with all the given times to obtain full
        # datetimes as values
        nbslot = 1
        while 'Slot #{0}'.format(nbslot) in irow:

            # in case this particular cell is not empty, add it to the domain
            if irow['Slot #{0}'.format(nbslot)]:
                exmvals.append(exmvalue.EXMValue(irow['Fecha'],
                                                 irow['Slot #{0}'.format(nbslot)]))

            # and move to the next slot
            nbslot += 1

    # and return all values retrieved so far
    return exmvals


# -----------------------------------------------------------------------------
# CONSTRAINTS
# -----------------------------------------------------------------------------

# --unit date constraints

# -----------------------------------------------------------------------------
# Verify that the date given in first place is equal to the second date
# -----------------------------------------------------------------------------
def uni_equal_date (xi, cj):
    """Verify that the date given in first place is equal to the second date

    """

    return xi.date() == cj.date()

# -----------------------------------------------------------------------------
# Verify that the date given in first place is not equal to the second date
# -----------------------------------------------------------------------------
def uni_not_equal_date (xi, cj):
    """Verify that the date given in first place is not equal to the second date

    """

    return xi.date() != cj.date()

# -----------------------------------------------------------------------------
# Verify that the date given in first place is strictly less than the second
# date
# -----------------------------------------------------------------------------
def uni_lt_date (xi, cj):
    """Verify that the date given in first place is strictly less than the second
       date

    """

    return xi.date() < cj.date()

# -----------------------------------------------------------------------------
# Verify that the date given in first place is less or equal than the second
# date
# -----------------------------------------------------------------------------
def uni_le_date (xi, cj):
    """Verify that the date given in first place is less or equal than the second
       date

    """

    return xi.date() <= cj.date()

# -----------------------------------------------------------------------------
# Verify that the date given in first place is strictly greater than the second
# date
# -----------------------------------------------------------------------------
def uni_gt_date (xi, cj):
    """Verify that the date given in first place is strictly greater than the second
       date

    """

    return xi.date() > cj.date()


# -----------------------------------------------------------------------------
# Verify that the date given in first place is greater or equal than the second
# date
# -----------------------------------------------------------------------------
def uni_ge_date (xi, cj):
    """Verify that the date given in first place is greater or equal than the second
       date

    """

    return xi.date() >= cj.date()

# --unit time constraints

# -----------------------------------------------------------------------------
# Verify that the time given in first place is equal to the second time
# -----------------------------------------------------------------------------
def uni_equal_time (xi, cj):
    """Verify that the time given in first place is equal to the second time

    """

    return xi.time() == cj

# -----------------------------------------------------------------------------
# Verify that the time given in first place is not equal to the second time
# -----------------------------------------------------------------------------
def uni_not_equal_time (xi, cj):
    """Verify that the time given in first place is not equal to the second time

    """

    return xi.time() != cj

# -----------------------------------------------------------------------------
# Verify that the time given in first place is strictly less than the second
# time
# -----------------------------------------------------------------------------
def uni_lt_time (xi, cj):
    """Verify that the time given in first place is strictly less than the second
       time

    """

    return xi.time() < cj

# -----------------------------------------------------------------------------
# Verify that the time given in first place is less or equal than the second
# time
# -----------------------------------------------------------------------------
def uni_le_time (xi, cj):
    """Verify that the time given in first place is less or equal than the second
       time

    """

    return xi.time() <= cj

# -----------------------------------------------------------------------------
# Verify that the time given in first place is strictly greater than the second
# time
# -----------------------------------------------------------------------------
def uni_gt_time (xi, cj):
    """Verify that the time given in first place is strictly greater than the second
       time

    """

    return xi.time() > cj


# -----------------------------------------------------------------------------
# Verify that the time given in first place is greater or equal than the second
# time
# -----------------------------------------------------------------------------
def uni_ge_time (xi, cj):
    """Verify that the time given in first place is greater or equal than the second
       time

    """

    return xi.time() >= cj

# --binary constraints

# -----------------------------------------------------------------------------
# Verify that the date of the first variable is equal to the date of the second
# variable
# -----------------------------------------------------------------------------
def bi_equal_date (xi, xj):
    """Verify that the date of the first variable is equal to the date of the second
       variable

    """

    return xi.get_date().date() == xj.get_date().date()

# -----------------------------------------------------------------------------
# Verify that the date of the first variable is not equal to the date of the
# second variable
# -----------------------------------------------------------------------------
def bi_not_equal_date (xi, xj):
    """Verify that the date of the first variable is not equal to the date of the
       second variable

    """

    return xi.get_date().date() != xj.get_date().date()

# -----------------------------------------------------------------------------
# Verify that the date of the first variable is strictly less than the date of
# the second variable
# -----------------------------------------------------------------------------
def bi_lt_date (xi, xj):
    """Verify that the date of the first variable is strictly less than the date of
       the second variable

    """

    return xi.get_date().date() < xj.get_date().date()

# -----------------------------------------------------------------------------
# Verify that the date of the first variable is less or equal than the date of
# the second variable
# -----------------------------------------------------------------------------
def bi_le_date (xi, xj):
    """Verify that the date of the first variable is less or equal than the date of
       the second variable

    """

    return xi.get_date().date() <= xj.get_date().date()

# -----------------------------------------------------------------------------
# Verify that the date of the first variable is strictly greater than the date
# of the second variable
# -----------------------------------------------------------------------------
def bi_gt_date (xi, xj):
    """Verify that the date of the first variable is strictly greater than the date of
       the second variable

    """

    return xi.get_date().date() > xj.get_date().date()

# -----------------------------------------------------------------------------
# Verify that the date of the first variable is greater or equal than the date
# of the second variable
# -----------------------------------------------------------------------------
def bi_ge_date (xi, xj):
    """Verify that the date of the first variable is greater or equal than the date of
       the second variable

    """

    return xi.get_date().date() >= xj.get_date().date()

# -----------------------------------------------------------------------------
# Verify that the time of the first variable is equal to the time of the second
# variable
# -----------------------------------------------------------------------------
def bi_equal_time (xi, xj):
    """Verify that the time of the first variable is equal to the time of the second
       variable

    """

    return xi.get_time() == xj.get_time()

# -----------------------------------------------------------------------------
# Verify that the time of the first variable is not equal to the time of the
# second variable
# -----------------------------------------------------------------------------
def bi_not_equal_time (xi, xj):
    """Verify that the time of the first variable is not equal to the time of the
       second variable

    """

    return xi.get_time() != xj.get_time()

# -----------------------------------------------------------------------------
# Verify that the time of the first variable is strictly less than the time of
# the second variable
# -----------------------------------------------------------------------------
def bi_lt_time (xi, xj):
    """Verify that the time of the first variable is strictly less than the time of
       the second variable

    """

    return xi.get_time() < xj.get_time()

# -----------------------------------------------------------------------------
# Verify that the time of the first variable is less or equal than the time of
# the second variable
# -----------------------------------------------------------------------------
def bi_le_time (xi, xj):
    """Verify that the time of the first variable is less or equal than the time of
       the second variable

    """

    return xi.get_time() <= xj.get_time()

# -----------------------------------------------------------------------------
# Verify that the time of the first variable is strictly greater than the time
# of the second variable
# -----------------------------------------------------------------------------
def bi_gt_time (xi, xj):
    """Verify that the time of the first variable is strictly greater than the time of
       the second variable

    """

    return xi.get_time() > xj.get_time()

# -----------------------------------------------------------------------------
# Verify that the time of the first variable is greater or equal than the time
# of the second variable
# -----------------------------------------------------------------------------
def bi_ge_time (xi, xj):
    """Verify that the time of the first variable is greater or equal than the time of
       the second variable

    """

    return xi.get_time() >= xj.get_time()


# -----------------------------------------------------------------------------
# Verify that the time delta between two exams is at least the setup time of the
# latest event
# -----------------------------------------------------------------------------
def bi_difftime (xi, xj):
    """Verify that the time delta between two exams is at least the setup time of
       the latest event"""

    if xi.get_value() > xj.get_value():
        c = xi.get_value() - xj.get_value()
        setup = xi.get_setup()
    else:
        c = xj.get_value() - xi.get_value()
        setup = xj.get_setup()

    # and now verify that the time detal is at least the setup time of the
    # latest value --which is measured in hours
    return c.total_seconds()/3600 >= setup


# -----------------------------------------------------------------------------
# main entry point
# -----------------------------------------------------------------------------
def main ():
    """main entry point"""

    # --initialization

    # invoke the parser and parse all commands
    params = exmarg.EXMArg().parse()

    # compute the name of the output spreadsheet
    output = get_output_spreadsheet(params.master, params.output)

    # and also the name of the icalendar in case any was requested
    icalname = get_output_ical(params.ical)

    # get the names of all sheets in this spreadsheet
    master_book = spsreader.SpsBook(params.master)

    # for all grades in this spreadsheet (i.e., for all sheetnames but
    # "Timeslots")
    poolvar = exmpoolvar.EXMPoolVar()
    for isheet in master_book.get_sheetnames():

        # skip the sheet of timeslots as it is solely used for computing the
        # domain
        if isheet == "Timeslots":
            continue

        # load all the information of this specific grade and add it to the pool
        # var
        nbvars = len(poolvar)
        poolvar += get_variables (params.master, isheet, params.grade,
                                  params.course, params.semester, params.verbose or params.debug)
        if len(poolvar) == nbvars:
            LOGGER.warning(WARNING_SKIP.format(isheet))
        else:
            LOGGER.info(INFO_VARS_PROCESSED.format(isheet,
                                                   len(poolvar)))

    # now, make sure that all indirections are also loaded into the poolvar if
    # and only if the user has requested it
    nbvars = len(poolvar)
    if params.load_indirects:
        indirect = get_next_indirect(poolvar)
        while indirect is not None:

            # then add it to the pool of variables
            poolvar += [get_variable(params.master,
                                     indirect[0], indirect[1], indirect[2],
                                     params.verbose or params.debug)]

            # and check the poolvar again
            indirect = get_next_indirect(poolvar)

    if len(poolvar) != nbvars:
        LOGGER.info(INFO_INDIRECT_VARS_PROCESSED.format(len(poolvar)-nbvars,
                                                        len(poolvar)))
    else:
        LOGGER.info(INFO_NO_INDIRECT_VARS_PROCESSED)


    # create a brand new CSP task
    task = constraint.Problem()

    # create the variables and domains: X and D. For this consider first all the
    # different values that can be used for any variable, and refine them later
    # considering the user preferences
    domain = get_values(params.master)
    for ivariable in poolvar:

        # process all feasible values and accept only those that are compatible
        # with the unit and binary date and time constraints specified in this
        # variable
        idomain = []
        for ivalue in domain:

            # if and only if this value is compatible with all unit and binary
            # date and time constraints specified for this variable, accept it
            if uni_is_compatible(ivariable, ivalue):

                # and add this value to the domain of this variable after
                # setting its setup time
                newval = copy.deepcopy(ivalue)
                newval.set_setup(ivariable.get_setup())
                idomain.append(newval)

        # in case this domain is empty something terrible happened and execution
        # must halt immediately. A likely reason is that the use set a date and
        # time which are recognized as legal timeslots. Next we only show an
        # error and the constraint lib will halt execution immediately. In the
        # lib we trust! :)
        if not idomain:
            LOGGER.error(ERROR_EMPTY_DOMAIN.format(ivariable))

        # in case debug output was requested, show the number of values in the
        # domain of each variable
        if params.debug:
            LOGGER.debug(DEBUG_DOMAIN_LENGTH.format(ivariable.get_cellname(),
                                                    ivariable.get_name(),
                                                    len(idomain)))
        task.addVariable(ivariable, idomain)

    LOGGER.info(INFO_VARS_LENGTH.format(len(domain)))

    # create the constraints: R. For this, all pairs of variables are initially
    # considered
    nbconstraints = 0
    for ivariable in poolvar._vars:
        for jvariable in poolvar._vars:

            # no variable should constraint itself, so get the shit out of
            # my face if that's the case!
            if ivariable == jvariable:
                continue

            # the first constraint is that the time delta between two
            # successive exams of the same course should be at least 24
            # hours
            if ivariable.get_grade() == jvariable.get_grade() and \
               ivariable.get_course() == jvariable.get_course():
                task.addConstraint(bi_difftime, [ivariable, jvariable])
                nbconstraints += 1

            # --date constraints

            # if the j-th variable is found among the date constraints of
            # the i-th variable then apply it
            if jvariable.get_cellname() in ivariable.get_date_biconstraints():

                # thus, apply all date constraints found in the i-th EXM CSP
                # variable
                for iconstraint in ivariable.get_date_biconstraints()[jvariable.get_cellname()]:

                    task.addConstraint({'=': bi_equal_date,
                                        '!=': bi_not_equal_date,
                                        '<' : bi_lt_date,
                                        '<=': bi_le_date,
                                        '>' : bi_gt_date,
                                        '>=': bi_ge_date}[iconstraint.get_operator()],
                                       [ivariable, jvariable])
                    nbconstraints += 1

            # --time constraints

            # if the j-th variable is found among the time constraints of the
            # i-th variable then apply it
            if jvariable.get_cellname() in ivariable.get_time_biconstraints():

                # thus, apply all time constraints found in the i-th EXM CSP
                # variable
                for iconstraint in ivariable.get_time_biconstraints()[jvariable.get_cellname()]:

                    task.addConstraint({'=': bi_equal_time,
                                        '!=': bi_not_equal_time,
                                        '<' : bi_lt_time,
                                        '<=': bi_le_time,
                                        '>' : bi_gt_time,
                                        '>=': bi_ge_time}[iconstraint.get_operator()],
                                       [ivariable, jvariable])
                    nbconstraints += 1

    LOGGER.info(INFO_CONSTRAINTS_LENGTH.format(nbconstraints))

    # Solve the CSP task
    solution = task.getSolution()
    if solution is None:
        LOGGER.error(ERROR_SOLUTION_NOT_FOUND)
    else:
        LOGGER.info(INFO_SOLUTION_FOUND)

        # set now the value of each variable
        for ivar in solution:
            ivar.set_date(solution[ivar].get_value())
            ivar.set_time(solution[ivar].get_value().time())

        # show the solution found on the output terminal
        for ivar in solution:
            LOGGER.warning('{0: <130}'.format(ivar))

            if (params.verbose or params.debug) and len(ivar.get_date_uniconstraints()) > 0:
                LOGGER.info(ivar.str_date_uniconstraints())
            if (params.verbose or params.debug) and len(ivar.get_time_uniconstraints()) > 0:
                LOGGER.info(ivar.str_time_uniconstraints())
            if (params.verbose or params.debug) and len(ivar.get_date_biconstraints()) > 0:
                LOGGER.info(ivar.str_date_biconstraints())
            if (params.verbose or params.debug) and len(ivar.get_time_biconstraints()) > 0:
                LOGGER.info(ivar.str_time_biconstraints())

        # and create an output spreadsheet to show the solution found
        poolvar.write_spreadsheet(output)

        # in case an ical file was given, then show the solution in icalendar format
        if icalname:
            poolvar.write_icalendar(icalname)


# main
# -----------------------------------------------------------------------------
if __name__ == '__main__':

    main()

# Local Variables:
# mode:python
# fill-column:80
# End:
