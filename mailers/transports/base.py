from __future__ import annotations

import abc
import typing as t
from email.message import Message

from mailers.config import EmailURL
from mailers.result import SentMessage


class Transport(abc.ABC):  # pragma: nocover
    @abc.abstractmethod
    async def send(self, message: Message) -> SentMessage:
        raise NotImplementedError()

    @classmethod
    def from_url(cls, url: t.Union[str, EmailURL]) -> t.Optional[Transport]:
        return None
