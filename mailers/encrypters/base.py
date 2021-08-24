import abc
from email.message import Message


class Encrypter(abc.ABC):  # pragma: no cover
    @abc.abstractmethod
    def encrypt(self, message: Message) -> Message:
        raise NotImplementedError()
