import datetime
import email.utils as email_utils
import os
import pytest
import tempfile
from email.message import EmailMessage, Message
from email.mime.base import MIMEBase

from mailers.exceptions import InvalidBodyError
from mailers.message import Email


def test_email_subject(email):
    email.subject = 'Hello'
    assert email.subject == 'Hello'

    email.subject = 'çéîщ 😀'
    assert email.subject == 'çéîщ 😀'


_mapping = {
    'to': 'To',
    'cc': 'Cc',
    'bcc': 'Bcc',
    'reply_to': 'Reply-To',
    'from_address': 'From',
}


def get_header(message: Message, prop: str) -> str:
    return message[_mapping[prop]]


@pytest.mark.parametrize('prop', ['to', 'cc', 'bcc', 'reply_to', 'from_address'])
def test_email_adds_address_header(prop):
    email = Email(text='Test message.', from_address='sender@localhost')
    attr = getattr(email, prop)
    if prop == 'from_address':
        attr.clear()

    attr.add('root@localhost')
    attr.add('User <user@localhost>')

    assert get_header(email.build(), prop) == 'root@localhost, User <user@localhost>'


@pytest.mark.parametrize('prop', ['to', 'cc', 'bcc', 'reply_to', 'from_address'])
def test_email_overwrites_address_header(prop):
    email = Email(
        to=['user@localhost', 'user2@localhost'],
        cc=['user@localhost', 'user2@localhost'],
        bcc=['user@localhost', 'user2@localhost'],
        reply_to=['user@localhost', 'user2@localhost'],
        from_address=['user@localhost', 'user2@localhost'],
        sender='sender@localhost',
        text='Test message.',
    )
    setattr(email, prop, 'root@localhost')

    assert get_header(email.build(), prop) == 'root@localhost'


@pytest.mark.parametrize('prop', ['to', 'cc', 'bcc', 'reply_to', 'from_address'])
def test_email_adds_multiple_recipients_at_once(prop):
    email = Email(from_address='sender@localhost', text='Test message.')
    attr = getattr(email, prop)
    if prop == 'from_address':
        attr.clear()

    attr.add('root@localhost', 'User <user@localhost>')

    assert get_header(email.build(), prop) == 'root@localhost, User <user@localhost>'


@pytest.mark.parametrize('prop', ['to', 'cc', 'bcc', 'reply_to', 'from_address'])
def test_email_sets_string_recipient_via_constructor(prop):
    kwargs = {prop: 'root@localhost'}
    if prop != 'from_address':
        kwargs['from_address'] = 'sender@localhost'
    email = Email(**kwargs, text='Test message.')
    assert get_header(email.build(), prop) == 'root@localhost'


@pytest.mark.parametrize('prop', ['to', 'cc', 'bcc', 'reply_to', 'from_address'])
def test_email_sets_fqual_address_via_constructor(prop):
    kwargs = {prop: 'Root <root@localhost>'}
    email = Email(**kwargs)
    assert getattr(email, prop) == 'Root <root@localhost>'


@pytest.mark.parametrize('prop', ['to', 'cc', 'bcc', 'reply_to', 'from_address'])
def test_email_extends_addresses_set_by_constructor(prop):
    kwargs = {prop: ['Root <root@localhost>', 'user@localhost']}
    if prop != 'from_address':
        kwargs['from_address'] = 'sender@localhost'

    email = Email(**kwargs)
    attr = getattr(email, prop)
    attr.add('user2@localhost')
    assert attr == 'Root <root@localhost>, user@localhost, user2@localhost'


def test_sets_sender():
    email = Email(sender='sender@localhost', text='', from_address='from@localhost')
    assert email.build()['Sender'] == 'sender@localhost'

    email.sender = 'sender2@localhost'
    assert email.build()['Sender'] == 'sender2@localhost'

    email.sender = None
    assert 'Sender' not in email.build()


def test_email_sets_custom_headers_via_constructor():
    email = Email(headers={'X-Custom': 'Value'}, from_address='sender@localhost', text='Test message.')
    assert email.headers['X-Custom'] == 'Value'
    assert email.build()['X-Custom'] == 'Value'


def test_adds_date_header_in_constructor(monkeypatch):
    now = datetime.datetime(2021, 1, 1, 0, 0, 0)
    monkeypatch.setattr(email_utils, 'localtime', lambda: now)
    email = Email(from_address='sender@localhost', text='Test message.')
    assert email.build()['Date'] == 'Fri, 01 Jan 2021 00:00:00 -0000'


def test_changes_date_header(monkeypatch):
    now = datetime.datetime(2021, 1, 1, 0, 0, 0)
    hour_later = datetime.datetime(2021, 1, 1, 1, 0, 0)
    monkeypatch.setattr(email_utils, 'localtime', lambda: now)
    email = Email(from_address='sender@localhost', text='Test message.')
    email.date = hour_later

    assert email.build()['Date'] == 'Fri, 01 Jan 2021 01:00:00 -0000'


def test_requires_html_or_text_or_attachment_parts():
    email = Email(from_address='sender@localhost')
    with pytest.raises(InvalidBodyError) as ex:
        email.build()
    assert str(ex.value) == 'Email message must have a text, or HTML part or attachments.'

    email = Email(from_address='sender@localhost', text='Text')
    assert email.build()

    email = Email(from_address='sender@localhost', html='HTML')
    assert email.build()

    email = Email(from_address='sender@localhost')
    email.attach('body')
    assert email.build()


def test_generates_text_only_message():
    email = Email(from_address='sender@localhost', to='root@localhost', text='Test message.')
    mime_message = email.build()
    assert mime_message.is_multipart() is False
    assert mime_message.get_payload() == 'Test message.\n'


def test_generates_html_only_message():
    email = Email(from_address='sender@localhost', to='root@localhost', html='Test message.')
    mime_message = email.build()
    assert mime_message.is_multipart() is False
    assert mime_message.get_payload() == 'Test message.\n'


def test_generates_attachments_only_message():
    email = Email(from_address='sender@localhost', to='root@localhost')
    email.attach('one', 'file1.txt')
    email.attach('two', 'file2.txt')
    mime_message = email.build()
    assert mime_message.get_content_type() == 'multipart/mixed'
    assert mime_message.is_multipart() is True
    assert mime_message.get_payload()[0].get_content() == b'one'
    assert mime_message.get_payload()[1].get_content() == b'two'


def test_generates_text_and_html_message():
    email = Email(
        from_address='sender@localhost',
        to='root@localhost',
        text='Text message.',
        html='HTML message.',
        headers={'X-Custom': 'x-value'},
    )
    mime_message = email.build()
    assert mime_message.is_multipart() is True
    assert mime_message['From'] == 'sender@localhost'
    assert mime_message['To'] == 'root@localhost'
    assert mime_message['X-Custom'] == 'x-value'
    assert mime_message.get_content_type() == 'multipart/alternative'
    assert mime_message.get_payload()[0].get_content_type() == 'text/plain'
    assert mime_message.get_payload()[0].get_payload() == 'Text message.\n'
    assert mime_message.get_payload()[1].get_content_type() == 'text/html'
    assert mime_message.get_payload()[1].get_payload() == 'HTML message.\n'


def test_generates_text_and_html_and_related_message():
    email = Email(
        from_address='sender@localhost',
        to='root@localhost',
        text='Text message.',
        html='HTML message.',
        headers={'X-Custom': 'x-value'},
    )
    email.embed(b'CONTENT', 'content', 'application/octet-stream')
    mime_message = email.build()
    assert mime_message.is_multipart() is True
    assert mime_message['From'] == 'sender@localhost'
    assert mime_message['To'] == 'root@localhost'
    assert mime_message['X-Custom'] == 'x-value'
    assert mime_message.get_content_type() == 'multipart/alternative'

    text_part = mime_message.get_payload()[0]
    assert text_part.get_content_type() == 'text/plain'

    html_part = mime_message.get_payload()[1]
    assert html_part.get_content_type() == 'multipart/related'
    assert html_part.get_payload()[0].get_content_type() == 'text/html'
    assert html_part.get_payload()[1].get_content_type() == 'application/octet-stream'
    assert html_part.get_payload()[1].get_content() == b'CONTENT'


def test_generates_html_and_related_message():
    email = Email(
        from_address='sender@localhost',
        to='root@localhost',
        html='HTML message.',
        headers={'X-Custom': 'x-value'},
    )
    email.embed(b'CONTENT', 'content', 'application/octet-stream')
    mime_message = email.build()
    assert mime_message.is_multipart() is True
    assert mime_message['From'] == 'sender@localhost'
    assert mime_message['To'] == 'root@localhost'
    assert mime_message['X-Custom'] == 'x-value'
    assert mime_message.get_content_type() == 'multipart/alternative'

    html_part = mime_message.get_payload()[0]
    assert html_part.get_content_type() == 'multipart/related'
    assert html_part.get_payload()[0].get_content_type() == 'text/html'
    assert html_part.get_payload()[1].get_content_type() == 'application/octet-stream'
    assert html_part.get_payload()[1].get_content() == b'CONTENT'


def test_attach_text():
    email = Email(from_address='sender@localhost', to='root@localhost')
    email.attach('Hello')

    mime_message = email.build()
    part: EmailMessage = mime_message.get_payload()[0]
    assert part.get_content() == b'Hello'
    assert part.get_content_type() == 'application/octet-stream'
    assert part.get_filename() is None


def test_attach_binary():
    email = Email(from_address='sender@localhost', to='root@localhost')
    email.attach(b'Hello')

    mime_message = email.build()
    part: EmailMessage = mime_message.get_payload()[0]
    assert part.get_content() == b'Hello'
    assert part.get_content_type() == 'application/octet-stream'
    assert part.get_filename() is None


def test_attach_text_with_filename_and_type():
    email = Email(from_address='sender@localhost', to='root@localhost')
    email.attach('Hello', 'file.html', 'text/html')

    mime_message = email.build()
    part: EmailMessage = mime_message.get_payload()[0]
    assert part.get_content() == 'Hello'
    assert part.get_content_type() == 'text/html'
    assert part.get_filename() == 'file.html'


def test_attach_binary_with_filename_and_type():
    email = Email(from_address='sender@localhost', to='root@localhost')
    email.attach(b'Hello', 'file.html', 'application/octet-stream')

    mime_message = email.build()
    part: EmailMessage = mime_message.get_payload()[0]
    assert part.get_content() == b'Hello'
    assert part.get_content_type() == 'application/octet-stream'
    assert part.get_filename() == 'file.html'


@pytest.mark.asyncio
async def test_attach_from_path():
    with tempfile.NamedTemporaryFile(suffix='.txt') as f:
        f.write(b'Hello')
        f.seek(0)

        email = Email(from_address='sender@localhost', to='root@localhost')
        await email.attach_from_path(f.name)

        mime_message = email.build()
        part: EmailMessage = mime_message.get_payload()[0]
        assert part.get_content() == 'Hello'
        assert part.get_content_type() == 'text/plain'
        assert part.get_filename() == os.path.basename(f.name)

        email = Email(from_address='sender@localhost', to='root@localhost')
        await email.attach_from_path(f.name, 'file.html', 'text/html')

        mime_message = email.build()
        part: EmailMessage = mime_message.get_payload()[0]
        assert part.get_content() == 'Hello'
        assert part.get_content_type() == 'text/html'
        assert part.get_filename() == 'file.html'


def test_attach_from_path_sync():
    with tempfile.NamedTemporaryFile(suffix='.txt') as f:
        f.write(b'Hello')
        f.seek(0)

        email = Email(from_address='sender@localhost', to='root@localhost')
        email.attach_from_path_sync(f.name)

        mime_message = email.build()
        part: EmailMessage = mime_message.get_payload()[0]
        assert part.get_content() == 'Hello'
        assert part.get_content_type() == 'text/plain'
        assert part.get_filename() == os.path.basename(f.name)

        email = Email(from_address='sender@localhost', to='root@localhost')
        email.attach_from_path_sync(f.name, 'file.html', 'text/html')

        mime_message = email.build()
        part: EmailMessage = mime_message.get_payload()[0]
        assert part.get_content() == 'Hello'
        assert part.get_content_type() == 'text/html'
        assert part.get_filename() == 'file.html'


def test_embed_text():
    email = Email(from_address='sender@localhost', to='root@localhost', html='HTML message.')
    email.embed('Hello')

    mime_message = email.build()
    html_part: EmailMessage = mime_message.get_payload()[0]
    inline_part: EmailMessage = html_part.get_payload()[1]

    assert inline_part.get_content() == 'Hello\n'
    assert inline_part.get_content_type() == 'text/plain'
    assert inline_part.get_filename() is None


def test_embed_binary():
    email = Email(from_address='sender@localhost', to='root@localhost', html='HTML message.')
    email.embed(b'Hello')

    mime_message = email.build()
    html_part: EmailMessage = mime_message.get_payload()[0]
    inline_part: EmailMessage = html_part.get_payload()[1]

    assert inline_part.get_content() == b'Hello'
    assert inline_part.get_content_type() == 'application/octet-stream'
    assert inline_part.get_filename() is None


def test_embed_text_with_filename_and_type():
    email = Email(from_address='sender@localhost', to='root@localhost', html='HTML message.')
    email.embed('"Hello"', 'file.json', 'application/json')

    mime_message = email.build()
    html_part: EmailMessage = mime_message.get_payload()[0]
    inline_part: EmailMessage = html_part.get_payload()[1]

    assert inline_part.get_content() == '"Hello"\n'
    assert inline_part.get_content_type() == 'text/plain'
    assert inline_part.get_filename() == 'file.json'


def test_embed_binary_with_filename_and_type():
    email = Email(from_address='sender@localhost', to='root@localhost', html='HTML message.')
    email.embed(b'"Hello"', 'file.json', 'application/json')

    mime_message = email.build()
    html_part: EmailMessage = mime_message.get_payload()[0]
    inline_part: EmailMessage = html_part.get_payload()[1]

    assert inline_part.get_content() == b'"Hello"'
    assert inline_part.get_content_type() == 'application/json'
    assert inline_part.get_filename() == 'file.json'


@pytest.mark.asyncio
async def test_embed_from_path():
    with tempfile.NamedTemporaryFile(suffix='.txt') as f:
        f.write(b'Hello')
        f.seek(0)

        email = Email(from_address='sender@localhost', to='root@localhost', html='HTML message.')
        await email.embed_from_path(f.name)

        mime_message = email.build()
        html_part: EmailMessage = mime_message.get_payload()[0]
        inline_part: EmailMessage = html_part.get_payload()[1]
        assert inline_part.get_content() == 'Hello\n'
        assert inline_part.get_content_type() == 'text/plain'
        assert inline_part.get_filename() == os.path.basename(f.name)


@pytest.mark.asyncio
async def test_embed_from_path_with_filename_and_type():
    with tempfile.NamedTemporaryFile(suffix='.txt') as f:
        f.write(b'Hello')
        f.seek(0)

        email = Email(from_address='sender@localhost', to='root@localhost', html='HTML message.')
        await email.embed_from_path(f.name, 'file.html', 'text/html')

        mime_message = email.build()
        html_part: EmailMessage = mime_message.get_payload()[0]
        inline_part: EmailMessage = html_part.get_payload()[1]
        assert inline_part.get_content() == 'Hello\n'
        assert inline_part.get_content_type() == 'text/html'
        assert inline_part.get_filename() == 'file.html'


def test_embed_from_path_sync():
    with tempfile.NamedTemporaryFile(suffix='.txt') as f:
        f.write(b'Hello')
        f.seek(0)

        email = Email(from_address='sender@localhost', to='root@localhost', html='HTML message.')
        email.embed_from_path_sync(f.name)

        mime_message = email.build()
        html_part: EmailMessage = mime_message.get_payload()[0]
        inline_part: EmailMessage = html_part.get_payload()[1]
        assert inline_part.get_content() == 'Hello\n'
        assert inline_part.get_content_type() == 'text/plain'
        assert inline_part.get_filename() == os.path.basename(f.name)


def test_attach_part():
    email = Email(from_address='sender@localhost', to='root@localhost')

    custom_part = MIMEBase('text', 'plain')
    custom_part.set_payload('CONTENT')
    email.attach_part(custom_part)

    mime_message = email.build()
    part: EmailMessage = mime_message.get_payload()[0]
    assert part.get_payload() == 'CONTENT'


def test_validates_content_presence():
    with pytest.raises(InvalidBodyError):
        email = Email(from_address='sender@localhost')
        email.build()
