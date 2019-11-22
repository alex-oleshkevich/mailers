import datetime
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pytest

from mailers.exceptions import BadHeaderError
from mailers.message import Attachment, EmailMessage


def _test_value_assigment(message, prop):
    # value as list of emails
    # message.to = ['user@localhost', 'another_user@localhost']
    setattr(message, prop, ["user@localhost", "another_user@localhost"])
    assert getattr(message, prop) == ["user@localhost", "another_user@localhost"]

    # value as string
    # message.to = user@localhost
    setattr(message, prop, "another_user@localhost")
    assert getattr(message, prop) == ["another_user@localhost"]

    # add email via adder
    # message.add_to('user@localhost')
    # message.add_to('user@localhost', 'UserName')
    setattr(message, prop, [])
    adder = getattr(message, f"add_{prop}")
    adder("user@localhost")
    adder("second_user@localhost", "UserName")
    assert getattr(message, prop) == [
        "user@localhost",
        "UserName <second_user@localhost>",
    ]


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
            "Date": datetime.datetime(2000, 12, 1, 0, 0, 0),
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
    assert message.date == "2000-01-01T00:00:00"

    assert message.from_address == "root@localhost"
    assert message.subject == "SUBJECT"
    assert message.text_body == "CONTENTS"
    assert message.html_body == "<b>CONTENTS</b>"

    assert message.attachments == [att1]
    assert message.headers == {"Date": "2000-01-01T00:00:00", "X-Custom": "x-value"}
    assert message.parts == [extra_message_part]


def test_to(message):
    _test_value_assigment(message, "to")


def test_cc(message):
    _test_value_assigment(message, "cc")


def test_bcc(message):
    _test_value_assigment(message, "bcc")


def test_reply_to(message):
    _test_value_assigment(message, "reply_to")


def test_date(message):
    today = datetime.datetime.today()
    message.date = today
    assert message.date == today.isoformat()


def test_headers(message):
    message.headers = {"X-Name": "value"}
    assert message.headers == {"X-Name": "value"}


def test_add_attachments(message):
    attachment = Attachment("file.txt", "contents")
    message.add_attachment(attachment)
    assert message.attachments == [attachment]


def test_attach(message):
    message.attach("contents", "file.txt", "text/plain", "utf8")
    assert len(message.attachments) == 1
    assert message.attachments[0].file_name == "file.txt"
    assert message.attachments[0].mime_type == "text/plain"
    assert message.attachments[0].charset == "utf8"


def test_requires_to_or_bcc():
    message = EmailMessage(from_address="user@localhost")
    with pytest.raises(BadHeaderError) as ex:
        message.build_message()
    assert str(ex.value) == 'Neither "to" or "bcc" attribute was not set.'

    # ok if "to" set
    message = EmailMessage(to="user@localhost", from_address="user@localhost")
    message.build_message()

    # ok if "bcc" set
    message = EmailMessage(bcc="user@localhost", from_address="user@localhost")
    message.build_message()


def test_requires_from_address():
    message = EmailMessage(to="user@localhost")
    with pytest.raises(BadHeaderError) as ex:
        message.build_message()
    assert str(ex.value) == '"from_address" attribute was not set.'


def test_build_message(message: EmailMessage):
    message.date = datetime.datetime(2000, 1, 1, 0, 0, 0)
    message.from_address = "root@localhost"
    message.cc = "cc@localhost"
    message.bcc = "bcc@localhost"
    message.reply_to = "reply_to@localhost"
    message.subject = "SUBJECT"
    message.text_body = "TEXT"
    message.html_body = "HTML"
    message.attach("ATTACHMENT", "file.txt")
    message.add_part(MIMEText("EXTRA PART"))

    mime_message = message.build_message()
    assert isinstance(mime_message, MIMEMultipart)
    assert len(mime_message.get_payload()) == 3  # content, extra part and attachment

    content = mime_message.get_payload()[0]
    text_part, html_part = content.get_payload()
    assert "TEXT" == text_part.get_payload()
    assert "HTML" == html_part.get_payload()

    custom_part = mime_message.get_payload()[1]
    assert "EXTRA PART" == custom_part.get_payload()

    attachment_part = mime_message.get_payload()[2]
    assert "QVRUQUNITUVOVA==\n" == attachment_part.get_payload()


def test_as_string(message):
    assert isinstance(message.as_string(), str)
    assert isinstance(str(message), str)


def test_forbid_new_lines():
    message = EmailMessage(from_address="sender@localhost")
    message.to = "root@localhost\n"
    with pytest.raises(BadHeaderError) as ex:
        message.build_message()

    text = 'Header value "root@localhost\n" contains new line characters.'
    assert str(ex.value) == text

    message = EmailMessage(from_address="sender@localhost")
    message.to = "root@localhost\r"
    with pytest.raises(BadHeaderError) as ex:
        message.build_message()

    text = 'Header value "root@localhost\r" contains new line characters.'
    assert str(ex.value) == text


def test_add_part():
    message = EmailMessage(
        to="root@localhost", boundary="1111111", from_address="sender@localhost"
    )
    part = MIMEText("CONTENT")
    message.add_part(part)
    assert len(message.parts) == 1

    msg: email.message.Message = email.message_from_string(message.as_string())
    assert len(msg.get_payload()) == 2  # content part + custom part

    actual_part = msg.get_payload()[1]
    assert str(part) == str(actual_part)
