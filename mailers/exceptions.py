class MailersError(Exception):
    """Base error class."""


class NotRegisteredTransportError(MailersError):
    """Raised when transport is not registered but retrieved."""


class BadHeaderError(MailersError):
    """Raised if the header contains errors."""
