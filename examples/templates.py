"""
This is a demo of templated mails.

You need to setup several environment variables before you can use this script:

* MAILERS_RECIPIENT - a recipient's email ("To" header)
* MAILERS_FROM_ADDRESS - a sender address ("From" header)
* MAILER_URL - mailer configuration URL
"""
import asyncio
import jinja2
import os
import pathlib

from mailers import TemplatedMailer

MAILER_URL = os.environ.get("MAILER_URL", "null://")
MAILERS_RECIPIENT = os.environ.get("MAILERS_RECIPIENT", "root@localhost")
MAILERS_FROM_ADDRESS = os.environ.get("MAILERS_FROM_ADDRESS", "sender@localhost")
THIS_DIR = pathlib.Path(__file__).parent


async def main() -> None:
    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(THIS_DIR / "templates"))
    mailer = TemplatedMailer(MAILER_URL, jinja_env=jinja_env)
    await mailer.send_templated_message(
        to=MAILERS_RECIPIENT,
        from_address="root@localhost",
        subject="Test message",
        text_template="mail.txt",
        html_template="mail.html",
        template_context={"hello": "world"},
    )


if __name__ == "__main__":
    asyncio.run(main())
