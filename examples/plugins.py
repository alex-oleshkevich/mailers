"""This example demonstrates how you can create your own transport and register it as a custom protocol."""
import asyncio

from mailers import BasePlugin, EmailMessage, create_mailer


class PrintPlugin(BasePlugin):
    async def on_before_send(self, message: EmailMessage) -> None:
        print('sending message')

    async def on_after_send(self, message: EmailMessage) -> None:
        print('message has been sent')


async def main():
    message = EmailMessage(to='root@localhost', subject='Hello', text_body='World', from_address='reply@localhost')
    mailer = create_mailer('null://', plugins=[PrintPlugin()])
    await mailer.send(message)


if __name__ == '__main__':
    asyncio.run(main())
