#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# spswriter.py
# Description: A writer of xlsx spreadsheets
# -----------------------------------------------------------------------------
#
# Started on <vie 19-02-2021 21:15:10.224342617 (1613765710)>
# Carlos Linares López <carlos.linares@uc3m.es>
#

"""
A writer of xlsx spreadsheets
"""

# imports
# -----------------------------------------------------------------------------
import os

import xlsxwriter

# globals
# -----------------------------------------------------------------------------
ERROR_WRONG_PATH = "The path '{0}' is not reachable"
ERROR_LIST_EXPECTED = "rows to be written should be given as lists"
ERROR_WRONG_DATA = "data to be written can be delivered only as a list of lists"
ERROR_NO_WORKSHEET = "no worksheet has been added"
ERROR_WRONG_HEADER = "The header {0} has not been registered"
ERROR_INVALID_AUTOFILTER_RANGE = "Two columns have to be given to define a range of columns to 'autofilter'"

# to_list
#
# formats data to be written in a spreadsheet
#
# data should be given as a list of lists, each item within a single list might
# be either a scalar or a tuple. In case it is a tuple, its items are stripped
# off and inserted in the list
#
# the result consists of another list of lists where all elements are scalars
# -----------------------------------------------------------------------------
def to_list(data):
    """ formats data to be written in a spreadsheet

        data should be given as a list of lists, each item within a single list might
        be either a scalar or a tuple. In case it is a tuple, its items are stripped
        off and inserted in the list

        the result consists of another list of lists where all elements are scalars

    """

    # -- initialization
    result = []

    # ensure that the overall structure is given as a list
    if not isinstance(data, list):
        raise TypeError(ERROR_WRONG_DATA)

    # for each list in data
    for iline in data:

        # ensure also each line is given as another list
        if not isinstance(iline, list):
            raise TypeError(ERROR_WRONG_DATA)

        # for each item in this list
        iresult = []
        for item in iline:

            # if this item is a tuple, then strip its elements
            if isinstance(item, tuple):
                iresult += list(item)

            # otherwise copy it as is
            else:
                iresult.append(item)

        # and add this line to the output
        result.append(iresult)

    # and return the result
    return result


# -----------------------------------------------------------------------------
# SpsWriter
#
# Writes data into a xlsx spreadsheet
#
# This class implements a generic writer to display data in xlsx spreadsheets in
# as many spreadsheets as needed
#
# It accepts the definition of headers with an arbitrary selection of formatting
# properties. Data can be also displayed with properties explicitly given. If
# none is given, then a definition of alternating colors can be provided to show
# different groups in different background colors. Two rows are said to belong
# to the same group if and only if:
#
#   1. They are consecutive
#   2. The contents of one column whose header has been marked as suppressable
#   are the same in both rows
#
# If neither formatting properties nor alternating colors are given, then data
# is displayed with the default format
# -----------------------------------------------------------------------------
class SpsWriter():
    """Writes data into a xlsx spreadsheet

       This class implements a generic writer to display data in xlsx
       spreadsheets with as many worksheets as needed

       It accepts the definition of headers with an arbitrary selection of
       formatting properties. Data can be also displayed with properties
       explicitly given. If none is given, then a definition of alternating
       colors can be provided to show different groups in different background
       colors. Two rows are said to belong to the same group if and only if:

          1. They are consecutive
          2. The contents of all columns whose header has been marked as part of
             the group are equal to the contents of the preceding line

       If neither formatting properties nor alternating colors are given, then
       data is displayed with the default format

    """

    def __init__(self, spsfilename):
        """the only information required to create a generic writer is the filename,
           which can be given with a path either relative or absolute

           Other than that this constructor only initializes some data members.
           To further configure the writer it is necessary to use the services
           via the set_* methods

        """

        # copy the attributes only in case this is a valid file
        path = os.path.dirname(os.path.realpath(spsfilename))
        if os.access(path, os.W_OK):
            self._spsfilename = spsfilename

        # otherwise raise an exception
        else:
            raise FileNotFoundError(ERROR_WRONG_PATH.format(path))

        # create an xlsx workbook
        self._sheet = xlsxwriter.Workbook(self._spsfilename)

        # No worksheet is selected by default. To create a worksheet it is
        # mandatory to add one with add_worksheet
        self._worksheet = None

        # headers contain the name of all columns to be shown in the
        # spreadsheet. These are set with set_headers which also accepts
        # formatting properties
        self._headers = []

        # by default the autofilter is disabled. If enabled it should be defined
        # given the names of two columns via set_autofilters which create a
        # range over which autofilters are defined
        self._autofilters = []

        # additionally, it is possible to define groups. Two rows belong to the
        # same group if and only if: 1) they are consecutive; 2) they both have
        # the same value in the headers stored in the attribute _group. If
        # _group is empty, then all rows are independent to each other, which is
        # the default behaviour. Groups can be defined via set_group
        self._group = []

        # if suppress_headers is given, then all rows in the same group remove
        # their contents but the first one. This is done for the sake of clarity
        # when presenting data. By default, this behaviour is disabled
        self._suppress_headers = False

        # Groups are coloured with different (alternating) colors.
        # _alternating_bg contains a list of colors to use. When writing data,
        # colors are taken in sequence. An arbitrary number of them can be used.
        # Alternating colors are defined via set_alternating_bg
        self._alternating_bg = []
        self._idx_bg = 0

        # the contents of the last row are stored in a dedicated attribute to
        # enable the computation of groups
        self._last_row = None

        # the data to be shown on the spreadsheet is oriented vertically, and
        # thus a counter of the next available line is maintained internally
        self._lineno = 0


    def _same_group(self, line):
        """returns whether the data in line starts a new group or not:

           1. If there is no line to compare with then this line starts a new
              group by definition

           2. If _group is non-empty and the contents of all columns in the
              headers given in _group are equal to those in the preceding line,
              then the row in line belongs to the same group than the previous
              one

           3. If either _group is empty or there is a column in 'line' whose
              content is different than that of the previous line for a given
              header in _group, then 'line' is said to start a new group

        """

        # first and foremost, if there is no row to compare with or if the
        # definition of groups is empty then this one starts a new group by
        # definition
        if not self._last_row or not self._group:
            return False

        # examine all headers marked as defining the same group. Note that
        # _group stores the indexes instead of the header names
        for iheader in self._group:

            # if this header shows different values in this line and the
            # preceding one
            if self._last_row[iheader] != line[iheader]:
                return False

        # at this point, all headers defined in the group have been traversed
        # and no difference has been found
        return True


    def _enable_autofilters(self):
        """enables the autofilter in all those columns that actually requested it"""

        # of course, if no autofilters have been requested, then exit
        # immediately
        if self._autofilters:

            if not self._worksheet:
                raise LookupError(ERROR_NO_WORKSHEET)

            self._worksheet.autofilter(0, self._autofilters[0],
                                       self._lineno, self._autofilters[1])


    def _write_line(self, data, props=None, colno=0):
        """write a line in the spreadsheet starting from colno with the format specified
           in props

           data should be given as a plain list. Items in the list are written
           in the next empty line of the spreadsheet in successive columns
           starting from the given column number in colno

           The format can be optionally specified with a dictionary of props
           ---see XlsxWriter documentation. If none is given the format is then
           automatically computed from the definition of groups:

           1. If two rows belong to the same group then:

              1.a. The same color is used. If no alternating background colors
                   were given, then the default one is used

              1.b. If '_suppress_headers' is enabled, then rows in the same
                   group remove their contents, but the first row in the same group

           2. If the next row starts a new group then the next color in the list
              of alternating background colors is used

        """

        if not self._worksheet:
            raise LookupError(ERROR_NO_WORKSHEET)

        if not isinstance(data, list):
            raise ValueError(ERROR_LIST_EXPECTED)

        # Importantly, do this row and the previous one belong to the same
        # group?
        same_group = self._same_group(data)

        # Determine the contents to show in this row. In general, all data given
        # in data should be displayed unless suppress_headers has been enabled
        # and this line and the previous one are proven to belong to the same
        # group. In passing, compute the contents of all cells to be shown in
        # this row
        line = data
        if same_group:

            if self._suppress_headers:

                # then suppress the contents of all headers in the group
                for iheader in self._group:
                    line[iheader] = None

        # now, determine the format to use. If a format was given, then use it.
        if props:
            cell_format = self._sheet.add_format(props)

        # if not, and no alternatibng background colors were given, then use the
        # default format
        elif not self._alternating_bg:
            cell_format = None

        # If no format was explicitly given but alternating colors were defined,
        # then determine which one to use
        else:

            # if this line starts a new group then use the next alternating
            # background color
            if not same_group:
                self._idx_bg = (1+self._idx_bg) % len(self._alternating_bg)
            cell_format = self._sheet.add_format({'bg_color': self._alternating_bg[self._idx_bg]})

        # and finally display the contents of this row with the format chosen
        # above
        for item in line:
            self._worksheet.write(self._lineno, colno, item, cell_format)
            colno += 1

        # and update the information of the last line written
        self._last_row = data

        # as a result of writing one line of data in the spreadsheet the next
        # available line is incremented by one
        self._lineno += 1


    def add_data(self, data, colno=0):
        """adds the given data to the spreadsheet from the given column number

           data should consist of a list of lists, each list to be displayed in
           a different line, and all lines starting in the specified column
           number

           Elements of a single list might be either scalar values or tuples. In
           the latter case, its items are stripped off the tuple and inserted
           into the list spanning for as many columns as items there are in the
           tuple

        """

        # first process data to make sure that it consists of a list of lists
        data = to_list(data)

        # write each list in data in a different line in the spreadsheet
        for iline in data:
            self._write_line(iline, colno)

        # finally, set the autofilters in those columns that requested it
        self._enable_autofilters()


    def add_worksheet(self, name):
        """add a new worksheet with the given name and use it to write data"""

        self._worksheet = self._sheet.add_worksheet(name)

        # when adding a worksheet make sure that it is properly initialized
        self._headers = []
        self._group = []
        self._lineno = 0
        self._last_row = None
        self._idx_bg = 0
        self._autofilters = []
        self._alternating_bg = []


    def close(self):
        """closes the worksheet effectively making sure that all data is written down"""

        self._sheet.close()


    def get_header_index(self, header):
        """"return the index (zero-based) of the specified header. In case the header
            does not exist, it automatically raises an exception

        """

        idx = 0

        # for all headers registered with set_headers
        while idx < len(self._headers):

            # if this is the requested header, return its position
            if self._headers[idx] == header:
                return idx

            # otherwise, move forward
            idx += 1

        # at this point, the header has not been found, raise an exception
        raise LookupError(ERROR_WRONG_HEADER.format(header))


    def set_alternating_bg(self, bg_colors):
        """set the alternating colours used to colour each row. 'bg_colors' has to be
           given as a list of colors in the format '#RRGGBB'

           If two rows belong to the same group the color of the preceding line
           is used again. Otherwise, the next color in bg_colors is used

        """

        self._alternating_bg = bg_colors

        # when initializing the alternating background colors, also initialize
        # the counter
        self._idx_bg = 0


    def set_autofilters(self, headers):
        """enables the autofilter in the range defined between the given columns. The
           headers should consist of a list with just two column names
        """

        if len(headers) != 2:
            raise ValueError(ERROR_INVALID_AUTOFILTER_RANGE)

        self._autofilters = [self.get_header_index(iheader) for iheader in headers]


    def set_group(self, headers):
        """defines a group as a collection of headers. *Consecutive* rows with the same
           value in the given columns are considered to belong to the same group.

           Groups are useful for determining whether to remove contents or for
           determining the colors to use

        """

        self._group = [self.get_header_index(iheader) for iheader in headers]


    def set_headers(self, value, props=None):
        """set the headers of the spreadsheet. The headers should be given as a list
           which will then be written in the first row of the spreadsheet using
           the format given in props which should be given as a dictionary of
           properties ---see XlsxWriter documentation

        """

        self._headers = value

        # and write the headers to the spreadsheet, one in a different column.
        # Note that the type of each header is preserved in the spreadsheet
        self._write_line(self._headers, props)


    def set_suppress_headers(self, value=True):
        """"if enabled, then rows in the same group remove their contents for the sake
            of clarity

        """

        self._suppress_headers = value

# Local Variables:
# mode:python
# fill-column:80
# End:
