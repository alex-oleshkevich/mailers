class MailersError(Exception):
    """Base error class."""


class NotRegisteredTransportError(MailersError):
    """Raised when transport is not registered but retrieved."""


class InvalidSenderError(MailersError):
    """Raised when From or Sender header is invalid."""


class InvalidBodyError(MailersError):
    """Raised when the message is empty."""
