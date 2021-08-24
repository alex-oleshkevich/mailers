"""This is a very basic example.
Here we send a HTML message along with a plain text part.

You need to setup several environment variables before you can use this script:

* MAILERS_RECIPIENT - a recipient's email ("To" header)
* MAILERS_FROM_ADDRESS - a sender address ("From" header)
* MAILER_URL - mailer configuration URL
"""
import asyncio
import os

from mailers import create_mailer
from mailers.message import Email

MAILER_URL = os.environ.get('MAILER_URL', 'null://')
MAILERS_RECIPIENT = os.environ.get('MAILERS_RECIPIENT', 'root@localhost')
MAILERS_FROM_ADDRESS = os.environ.get('MAILERS_FROM_ADDRESS', 'sender@localhost')


async def main():
    mailer = create_mailer(MAILER_URL)
    await mailer.send(
        Email(
            to=MAILERS_RECIPIENT,
            subject='Test HTML message',
            html='<html><body><b>Hello, this is a HTML message.</b></body></html>',
            from_address=MAILERS_FROM_ADDRESS,
        )
    )


if __name__ == '__main__':
    asyncio.run(main())
