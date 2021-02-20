#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# exmconstraints.py
# Description: Definition of a container of binary constraints a CSP EXM
# Variable is bound to
# -----------------------------------------------------------------------------
#
# Started on <dom 07-02-2021 15:14:09.203251863 (1612707249)>
# Carlos Linares López <carlos.linares@uc3m.es>
#

"""Definition of a container of binary constraints a CSP EXM Variable is bound
to

"""

# imports
# -----------------------------------------------------------------------------
from collections import defaultdict

# -----------------------------------------------------------------------------
# EXMConstraints
#
# A set of binary constraints consists just of a dictionary of constraints
# indexed by the variable they are bound to
# -----------------------------------------------------------------------------
class EXMConstraints():
    """A set of binary constraints consists just of a dictionary of constraints
       indexed by the variable they are bound to

    """

    def __init__(self):
        """Initially, a set of constraints is empty

        """

        # initialize a dictionary to record all variables to be added in the
        # future. Note that EXM CSP variables are indexed by their *full*
        # location in the master spreadsheet, e.g., "$GII.B21"
        self._constraints = defaultdict(list)

    def __contains__(self, other: str):
        """Return true if and only if there is a binary constraint related to the EXM
           CSP variable whose index is given in other, and false otherwise

        """

        return other in self._constraints.keys()

    def __getitem__(self, key: str):
        """Called to implement evaluation of self[key]

           Return the specific binary constraints related to the EXM CSP variable
           with the given key

        """

        return self._constraints[key]

    def __len__(self):
        """Return the number of binary constraints of this set"""

        return len(self._constraints)

    def __setitem__(self, key:str, value: list):
        """Called to implement assignment to self[key]

           It adds the constraints given in value to this set and index it by
           the given key which is the location in the master spreadsheet where
           the EXM CSP variable is defined.

           Note that the same EXM CSP variable might be bound to an arbitrary
           number of binary constraints

        """

        # in case the key currently exists
        if key in self._constraints:
            self._constraints[key] += value

        else:

            # otherwise, just associate the given constraint to this key
            self._constraints[key] = value

        return self

    def __str__(self):
        """Provides a human readable version of this instance"""

        output = ''
        for ikey in self._constraints:
            output += '[{0}]: '.format(ikey)
            for iconstraint in self._constraints[ikey]:
                output += '{0} '.format(iconstraint)
            output += '\n'
        return output

    def keys(self):
        """Return a list with all keys in this instance"""

        return self._constraints.keys()

# Local Variables:
# mode:python
# fill-column:80
# End:
