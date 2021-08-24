from __future__ import annotations

from email.message import Message
from typing import Any

from mailers.result import SentMessage
from mailers.transports.base import Transport


class NullTransport(Transport):
    async def send(self, message: Message) -> SentMessage:
        return SentMessage(True, message, self)

    @classmethod
    def from_url(cls, *args: Any) -> NullTransport:
        return cls()
