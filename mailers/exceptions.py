class MailablesError(Exception):
    pass


class SMTPError(MailablesError):
    pass


class DependencyNotFound(MailablesError):
    pass


class ImproperlyConfiguredError(MailablesError):
    pass


class ImportFromStringError(MailablesError):
    pass


class NotRegisteredTransportError(MailablesError):
    pass


class BadHeaderError(MailablesError):
    pass


class NotRegisteredMailer(MailablesError):
    pass
