"""This example demonstrates how you can create mailer plugins to perform before/after sending actions.

You need to setup several environment variables before you can use this script:

* MAILERS_RECIPIENT - a recipient's email ("To" header)
* MAILERS_FROM_ADDRESS - a sender address ("From" header)
* MAILER_URL - mailer configuration URL
"""
import asyncio
import os
from email.message import Message

from mailers import BasePlugin, EmailMessage, create_mailer


class PrintPlugin(BasePlugin):
    async def on_before_send(self, message: Message) -> None:
        print('sending message')

    async def on_after_send(self, message: Message) -> None:
        print('message has been sent')


async def main():
    message = EmailMessage(
        to=os.environ.get('MAILERS_RECIPIENT', 'root@localhost'),
        subject='Plugin test',
        text_body='Hello, this is a test message.',
        from_address=os.environ.get('MAILERS_FROM_ADDRESS', 'root@localhost'),
    )
    mailer = create_mailer(os.environ.get('MAILER_URL', 'null://'), plugins=[PrintPlugin()])
    await mailer.send(message)


if __name__ == '__main__':
    asyncio.run(main())
