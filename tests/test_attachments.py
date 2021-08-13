from mailers.message import Attachment


def test_attachment():
    attachment = Attachment(
        file_name="file.txt",
        content="CONTENTS",
        mime_type="text/plain",
        disposition="inline",
        charset="utf-8",
        content_id="plain1",
        headers={"X-Custom": "value"},
    )

    assert attachment.file_name == "file.txt"
    assert attachment.content == b"CONTENTS"
    assert attachment.mime_type == "text/plain"
    assert attachment.disposition == "inline"
    assert attachment.charset == "utf-8"
    assert attachment.content_id == "plain1"
    assert attachment.headers == {
        "Content-ID": "<plain1>",
        "X-Attachment-ID": "plain1",
        "X-Custom": "value",
    }
