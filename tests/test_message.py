import datetime
import pytest
import tempfile
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

from mailers.exceptions import BadHeaderError
from mailers.message import Attachment, EmailMessage


def test_creates_message_from_init():
    att1 = Attachment("file.txt", "filecontents", "application/mimetype")

    extra_message_part = MIMEText("CUSTOM PART CONTENT")
    message = EmailMessage(
        to="user@localhost",
        from_address="root@localhost",
        subject="SUBJECT",
        text_body="CONTENTS",
        html_body="<b>CONTENTS</b>",
        reply_to="trash@localhost",
        cc="cc_user@localhost",
        bcc="bcc_user@localhost",
        attachments=[att1],
        headers={
            "X-Custom": "x-value",
        },
        boundary="boundary---",
        parts=[extra_message_part],
        date=datetime.datetime(2000, 1, 1, 0, 0, 0),
    )

    # these created by __init__
    assert message.to == ["user@localhost"]
    assert message.reply_to == ["trash@localhost"]
    assert message.cc == ["cc_user@localhost"]
    assert message.bcc == ["bcc_user@localhost"]
    assert message.date.isoformat() == "2000-01-01T00:00:00"

    assert message.from_address == "root@localhost"
    assert message.subject == "SUBJECT"
    assert message.text_body == "CONTENTS"
    assert message.html_body == "<b>CONTENTS</b>"

    assert message.attachments == [att1]
    assert message.headers == {"X-Custom": "x-value"}
    assert message.parts == [extra_message_part]


def test_creates_message_from_init_using_lists():
    message = EmailMessage(
        to=["user@localhost", 'user2@localhost'],
        from_address="root@localhost",
        subject="SUBJECT",
        text_body="CONTENTS",
        reply_to=["reply@localhost", 'reply2@localhost'],
        cc=["cc@localhost", 'cc2@localhost'],
        bcc=["bcc@localhost", 'bcc2@localhost'],
    )

    mime_message = message.to_mime_message()
    assert mime_message['To'] == 'user@localhost, user2@localhost'
    assert mime_message['Cc'] == 'cc@localhost, cc2@localhost'
    assert mime_message['Bcc'] == 'bcc@localhost, bcc2@localhost'
    assert mime_message['Reply-To'] == 'reply@localhost, reply2@localhost'


def test_creates_message_from_init_using_nulls():
    message = EmailMessage(
        from_address="root@localhost",
        subject="SUBJECT",
        text_body="CONTENTS",
    )
    assert message.to == []
    assert message.cc == []
    assert message.bcc == []
    assert message.reply_to == []


def test_headers(message):
    message.headers = {"X-Name": "value"}
    assert message.headers == {"X-Name": "value"}


def test_add_attachments(message):
    attachment = Attachment("file.txt", "contents")
    message.add_attachment(attachment)
    assert message.attachments == [attachment]


def test_attach(message: EmailMessage):
    message.attach("file.txt", "contents", "text/plain", charset="utf-8", headers={'X-Test': 'value'})
    assert len(message.attachments) == 1
    mime_message = message.to_mime_message()
    attachment: MIMEBase = mime_message.get_payload()[1]
    assert attachment['X-Test'] == 'value'
    assert attachment.get_charset() == 'utf-8'
    assert 'text/plain' in attachment['Content-Type']
    assert attachment['Content-Disposition'] == 'attachment; filename="file.txt"'


@pytest.mark.asyncio
async def test_attach_file(message):
    with tempfile.NamedTemporaryFile('w') as f:
        f.write('test')
        f.seek(0)
        await message.attach_file(f.name)
    assert message.attachments[0].content == b'test'


@pytest.mark.asyncio
async def test_attach_file_guess_mime(message):
    with tempfile.NamedTemporaryFile('w', suffix='.jpg') as f:
        print(f.name)
        f.write('test')
        f.seek(0)
        await message.attach_file(f.name)
    assert message.attachments[0].mime_type == 'image/jpeg'


def test_requires_to_or_bcc():
    message = EmailMessage(from_address="user@localhost")
    with pytest.raises(AssertionError) as ex:
        message.to_mime_message()
    assert str(ex.value) == 'Either value for "to" or "bcc" required.'

    # ok if "to" set
    message = EmailMessage(to="user@localhost", from_address="user@localhost")
    assert message.to_mime_message()['To'] == 'user@localhost'

    # ok if "bcc" set
    message = EmailMessage(bcc="user@localhost", from_address="user@localhost")
    assert message.to_mime_message()['Bcc'] == 'user@localhost'


def test_requires_from_address():
    message = EmailMessage(to="user@localhost")
    with pytest.raises(AssertionError) as ex:
        message.to_mime_message()
    assert str(ex.value) == 'A sender address (from_address) is required.'


def test_build_message(message: EmailMessage):
    message.date = datetime.datetime(2000, 1, 1, 0, 0, 0)
    message.from_address = "root@localhost"
    message.to = "to@localhost"
    message.cc = "cc@localhost"
    message.bcc = "bcc@localhost"
    message.reply_to = "reply_to@localhost"
    message.subject = "SUBJECT"
    message.text_body = "TEXT"
    message.html_body = "HTML"
    message.attach("file.txt", "ATTACHMENT", mime_type='text/plain')
    message.add_part(MIMEText("EXTRA PART"))

    mime_message = message.to_mime_message()
    assert mime_message['From'] == 'root@localhost'
    assert mime_message['To'] == 'to@localhost'
    assert mime_message['Cc'] == 'cc@localhost'
    assert mime_message['Bcc'] == 'bcc@localhost'
    assert mime_message['Reply-To'] == 'reply_to@localhost'
    assert mime_message['Subject'] == 'SUBJECT'

    text_part = mime_message.get_payload()[0]
    assert "TEXT" == text_part.get_payload()

    html_part = mime_message.get_payload()[1]
    assert "HTML" == html_part.get_payload()

    custom_part = mime_message.get_payload()[2]
    assert "EXTRA PART" == custom_part.get_payload()

    attachment_part = mime_message.get_payload()[3]
    assert "ATTACHMENT" == attachment_part.get_payload()


def test_as_string(message):
    assert isinstance(message.as_string(), str)
    assert isinstance(str(message), str)


def test_forbid_new_lines():
    message = EmailMessage(from_address="sender@localhost", to="root@localhost\n")
    with pytest.raises(BadHeaderError) as ex:
        message.to_mime_message()
    text = 'Header value "root@localhost\n" contains new line characters.'
    assert str(ex.value) == text

    message = EmailMessage(from_address="sender@localhost", to="root@localhost\r")
    with pytest.raises(BadHeaderError) as ex:
        message.to_mime_message()

    text = 'Header value "root@localhost\r" contains new line characters.'
    assert str(ex.value) == text


def test_add_part():
    message = EmailMessage(to="root@localhost", boundary="1111111", from_address="sender@localhost", text_body='Hey')
    message.add_part(MIMEText("CONTENT"))

    mime_message = message.to_mime_message()
    assert len(mime_message.get_payload()) == 2
