"""Errors defined for Perf task."""

class Error(Exception):
  """A base class for errors related to Perf task."""


class EmptyCollectionError(Error):
  """Error related to the parsing result which is empty."""

  def __init__(self, message='No valid cycle is detected!'):
    super().__init__(message)
