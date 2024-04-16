"""
This is a very basic example. Here we send a plain text message.

You need to setup several environment variables before you can use this script:

* MAILERS_RECIPIENT - a recipient's email ("To" header)
* MAILERS_FROM_ADDRESS - a sender address ("From" header)
* MAILER_URL - mailer configuration URL
"""

import asyncio
import os

from mailers import Mailer, create_transport_from_url
from mailers.message import Email

MAILER_URL = os.environ.get("MAILER_URL", "null://")
MAILERS_RECIPIENT = os.environ.get("MAILERS_RECIPIENT", "root@localhost")
MAILERS_FROM_ADDRESS = os.environ.get("MAILERS_FROM_ADDRESS", "sender@localhost")


async def main() -> None:
    mailer = Mailer(create_transport_from_url(MAILER_URL))
    await mailer.send(
        Email(
            to=MAILERS_RECIPIENT,
            subject="Test message",
            text="Hello, this is a text message.",
            from_address=MAILERS_FROM_ADDRESS,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
