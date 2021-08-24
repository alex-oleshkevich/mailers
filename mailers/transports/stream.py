import typing as t
from email.message import Message

from mailers.result import SentMessage
from mailers.transports.base import Transport


class StreamTransport(Transport):
    def __init__(self, output: t.IO):
        self._output = output

    async def send(self, message: Message) -> SentMessage:
        self._output.write(str(message))
        return SentMessage(True, message, self)
