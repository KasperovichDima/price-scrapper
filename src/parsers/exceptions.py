"""Base parser exceptions."""


class EmptyFactoryDataError(BaseException):
    """Raises upon attemt to create
    catalog factory with empty init data."""
