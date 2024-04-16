"""
This example demonstrates how you can create your own transport and use it with mailers.

You need to setup several environment variables before you can use this script:

* MAILERS_RECIPIENT - a recipient's email ("To" header)
* MAILERS_FROM_ADDRESS - a sender address ("From" header)
"""

import asyncio
import os
import sys
import typing as t
from email.message import Message

from mailers import Mailer, Transport
from mailers.message import Email

MAILERS_RECIPIENT = os.environ.get("MAILERS_RECIPIENT", "root@localhost")
MAILERS_FROM_ADDRESS = os.environ.get("MAILERS_FROM_ADDRESS", "sender@localhost")


class PrintTransport(Transport):
    def __init__(self, stream: t.IO) -> None:
        self.stream = stream

    async def send(self, message: Message) -> None:
        self.stream.write(str(message))


async def main() -> None:
    message = Email(
        to=MAILERS_RECIPIENT,
        subject="Custom transport test",
        text="Hello, this is a test message.",
        from_address=MAILERS_FROM_ADDRESS,
    )
    mailer = Mailer(PrintTransport(sys.stdout))
    await mailer.send(message)


if __name__ == "__main__":
    asyncio.run(main())
