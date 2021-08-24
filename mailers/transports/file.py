from __future__ import annotations

import anyio as anyio
import datetime
import os
from email.message import Message
from typing import Union

from mailers.config import EmailURL
from mailers.result import SentMessage
from mailers.transports.base import Transport


class FileTransport(Transport):
    def __init__(self, directory: str):
        if directory is None or directory == "":
            raise ValueError('Argument "path" of FileTransport cannot be None.')

        self._directory = directory

    async def send(self, message: Message) -> SentMessage:
        file_name = "message_%s.eml" % datetime.datetime.today().isoformat()
        output_file = os.path.join(self._directory, file_name)
        async with await anyio.open_file(output_file, 'wb') as f:
            await f.write(message.as_bytes())
        return SentMessage(True, message, self)

    @classmethod
    def from_url(cls, url: Union[str, EmailURL]) -> FileTransport:
        url = EmailURL(url)
        return cls(url.path)
