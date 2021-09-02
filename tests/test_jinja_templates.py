import jinja2
import pathlib

from mailers import Email, InMemoryTransport, Mailer, TemplatedEmail
from mailers.plugins.jinja_renderer import JinjaRendererPlugin

THIS_DIR = pathlib.Path().parent


def test_renders_jinja_templates():
    env = jinja2.Environment(loader=jinja2.FileSystemLoader([THIS_DIR / 'templates']))

    mailbox = []
    mailer = Mailer(InMemoryTransport(mailbox), plugins=[JinjaRendererPlugin(env)], from_address='root@localhost')
    mailer.send_sync(TemplatedEmail(html_template='mail.html', text_template='mail.txt', context={'hello': 'world'}))

    assert mailbox[0].get_payload()[0].get_content() == 'Text message: world.\n'
    assert mailbox[0].get_payload()[1].get_content() == '<b>HTML message: world</b>\n'


def test_ignores_regular_mails():
    env = jinja2.Environment(loader=jinja2.FileSystemLoader([THIS_DIR / 'templates']))

    mailbox = []
    mailer = Mailer(InMemoryTransport(mailbox), plugins=[JinjaRendererPlugin(env)], from_address='root@localhost')
    mailer.send_sync(Email(text='Text message.'))

    assert mailbox[0].get_content() == 'Text message.\n'
