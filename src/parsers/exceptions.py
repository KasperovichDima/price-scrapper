"""Base parser exceptions."""


class UnexpectedParserError(Exception):
    """Raises when get rsp.status != 200 while parsing."""
