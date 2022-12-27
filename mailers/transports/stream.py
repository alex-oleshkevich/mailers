import typing
from email.message import Message

from mailers.transports.base import Transport


class StreamTransport(Transport):
    def __init__(self, output: typing.IO) -> None:
        self.stream = output

    async def send(self, message: Message) -> None:
        self.stream.write(str(message))
