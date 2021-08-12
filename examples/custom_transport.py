"""This example demonstrates how you can create your own transport and use it with mailers."""
import asyncio
import sys
import typing as t

from mailers import BaseTransport, EmailMessage, Mailer


class PrintTransport(BaseTransport):
    def __init__(self, stream: t.IO) -> None:
        self.stream = stream

    async def send(self, message: EmailMessage) -> None:
        self.stream.write(str(message))


async def main():
    message = EmailMessage(to='root@localhost', subject='Hello', text_body='World', from_address='reply@localhost')
    mailer = Mailer(PrintTransport(sys.stdout))
    await mailer.send(message)


if __name__ == '__main__':
    asyncio.run(main())
