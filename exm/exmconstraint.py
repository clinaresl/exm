#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# exmconstraint.py
# Description: Definition of EXM CSP constraints
# -----------------------------------------------------------------------------
#
# Started on <dom 07-02-2021 15:04:29.302791668 (1612706669)>
# Carlos Linares López <carlos.linares@uc3m.es>
#

"""
Definition of EXM CSP constraints
"""

# imports
# -----------------------------------------------------------------------------

# globals
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# EXMUniConstraint
#
# An EXM unit constraint is a constraint bound to a constant value. As
# constraints are stored within an EXM CSP variable, the constraint itself only
# contains a reference to the constant term involved
#
# These are not true CSP variables as they do not store all values
# simultaneously legal, but just the user specification of a constraint
# -----------------------------------------------------------------------------
class EXMUniConstraint():
    """An EXM unitary constraint is a constraint bound to a constant value. As
       constraints are stored within an EXM CSP variable, the constraint itself
       only contains a reference to the constant term involved

       These are not true CSP variables as they do not store all values
       simultaneously legal, but just the user specification of a constraint

    """

    def __init__(self, operator: str, exmconst):
        """A unit constraint relates an EXM CSP variable to a constant value with an
           operator

           Within the context of the definition of these constraints, operators
           are arbitrary strings whose interpretation corresponds to someone
           else. Some goes to the type of the constant: typical types for the
           constant are dates and times

        """

        # copy the attributes
        (self._operator, self._const) = (operator, exmconst)

    def __eq__(self, other: str):
        """Return true if and only if this instance and other are the same and false
           otherwise"""

        return self._operator == other.get_operator() and \
            self._const == other.get_const()

    def __format__(self, format_spec):
        """Evaluates format string literals"""

        return "{0:{f}}".format(self.__str__(), f=format_spec)

    def __str__(self):
        """Provides a human readable version of the contents of this instance"""

        return "{0} {1}".format(self._operator, self._const)

    def get_operator(self):
        """Return the operator of this unit constraint"""

        return self._operator

    def get_const(self):
        """Return the constant term this unit constraint is bound to"""

        return self._const


# -----------------------------------------------------------------------------
# EXMBiConstraint
#
# An EXM binary constraint is a constraint arity two that involves two
# variables. As constraints are stored within an EXM CSP variable, the
# constraint itself only contains a reference to the other EXM CSP variable
# involved.
#
# These are not true CSP variables as they do not store all values
# simultaneously legal, but just the user specification of a constraint
# -----------------------------------------------------------------------------
class EXMBiConstraint():
    """An EXM binary constraint is a constraint arity two that involves two
       variables. As constraints are stored within an EXM CSP variable, the
       constraint itself only contains a reference to the other EXM CSP variable
       involved


       These are not true CSP variables as they do not store all values
       simultaneously legal, but just the user specification of a constraint

    """

    def __init__(self, operator: str, exmvar: str):
        """A binary constraint relates an EXM CSP variable with another one (exmvar)
           which is *fully* identified only by the cellname where it is defined,
           e.g., "$GII.B21"

           Within the context of the definition of these constraints, operators
           are arbitrary strings whose interpretation corresponds to someone else

        """

        # copy the attributes
        (self._operator, self._var) = (operator, exmvar)

    def __eq__(self, other: str):
        """Return true if and only if this instance and other are the same and false
           otherwise"""

        return self._var == other.get_var()

    def __format__(self, format_spec):
        """Evaluates format string literals"""

        return "{0:{f}}".format(self.__str__(), f=format_spec)

    def __str__(self):
        """Provides a human readable version of the contents of this instance"""

        return "{0} {1}".format(self._operator, self._var)

    def get_operator(self):
        """Return the operator of this binary constraint"""

        return self._operator

    def get_var(self):
        """Return the variable this binary constraint is bound to"""

        return self._var


# Local Variables:
# mode:python
# fill-column:80
# End:
