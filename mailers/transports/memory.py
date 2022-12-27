from __future__ import annotations

import typing
from email.message import EmailMessage

from mailers.transports.base import Transport


class InMemoryTransport(Transport):
    def __init__(self, storage: typing.Optional[typing.List[EmailMessage]] = None) -> None:
        self.storage = [] if storage is None else storage

    @property
    def mailbox(self) -> typing.List[EmailMessage]:
        return self.storage

    async def send(self, message: EmailMessage) -> None:
        self.storage.append(message)
