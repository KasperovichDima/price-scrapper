"""Base parser exceptions."""


class UnexpectedParserError(Exception):
    """Raises when get rsp.status != 200 while parsing."""


class NotInitializedError(Exception):
    """Raises on attempt to use not initialized box."""
