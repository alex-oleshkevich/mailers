from __future__ import annotations

import aiofiles
import datetime
import email
import email.encoders
import email.utils
import mimetypes
import os
import pathlib
import time
import typing as t
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Attachment:
    def __init__(
        self,
        file_name: str,
        content: t.Union[str, bytes],
        mime_type: str = "application/octet-stream",
        disposition: str = "attachment",
        charset: str = 'utf-8',
        content_id: str = None,
        headers: t.Dict[str, str] = None,
    ):
        self.mime_type = mime_type
        self.disposition = disposition
        self.charset = charset
        self.headers = headers or {}
        self.file_name = file_name
        self.content = content.encode() if isinstance(content, str) else content
        if content_id:
            self.headers["Content-ID"] = f"<{content_id}>"
            self.headers["X-Attachment-ID"] = content_id

    def __repr__(self) -> str:
        return '<Attachment file_name="%s" mime-type="%s" charset="%s">' % (
            self.file_name,
            self.mime_type,
            self.charset,
        )


def _make_list(obj: t.Union[str, None, t.Iterable[str]]) -> list[str]:
    if obj is None:
        return []

    if isinstance(obj, str):
        return [obj]

    return list(obj)


class EmailMessage:
    def __init__(
        self,
        *,
        from_address: str,
        to: t.Union[str, t.Iterable[str]] = None,
        subject: str = None,
        text_body: str = None,
        html_body: str = None,
        cc: t.Union[str, t.Iterable[str]] = None,
        bcc: t.Union[str, t.Iterable[str]] = None,
        reply_to: t.Union[str, t.Iterable[str]] = None,
        attachments: t.Iterable[Attachment] = None,
        parts: t.Iterable[Message] = None,
        headers: t.Dict[str, str] = None,
        date: t.Optional[datetime.datetime] = None,
        boundary: t.Optional[str] = None,
        charset: t.Optional[str] = None,
    ) -> None:
        assert to or bcc, 'Either "to" or "bcc" argument required.'

        self.subject = subject
        self.from_address = from_address
        self.text = text_body
        self.html = html_body
        self.boundary = boundary
        self.charset = charset
        self.to = _make_list(to)
        self.cc = _make_list(cc)
        self.bcc = _make_list(bcc)
        self.reply_to = _make_list(reply_to)
        self.date = date or datetime.datetime.today()
        self.headers = headers or {}
        self.attachments = list(attachments or [])
        self.parts = list(parts or [])

        domain = self.from_address.split('@')[-1]
        self.id = email.utils.make_msgid(domain=domain)

    def add_part(self, part: MIMEBase) -> None:
        self.parts.append(part)

    def add_attachment(self, attachment: Attachment) -> None:
        self.attachments.append(attachment)

    def attach(
        self,
        file_name: str,
        content: t.Union[str, bytes],
        mime_type: str = 'application/octet-stream',
        inline: bool = False,
        content_id: str = None,
        charset: str = 'utf-8',
        headers: dict = None,
    ) -> None:
        self.add_attachment(
            Attachment(
                charset=charset,
                headers=headers,
                mime_type=mime_type,
                content_id=content_id,
                content=content,
                file_name=file_name,
                disposition='inline' if inline else 'attachment',
            )
        )

    async def attach_file(
        self,
        path: t.Union[str, pathlib.Path],
        file_name: str = None,
        mime_type: str = 'application/octet-stream',
        inline: bool = False,
        content_id: str = None,
        charset: str = 'utf-8',
        headers: dict = None,
    ) -> None:
        path = str(path)
        file_name = file_name or os.path.basename(path)
        if mime_type is None:
            guessed = mimetypes.guess_extension(file_name)
            if guessed:
                mime_type = guessed[0]
        async with aiofiles.open(path, 'rb') as f:
            self.attach(
                content=await f.read(),
                file_name=file_name,
                mime_type=mime_type,
                inline=inline,
                content_id=content_id,
                charset=charset,
                headers=headers,
            )

    def to_mime_message(self) -> Message:
        """Generate a MIME message.
        We will try to keep the result message as simple as possible."""
        message: Message
        if any([self.parts, self.attachments, self.html, self.parts]):
            message = MIMEMultipart('alternative', boundary=self.boundary)

            if self.text:
                message.attach(MIMEText(self.text, 'plain', _charset=self.charset))

            if self.html:
                # the email client will try to render the last part first
                message.attach(MIMEText(self.html, 'html', _charset=self.charset))

            for part in self.parts:
                message.attach(part)

            for attachment in self.attachments:
                main_type, sub_type = attachment.mime_type.split('/')
                part = MIMEBase(main_type, sub_type, _charset=attachment.charset)
                part.set_payload(attachment.content)
                part.add_header('Content-Disposition', attachment.disposition, filename=attachment.file_name)
                for header_name, header_value in attachment.headers.items():
                    part.add_header(header_name, header_value)
                message.attach(part)
        else:
            message = MIMEText(self.text or '', 'plain', _charset=self.charset)

        # add headers
        message.add_header('From', self.from_address)
        message.add_header('To', ', '.join(self.to))

        date = time.mktime(self.date.timetuple())
        message.add_header('Date', email.utils.formatdate(date))
        message.add_header('Message-ID', self.id)

        for header_name, header_value in self.headers.items():
            message.add_header(header_name, header_value)

        if self.subject:
            message.add_header('Subject', self.subject)
        if self.cc:
            message.add_header('Cc', ', '.join(self.cc))
        if self.bcc:
            message.add_header('Bcc', ', '.join(self.bcc))
        if self.reply_to:
            message.add_header('Reply-to', ', '.join(self.reply_to))

        return message

    def as_bytes(self) -> bytes:
        return self.get_message().as_bytes()

    def as_string(self) -> str:
        return self.get_message().as_string()

    def get_message(self) -> Message:
        return self.to_mime_message()

    def __str__(self) -> str:
        return self.as_string()
