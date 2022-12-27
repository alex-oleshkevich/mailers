from __future__ import annotations

import abc
from email.message import EmailMessage


class Transport(abc.ABC):  # pragma: nocover
    @abc.abstractmethod
    async def send(self, message: EmailMessage) -> None:
        raise NotImplementedError()
