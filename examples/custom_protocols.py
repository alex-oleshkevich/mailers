"""This example demonstrates how you can create your own transport and register it as a custom protocol."""
import asyncio
import sys
import typing as t

from mailers import BaseTransport, EmailMessage, EmailURL, Transport, add_protocol_handler, create_mailer


class PrintTransport(BaseTransport):
    def __init__(self, stream: t.IO) -> None:
        self.stream = stream

    async def send(self, message: EmailMessage) -> None:
        self.stream.write(str(message))

    @classmethod
    def from_url(cls, url: t.Union[str, EmailURL]) -> t.Optional[Transport]:
        print(url.options)
        stream_name = url.options.get('stream')
        if stream_name == 'stdout':
            return PrintTransport(sys.stdout)
        if stream_name == 'stderr':
            return PrintTransport(sys.stderr)
        raise ValueError('Unknown stream type %s.' % stream_name)


# bind PrintTransport to "print" protocol
add_protocol_handler('print', PrintTransport)


async def main():
    message = EmailMessage(to='root@localhost', subject='Hello', text_body='World', from_address='reply@localhost')
    mailer = create_mailer('print://?stream=stdout')  # or stream=stderr
    await mailer.send(message)


if __name__ == '__main__':
    asyncio.run(main())
