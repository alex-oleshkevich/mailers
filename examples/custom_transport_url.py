"""This example demonstrates how you can create your own transport and register it as a custom protocol.

You need to setup several environment variables before you can use this script:

* MAILERS_RECIPIENT - a recipient's email ("To" header)
* MAILERS_FROM_ADDRESS - a sender address ("From" header)
"""
import asyncio
import os
import sys
import typing as t
from email.message import Message

from mailers import BaseTransport, EmailURL, Transport, add_protocol_handler, create_mailer
from mailers.message import Email

MAILERS_RECIPIENT = os.environ.get('MAILERS_RECIPIENT', 'root@localhost')
MAILERS_FROM_ADDRESS = os.environ.get('MAILERS_FROM_ADDRESS', 'sender@localhost')


class PrintTransport(BaseTransport):
    def __init__(self, stream: t.IO) -> None:
        self.stream = stream

    async def send(self, message: Message) -> None:
        self.stream.write(str(message))

    @classmethod
    def from_url(cls, url: t.Union[str, EmailURL]) -> t.Optional[Transport]:
        stream_name = url.options.get('stream')
        if stream_name == 'stdout':
            return PrintTransport(sys.stdout)
        if stream_name == 'stderr':
            return PrintTransport(sys.stderr)
        raise ValueError('Unknown stream type %s.' % stream_name)


# bind PrintTransport to "print" protocol
add_protocol_handler('print', PrintTransport)


async def main():
    message = Email(
        to=MAILERS_RECIPIENT,
        subject='Custom transport URL test',
        text='Hello, this is a test message.',
        from_address=MAILERS_FROM_ADDRESS,
    )
    mailer = create_mailer('print://?stream=stdout')  # or stream=stderr
    await mailer.send(message)


if __name__ == '__main__':
    asyncio.run(main())
