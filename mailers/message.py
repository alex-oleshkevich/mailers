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
from builtins import AttributeError
from email.encoders import encode_base64
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .exceptions import BadHeaderError


def _forbid_new_lines(value: t.Optional[str]) -> t.Optional[str]:
    if value is not None and ("\n" in value or "\r" in value):
        raise BadHeaderError(f'Header value "{value}" contains new line characters.')
    return value


def _make_list(value: t.Union[str, None, t.Iterable[str]]) -> t.List[str]:
    if value is None:
        value = []

    if isinstance(value, str):
        value = [value]
    return list(value)


class Attachment:
    def __init__(
        self,
        file_name: str,
        content: t.Union[str, bytes],
        mime_type: t.Optional[str] = "application/octet-stream",
        disposition: str = "attachment",
        charset: str = None,
        content_id: str = None,
        headers: t.Dict[str, str] = None,
    ):
        self._content: bytes = b''

        self.mime_type = mime_type or "application/octet-stream"
        self.disposition = disposition
        self.charset = charset
        self.headers = headers or {}
        self.file_name = file_name
        self.content_id = content_id
        self.content = content  # type: ignore
        if content_id:
            self.headers["Content-ID"] = f"<{content_id}>"
            self.headers["X-Attachment-ID"] = content_id

    @property
    def content(self) -> bytes:
        return self._content

    @content.setter
    def content(self, value: t.Union[str, bytes]) -> None:
        self._content = value.encode() if isinstance(value, str) else value

    def __repr__(self) -> str:  # pragma: no cover
        return '<Attachment file_name="%s" mime-type="%s" charset="%s">' % (
            self.file_name,
            self.mime_type,
            self.charset,
        )


class EmailMessage:
    def __init__(
        self,
        *,
        from_address: str = None,
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
        self._to: t.List[str] = []
        self._cc: t.List[str] = []
        self._bcc: t.List[str] = []
        self._reply_to: t.List[str] = []

        self.subject = subject
        self.from_address = from_address
        self.text_body = text_body
        self.html_body = html_body
        self.boundary = boundary
        self.charset = charset
        self.to = to  # type: ignore
        self.cc = cc  # type: ignore
        self.bcc = bcc  # type: ignore
        self.reply_to = reply_to  # type: ignore
        self.date = date or datetime.datetime.today()
        self.headers = headers or {}
        self.attachments = list(attachments or [])
        self.parts = list(parts or [])

        self.id = ''

    @property
    def to(self) -> list[str]:
        return self._to

    @to.setter
    def to(self, value: t.Union[str, None, t.Iterable[str]]) -> None:
        self._to = _make_list(value)

    @property
    def cc(self) -> list[str]:
        return self._cc

    @cc.setter
    def cc(self, value: t.Union[str, None, t.Iterable[str]]) -> None:
        self._cc = _make_list(value)

    @property
    def bcc(self) -> list[str]:
        return self._bcc

    @bcc.setter
    def bcc(self, value: t.Union[str, None, t.Iterable[str]]) -> None:
        self._bcc = _make_list(value)

    @property
    def reply_to(self) -> list[str]:
        return self._reply_to

    @reply_to.setter
    def reply_to(self, value: t.Union[str, None, t.Iterable[str]]) -> None:
        self._reply_to = _make_list(value)

    def add_mime_part(self, part: MIMEBase) -> None:
        self.parts.append(part)

    def add_attachment(self, attachment: Attachment) -> None:
        self.attachments.append(attachment)

    def attach_content(
        self,
        file_name: str,
        content: t.Union[str, bytes],
        mime_type: t.Optional[str] = 'application/octet-stream',
        inline: bool = False,
        content_id: str = None,
        charset: str = None,
        headers: dict = None,
    ) -> None:
        """Attach arbitrary content."""
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
        mime_type: str = None,
        inline: bool = False,
        content_id: str = None,
        charset: str = None,
        headers: dict = None,
    ) -> None:
        """Read and attach file contents."""
        path = str(path)
        file_name = file_name or os.path.basename(path)
        if mime_type is None:
            guessed = mimetypes.guess_type(file_name)
            if guessed:
                mime_type = guessed[0]
        async with aiofiles.open(path, 'rb') as f:
            self.attach_content(
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

        assert self.to or self.bcc, 'Either value for "to" or "bcc" required.'
        assert self.from_address, 'A sender address (from_address) is required.'

        if not self.id:
            domain = self.from_address.split('@')[-1]
            self.id = email.utils.make_msgid(domain=domain)

        message: Message
        if any([self.parts, self.attachments, self.html_body, self.parts]):
            message = MIMEMultipart('alternative', boundary=self.boundary)

            if self.text_body:
                message.attach(MIMEText(self.text_body, 'plain', _charset=self.charset))

            if self.html_body:
                # the email client will try to render the last part first
                message.attach(MIMEText(self.html_body, 'html', _charset=self.charset))

            for part in self.parts:
                message.attach(part)

            for attachment in self.attachments:
                try:
                    main_type, sub_type = attachment.mime_type.split('/')
                except AttributeError:
                    main_type, sub_type = 'application', 'octet-stream'
                part = MIMEBase(main_type, sub_type, _charset=attachment.charset)
                part.set_payload(attachment.content)
                part.set_charset(attachment.charset)
                part.add_header('Content-Disposition', attachment.disposition, filename=attachment.file_name)

                for header_name, header_value in attachment.headers.items():
                    part.add_header(header_name, header_value)

                if main_type != 'text':
                    encode_base64(part)
                message.attach(part)
        else:
            message = MIMEText(self.text_body or '', 'plain', _charset=self.charset)

        date = time.mktime(self.date.timetuple())
        headers = {
            'From': self.from_address,
            'To': ', '.join(self.to),
            'Cc': ', '.join(self.cc),
            'Bcc': ', '.join(self.bcc),
            'Reply-to': ', '.join(self.reply_to),
            'Date': email.utils.formatdate(date),
            'Subject': self.subject,
            'Message-ID': self.id,
            **self.headers,
        }
        for name, value in headers.items():
            if value := _forbid_new_lines(value):
                message.add_header(name, value)

        return message

    def as_bytes(self) -> bytes:
        return self.get_message().as_bytes()

    def as_string(self) -> str:
        return self.get_message().as_string()

    def get_message(self) -> Message:
        return self.to_mime_message()

    def __str__(self) -> str:
        return self.as_string()
