from email.mime.base import MIMEBase

from mailers.message import Attachment


def test_attachment():
    attachment = Attachment(
        file_name="file.txt",
        contents="CONTENTS",
        mime_type="text/plain",
        disposition="inline",
        charset="utf-8",
        content_id="plain1",
        headers={"X-Custom": "value"},
    )

    assert attachment.file_name == "file.txt"
    assert attachment.contents == "CONTENTS"
    assert attachment.mime_type == "text/plain"
    assert attachment.disposition == "inline"
    assert attachment.charset == "utf-8"
    assert attachment.content_id == "plain1"
    assert attachment.headers == {
        "Content-ID": "<plain1>",
        "X-Attachment-ID": "plain1",
        "X-Custom": "value",
    }


def test_build():
    attachment = Attachment(file_name="file.txt", contents="CONTENTS", mime_type="text/plain")
    part = attachment.build()
    assert isinstance(part, MIMEBase)


def test_as_string():
    attachment = Attachment(
        file_name="file.txt",
        contents="CONTENTS",
        mime_type="text/plain",
        disposition="inline",
        charset="utf-8",
        content_id="plain1",
        headers={"X-Custom": "value"},
    )
    expected = (
        "MIME-Version: 1.0\n"
        'Content-Disposition: inline; filename="file.txt"\n'
        'Content-Type: text/plain; charset="utf-8"\n'
        "Content-Transfer-Encoding: base64\n"
        "X-Custom: value\n"
        "Content-ID: <plain1>\n"
        "X-Attachment-ID: plain1\n"
        "\n"
        "Q09OVEVOVFM=\n"
    )
    assert attachment.as_string() == str(attachment)
    assert attachment.as_string() == expected
