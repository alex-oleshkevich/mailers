"""This is a very basic example.

You need to setup several environment variables before you can use this script:

* MAILERS_RECIPIENT - a recipient's email ("To" header)
* MAILERS_FROM_ADDRESS - a sender address ("From" header)
* MAILER_URL - mailer configuration URL
"""
import asyncio
import os

from mailers import EmailMessage, create_mailer


async def main():
    mailer = create_mailer(os.environ.get('MAILER_URL', 'null://'))
    await mailer.send(
        EmailMessage(
            to=os.environ.get('MAILERS_RECIPIENT', 'root@localhost'),
            subject='Test message',
            text_body='Hello, this is a test message.',
            from_address=os.environ.get('MAILERS_FROM_ADDRESS', 'root@localhost'),
        )
    )


if __name__ == '__main__':
    asyncio.run(main())
