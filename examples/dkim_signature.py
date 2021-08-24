"""This example demonstrates how to add DKIM signature to your outgoing messages.

You need to setup several environment variables before you can use this script:

* MAILERS_RECIPIENT - a recipient's email ("To" header)
* MAILERS_FROM_ADDRESS - a sender address ("From" header)
* MAILER_URL - mailer configuration URL
* MAILERS_DKIM_KEY_PATH - a path to DKIM private key

Also make sure that you have set up DKIM DNS TXT record.
Also, you may need to setup SPF DNS TEXT record as well if sender's IP is not the same as DKIM domain.
"""
import asyncio
import os

from mailers import create_mailer
from mailers.message import Email
from mailers.signers import DKIMSigner

MAILER_URL = os.environ.get('MAILER_URL', 'null://')
MAILERS_RECIPIENT = os.environ.get('MAILERS_RECIPIENT', 'root@localhost')
MAILERS_FROM_ADDRESS = os.environ.get('MAILERS_FROM_ADDRESS', 'sender@localhost')
MAILERS_DKIM_KEY_PATH = os.environ.get('MAILERS_DKIM_KEY_PATH')


async def main():
    message = Email(
        to=MAILERS_RECIPIENT,
        subject='DKIM check',
        text='Hello, this is a test message to check the DKIM signature.',
        from_address=MAILERS_FROM_ADDRESS,
    )
    mailer = create_mailer(
        MAILER_URL,
        signer=DKIMSigner(selector='default', private_key_path=MAILERS_DKIM_KEY_PATH),
    )
    await mailer.send(message)


if __name__ == '__main__':
    asyncio.run(main())
