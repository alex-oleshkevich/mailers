from __future__ import annotations

from email.message import Message

from mailers.transports.base import Transport


class NullTransport(Transport):
    async def send(self, message: Message) -> None:
        pass
