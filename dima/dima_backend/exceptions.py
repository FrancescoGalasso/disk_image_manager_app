# -*- coding: utf-8 -*-

"""
dima_backend.exceptions
~~~~~~~~~~~~~~~~~~~
This module contains the set of Dima Backend exceptions.
"""


class DimaBaseException(Exception):
    """There was an ambiguous exception that occurred while handling your
    request.
    """

    # def __init__(self,*args,**kwargs):
    #     Exception.__init__(self,*args,**kwargs)
    pass


class MissingSourcePath(DimaBaseException, ValueError):
    """The source path is missing."""


class MissingDestinationsPath(DimaBaseException, ValueError):
    """The destinations path is missing."""


class TooManySourcePath(DimaBaseException):
    """ Too many source path are passed"""

class TooManyDestinationsPath(DimaBaseException):
    """ Too many destinations path are passed"""


class EmptyArguments(DimaBaseException):
    """ Empty source and destionations arguments are passed"""


# Warnings


class DimaWarning(Warning):
    """Base warning for Dima."""


class InputCancelWarning(DimaWarning):
    """Input dialog cancelled; READ process cancelled."""



