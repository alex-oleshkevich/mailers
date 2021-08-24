import abc
from email.message import Message


class Signer(abc.ABC):  # pragma: no cover
    @abc.abstractmethod
    def sign(self, message: Message) -> Message:
        raise NotImplementedError()
