#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# EXMPoolVar.py
# Description: Definition of a pool of EXM CSP variables
# -----------------------------------------------------------------------------
#
# Started on <sáb 06-02-2021 19:13:47.468261963 (1612635227)>
# Carlos Linares López <carlos.linares@uc3m.es>
#

"""
Definition of a pool of EXM CSP variables
"""

# imports
# -----------------------------------------------------------------------------
from collections import defaultdict
from operator import itemgetter

import datetime

import icalendar    # icalendar ics files
import pytz         # python timzezones

if __package__ is None or __package__ == '':
    import spswriter
else:
    from . import spswriter

# -----------------------------------------------------------------------------
# wrapper function used to sort variables by multiple criteria.
#
# vars is a list of lists, each containing the following information:
#    [name, course, semester, date, time]
#
# The specifications consist of an interable of pairs (index, reverse), where
# index is the position of each field that has to be used for sorting data, e.g.
# [(1, False), (2, False), (3, False), (4, False)] sorts all entries by their
# course, next by the semester, then by the date and tie-breaks are broken in
# favour of minor times. If True is given in the second entry of each pair then
# the order is reversed for that specific key
# -----------------------------------------------------------------------------
def multisort(xvars, specs):
    """wrapper function used to sort variables by multiple criteria

       vars is a list of lists, each containing the following information:
          [name, course, semester, date, time]

       The specifications consist of an interable of pairs (index, reverse),
       where index is the position of each field that has to be used for sorting
       data, e.g. [(1, False), (2, False), (3, False), (4, False)] sorts all
       entries by their course, next by the semester, then by the date and
       tie-breaks are broken in favour of minor times. If True is given in the
       second entry of each pair then the order is reversed for that specific
       key

    """

    # sort all entries according to the given specification
    for index, reverse in reversed(specs):
        xvars.sort(key=itemgetter(index), reverse=reverse)

    # return the sorted data
    return xvars

# -----------------------------------------------------------------------------
# EXMPoolVar
#
# An EXM pool is just a container of EXM CSP variables
# -----------------------------------------------------------------------------
class EXMPoolVar():
    """An EXM pool is just a container of EXM CSP variables

    """

    def __init__(self):
        """Initially, a pool is always empty

        """

        # initialize an empty list to record all variables to be added in the
        # future
        self._vars = []

        # initialize the counter used for iterating all members of this instance
        self._idx = 0

    def __contains__(self, other: str):
        """Return true if and only if the given sheet name is found in this pool of EXM
           CSP Variables, and false otherwise

        """

        return other in self._vars

    def __len__(self):
        """return the number of sheet names registered in this pool"""

        return len(self._vars)

    def __iadd__(self, value: list):
        """It adds a list of EXM CSP Variables to this container

        """

        self._vars += value
        return self

    def __iter__(self):
        """return the base case for iterators"""

        return self

    def __next__(self):
        """return the next member of this instance"""

        # if we did not reach the limit
        if self._idx < len(self._vars):

            # return the current item
            item = self._vars[self._idx]
            self._idx += 1
            return item

        # restart the iterator from the very beginning
        self._idx = 0

        # and stop the current iteration
        raise StopIteration()


    def write_spreadsheet(self, spsfilename):
        """Write the value of all variables stored in this poolvar in the specified
           spreadsheet

           Each variable is written in a different spreadsheet. The name of the
           spreadsheet to write data is obtained from the variable name

        """

        # first things first, group all exm variables in this poolvar by the
        # grade they belong to
        sheets = defaultdict(list)
        for ivar in self._vars:

            # add this variable to a sheet with the name of the grade it belongs to
            sheets[ivar.get_grade()].append(ivar)

        # next, create a spreadsheet
        output = spswriter.SpsWriter(spsfilename)

        # and write the information of all EXM variables each one in a different
        # spreadsheet according to the grade they belong to
        for igrade in sheets:

            # create this spreadsheet
            output.add_worksheet(igrade)

            # set the headers. The foreground is given in light yellow and the
            # backgroun in dark blue
            output.set_headers(["Asignatura", "Curso", "Cuatrimestre", "Fecha", "Hora"],
                               {'font_color':'#FFF5CD', 'bg_color': '#2A6096',
                                'bold': True, 'align':'center'})

            # enable autofilters in the last four columns
            output.set_autofilters(["Curso", "Hora"])

            # create different groups for each combination of course and
            # semester and colour them differently
            output.set_group(["Curso", "Cuatrimestre"])
            output.set_alternating_bg(['#DEE6EF', '#F6F9D4'])

            # and now collect all data to show
            data = []
            for ivar in sheets[igrade]:

                # add a new line of data with the information of this specific
                # EXM variable
                data.append([ivar.get_name(), ivar.get_course(), ivar.get_semester(),
                             str(ivar.get_date().date()), str(ivar.get_time())])

            # before adding data, sort it
            multisort(data, [(1, False), (2, False), (3, False), (4, False)])
            output.add_data(data)

        # and close the output spreadsheet
        output.close()


    def write_icalendar(self, icalname):
        """Write the value of all variables stored in this poolvar in the specified
           icalendar

           Each variable is written as a different event whose summary is a
           combination of the grade and subject. Other information is shown in
           the DESCRIPTION field

        """

        # first things first, group all exm variables in this poolvar by the
        # grade they belong to
        sheets = defaultdict(list)
        for ivar in self._vars:

            # add this variable to a sheet with the name of the grade it belongs to
            sheets[ivar.get_grade()].append(ivar)

        # create a new calendar
        cal = icalendar.Calendar()
        cal.add('prodid', '-//EXM Calendar//Python EXM//SP')
        cal.add('version', '2.0')

        # set the timezone
        tz = pytz.timezone("Europe/Madrid")

        # and now create an event in the calendar for each variable in the
        # poolvar
        for igrade in sheets:
            for ivar in sheets[igrade]:

                # add the information of this variable as a new event
                event = icalendar.Event()
                event.add('summary', igrade + '.' + ivar.get_name())
                event.add('description',
                          'Asignatura: {0}\nCurso: {1}\nCuatrimestre: {2}'.format(ivar.get_name(),
                                                                                  ivar.get_course(),
                                                                                  ivar.get_semester()))

                # make these events to last one hour by default
                event.add('dtstart', tz.localize(ivar.get_date()))
                event.add('dtend', tz.localize(ivar.get_date() + datetime.timedelta(seconds=3600)))
                event.add('dtstamp', datetime.datetime.now())

                # and add it to the calendar
                cal.add_component(event)

        # and now write the calendar to the given file
        with open(icalname, 'w') as stream:

            stream.write(cal.to_ical().decode("utf-8"))

# Local Variables:
# mode:python
# fill-column:80
# End:
