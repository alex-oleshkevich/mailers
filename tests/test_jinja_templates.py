import jinja2
import pathlib
import pytest
import typing
from email.message import EmailMessage

from mailers import Email, InMemoryTransport, Mailer, TemplatedEmail
from mailers.plugins.jinja_renderer import JinjaRendererPlugin

THIS_DIR = pathlib.Path(__file__).parent


@pytest.mark.asyncio
async def test_renders_jinja_templates() -> None:
    env = jinja2.Environment(loader=jinja2.FileSystemLoader([THIS_DIR / "templates"]))

    mailbox: typing.List[EmailMessage] = []
    mailer = Mailer(InMemoryTransport(mailbox), plugins=[JinjaRendererPlugin(env)], from_address="root@localhost")
    await mailer.send(TemplatedEmail(html_template="mail.html", text_template="mail.txt", context={"hello": "world"}))

    assert mailbox[0].get_payload()[0].get_content() == "Text message: world.\n"
    assert mailbox[0].get_payload()[1].get_content() == "<b>HTML message: world</b>\n"


@pytest.mark.asyncio
async def test_ignores_regular_mails() -> None:
    env = jinja2.Environment(loader=jinja2.FileSystemLoader([THIS_DIR / "templates"]))

    mailbox: typing.List[EmailMessage] = []
    mailer = Mailer(InMemoryTransport(mailbox), plugins=[JinjaRendererPlugin(env)], from_address="root@localhost")
    await mailer.send(Email(text="Text message."))

    assert mailbox[0].get_content() == "Text message.\n"
