import abc
from email.message import EmailMessage


class Encrypter(abc.ABC):  # pragma: no cover
    @abc.abstractmethod
    def encrypt(self, message: EmailMessage) -> EmailMessage:
        raise NotImplementedError()
