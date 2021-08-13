"""This example demonstrates how to add DKIM signature to your outgoing messages.

You need to setup several environment variables before you can use this script:

* MAILERS_RECIPIENT - an address to use in "To" header
* MAILERS_FROM_ADDRESS - a sender address ("From" header)
* MAILER_URL - mailer configuration URL
* MAILERS_DKIM_KEY_PATH - a path to DKIM private key

Also make sure that you have set up DKIM DNS TXT record.
Also, you may need to setup SPF DNS TEXT record as well if sender's IP is not the same as DKIM domain.
"""
import asyncio
import os

from mailers import EmailMessage, create_mailer
from mailers.plugins.dkim import DkimSignature


async def main():
    message = EmailMessage(
        to=os.environ.get('MAILERS_RECIPIENT', 'root@localhost'),
        subject='DKIM check',
        text_body='Hello, this is a test message to check the DKIM signature.',
        from_address=os.environ.get('MAILERS_FROM_ADDRESS', 'root@localhost'),
    )
    mailer = create_mailer(
        os.environ.get('MAILER_URL', 'null://'),
        plugins=[DkimSignature(selector='default', private_key_path=os.environ.get('MAILERS_DKIM_KEY_PATH'))],
    )
    await mailer.send(message)


if __name__ == '__main__':
    asyncio.run(main())
