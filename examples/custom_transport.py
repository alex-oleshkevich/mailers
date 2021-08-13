"""This example demonstrates how you can create your own transport and use it with mailers.

You need to setup several environment variables before you can use this script:

* MAILERS_RECIPIENT - a recipient's email ("To" header)
* MAILERS_FROM_ADDRESS - a sender address ("From" header)
* MAILER_URL - mailer configuration URL
"""
import asyncio
import os
import sys
import typing as t
from email.message import Message

from mailers import BaseTransport, EmailMessage, Mailer


class PrintTransport(BaseTransport):
    def __init__(self, stream: t.IO) -> None:
        self.stream = stream

    async def send(self, message: Message) -> None:
        self.stream.write(str(message))


async def main():
    message = EmailMessage(
        to=os.environ.get('MAILERS_RECIPIENT', 'root@localhost'),
        subject='Attachments test',
        text_body='Hello, this is a test message with attachments.',
        from_address=os.environ.get('MAILERS_FROM_ADDRESS', 'root@localhost'),
    )
    mailer = Mailer(PrintTransport(sys.stdout))
    await mailer.send(message)


if __name__ == '__main__':
    asyncio.run(main())
