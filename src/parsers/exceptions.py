"""Base parser exceptions."""


class WrongFactoryConfigurationError(BaseException):
    """Raises upon attemt to create factory with improper init data."""
