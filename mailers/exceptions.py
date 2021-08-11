class MailersError(Exception):
    """Base error class."""


class NotRegisteredTransportError(MailersError):
    """Raised when transport is not registered but retrieved."""


class BadHeaderError(MailersError):
    """Raised if the header contains errors."""


class MailerIsRegisteredError(MailersError):
    """Raised if the mailer's name is already taken."""


class NotRegisteredMailer(MailersError):
    """Raised when a mailer is not registered."""
