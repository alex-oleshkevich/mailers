import abc
from email.message import EmailMessage


class Signer(abc.ABC):  # pragma: no cover
    @abc.abstractmethod
    def sign(self, message: EmailMessage) -> EmailMessage:
        raise NotImplementedError()
