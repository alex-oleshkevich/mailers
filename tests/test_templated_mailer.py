import jinja2
import pathlib
import pytest
import typing
from email.message import EmailMessage

from mailers import InMemoryTransport
from mailers.mailer import TemplatedMailer

THIS_DIR = pathlib.Path(__file__).parent


@pytest.mark.asyncio
async def test_templated_mailer(mailbox: typing.List[EmailMessage]) -> None:
    env = jinja2.Environment(loader=jinja2.FileSystemLoader([THIS_DIR / "templates"]))

    transport = InMemoryTransport(mailbox)
    mailer = TemplatedMailer(transport=transport, jinja_env=env, from_address="root@localhost")
    await mailer.send_templated_message(
        to="root@localhost",
        subject="hello",
        html_template="mail.html",
        text_template="mail.txt",
        template_context={"hello": "world"},
    )
    assert mailbox[0].get_payload()[0].get_content() == "Text message: world.\n"
    assert mailbox[0].get_payload()[1].get_content() == "<b>HTML message: world</b>\n"


@pytest.mark.asyncio
async def test_templated_mailer_with_text_part(mailbox: typing.List[EmailMessage]) -> None:
    env = jinja2.Environment(loader=jinja2.FileSystemLoader([THIS_DIR / "templates"]))

    transport = InMemoryTransport(mailbox)
    mailer = TemplatedMailer(transport=transport, jinja_env=env, from_address="root@localhost")
    await mailer.send_templated_message(
        to="root@localhost",
        subject="hello",
        text_template="mail.txt",
        template_context={"hello": "world"},
    )
    assert mailbox[0].get_content() == "Text message: world.\n"


@pytest.mark.asyncio
async def test_templated_mailer_with_html_part(mailbox: typing.List[EmailMessage]) -> None:
    env = jinja2.Environment(loader=jinja2.FileSystemLoader([THIS_DIR / "templates"]))

    transport = InMemoryTransport(mailbox)
    mailer = TemplatedMailer(transport=transport, jinja_env=env, from_address="root@localhost")
    await mailer.send_templated_message(
        to="root@localhost",
        subject="hello",
        html_template="mail.html",
        template_context={"hello": "world"},
    )
    assert mailbox[0].get_payload() == "<b>HTML message: world</b>\n"
