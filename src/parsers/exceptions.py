"""Base parser exceptions."""


class UnexpectedParserException(Exception):
    """Raises when get rsp.status != 200 while parsing."""


class SavingResultsException(Exception):
    """Raise if error while saving parsing results."""
