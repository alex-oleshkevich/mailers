class MailersError(Exception):
    pass


class SMTPError(MailersError):
    pass


class DependencyNotFound(MailersError):
    pass


class ImproperlyConfiguredError(MailersError):
    pass


class ImportFromStringError(MailersError):
    pass


class NotRegisteredTransportError(MailersError):
    pass


class BadHeaderError(MailersError):
    pass


class NotRegisteredMailer(MailersError):
    pass
