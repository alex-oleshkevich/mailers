from __future__ import annotations

from email.message import Message
from typing import Any, List

from mailers.result import SentMessage
from mailers.transports.base import Transport


class InMemoryTransport(Transport):
    @property
    def mailbox(self) -> List[Message]:
        return self._storage

    def __init__(self, storage: List[Message]):
        self._storage = storage

    async def send(self, message: Message) -> SentMessage:
        self._storage.append(message)
        return SentMessage(True, message, self)

    @classmethod
    def from_url(cls, *args: Any) -> InMemoryTransport:
        mailbox: List[Message] = []
        return cls(mailbox)
