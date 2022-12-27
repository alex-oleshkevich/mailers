"""
This example demonstrates how you can create mailer plugins to perform before/after sending actions.

You need to setup several environment variables before you can use this script:

* MAILERS_RECIPIENT - a recipient's email ("To" header)
* MAILERS_FROM_ADDRESS - a sender address ("From" header)
* MAILER_URL - mailer configuration URL
"""
import asyncio
import os
from email.message import Message

from mailers import BasePlugin, Mailer, create_transport_from_url
from mailers.message import Email

MAILER_URL = os.environ.get("MAILER_URL", "null://")
MAILERS_RECIPIENT = os.environ.get("MAILERS_RECIPIENT", "root@localhost")
MAILERS_FROM_ADDRESS = os.environ.get("MAILERS_FROM_ADDRESS", "sender@localhost")


class PrintPlugin(BasePlugin):
    async def on_before_send(self, message: Message) -> None:
        message.replace_header("Subject", "[CHANGED BY PLUGIN] " + message["Subject"])
        print("sending message")

    async def on_after_send(self, message: Message) -> None:
        print("message has been sent")


async def main() -> None:
    message = Email(
        to=MAILERS_RECIPIENT,
        subject="Plugin test",
        text="Hello, this is a test message.",
        from_address=MAILERS_FROM_ADDRESS,
    )
    mailer = Mailer(create_transport_from_url(MAILER_URL), plugins=[PrintPlugin()])
    await mailer.send(message)


if __name__ == "__main__":
    asyncio.run(main())
