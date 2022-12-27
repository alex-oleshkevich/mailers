from __future__ import annotations

from dataclasses import dataclass

import anyio as anyio
import email
import email.encoders
import email.utils
import mimetypes
import os
import random
import string
import typing
from email.headerregistry import Address
from email.message import EmailMessage, Message
from email.mime.base import MIMEBase
from email.policy import EmailPolicy

from mailers.exceptions import InvalidBodyError

if typing.TYPE_CHECKING:  # pragma: no cover
    from _typeshed import OpenBinaryMode, OpenTextMode

Recipients = typing.Union[str, Address, typing.Iterable[typing.Union[str, Address]]]


def _randon_string(length: int) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def _string_to_address(value: typing.Union[str, Address]) -> Address:
    if isinstance(value, Address):
        return value

    if "<" in value:
        start_pos = value.index("<")
        end_pos = value.index(">")
        display_name = value[0 : start_pos - 1]
        email = value[start_pos + 1 : end_pos]
        return Address(display_name=display_name, addr_spec=email)
    return Address(addr_spec=value)


def _to_addresses(recipients: typing.Optional[Recipients] = None) -> typing.List[Address]:
    if recipients is None:
        return []
    if isinstance(recipients, str):
        return [_string_to_address(recipients)]
    if isinstance(recipients, Address):
        return [recipients]
    return list(map(_string_to_address, recipients))


AddressType = typing.Union[typing.Union[str, Address], typing.Iterable[typing.Union[str, Address]]]


class AddressList:
    def __init__(self, addresses: typing.Optional[AddressType] = None) -> None:
        self._addresses: typing.List[Address] = []
        if addresses is not None:
            if isinstance(addresses, (str, Address)):
                addresses = [addresses]
            self.set(*addresses)

    @property
    def empty(self) -> bool:
        return len(self) == 0

    @property
    def first(self) -> typing.Optional[Address]:
        try:
            return self._addresses[0]
        except IndexError:
            return None

    def set(self, *address: typing.Union[str, Address]) -> None:
        self._addresses = _to_addresses(address)

    def add(self, *address: typing.Union[str, Address]) -> None:
        self._addresses.extend(_to_addresses(address))

    def clear(self) -> None:
        self._addresses = []

    def __str__(self) -> str:
        return ", ".join(map(str, self._addresses))

    def __repr__(self) -> str:  # pragma: no cover
        return f'<AddressList: addresses="{self}">'

    def __iter__(self) -> typing.Iterator[Address]:
        return iter(self._addresses)

    def __len__(self) -> int:
        return len(self._addresses)

    def __bool__(self) -> bool:
        return not self.empty

    def __eq__(self, other: object) -> bool:
        return str(self) == str(other)

    def __get__(self, obj: object, type: typing.Optional[type] = None) -> AddressList:
        return self

    def __set__(self, obj: object, value: typing.Optional[Recipients]) -> None:
        self._addresses = _to_addresses(value)


def _sanitize_input(
    path: typing.Union[str, os.PathLike],
    name: typing.Optional[str] = None,
    content_type: typing.Optional[str] = None,
) -> typing.Tuple[str, str]:
    name = name or os.path.basename(path)
    content_type = content_type or mimetypes.guess_type(path)[0] or "application/octet-stream"
    return name, content_type


@dataclass
class Attachment:
    name: typing.Optional[str] = None
    content_type: typing.Optional[str] = None
    body: typing.Optional[typing.Union[str, bytes]] = None
    path: typing.Optional[str] = None
    inline: typing.Optional[bool] = False
    part: typing.Optional[Message] = None

    @property
    def mime_type_parts(self) -> typing.Tuple[str, str]:
        if self.content_type:
            main_type, sub_type = self.content_type.split("/")
            return main_type, sub_type
        return "application", "octet-stream"


class Email:
    to = AddressList()
    cc = AddressList()
    bcc = AddressList()
    reply_to = AddressList()
    from_address = AddressList()

    def __init__(
        self,
        to: typing.Optional[Recipients] = None,
        subject: typing.Optional[str] = None,
        text: typing.Optional[str] = None,
        html: typing.Optional[str] = None,
        from_address: typing.Optional[Recipients] = None,
        cc: typing.Optional[Recipients] = None,
        bcc: typing.Optional[Recipients] = None,
        reply_to: typing.Optional[Recipients] = None,
        headers: typing.Optional[dict] = None,
        sender: typing.Optional[str] = None,
        return_path: typing.Optional[str] = None,
        text_charset: str = "utf-8",
        html_charset: str = "utf-8",
        boundary: typing.Optional[str] = None,
        message_id: typing.Optional[str] = None,
    ) -> None:
        self._sender: typing.Optional[Address] = None
        self._attachments: typing.List[Attachment] = []

        self.to = to
        self.cc = cc
        self.bcc = bcc
        self.reply_to = reply_to
        self.from_address = from_address

        if sender:
            self.sender = _string_to_address(sender)
        self.return_path = return_path
        self.subject = subject
        self.html = html
        self.html_charset = html_charset
        self.text = text
        self.text_charset = text_charset
        self.boundary = boundary
        self.headers = headers or {}
        self.id = message_id

        self.date = email.utils.localtime()

    @property
    def sender(self) -> typing.Optional[Address]:
        return self._sender

    @sender.setter
    def sender(self, value: typing.Optional[typing.Union[str, Address]]) -> None:
        self._sender = _string_to_address(value) if value else None

    def attach(
        self,
        body: typing.Union[str, bytes],
        name: typing.Optional[str] = None,
        content_type: typing.Optional[str] = None,
    ) -> None:
        if isinstance(body, str):
            body = body.encode()
        self._attachments.append(Attachment(body=body, name=name, content_type=content_type))

    async def attach_from_path(
        self,
        path: typing.Union[str, os.PathLike],
        name: typing.Optional[str] = None,
        content_type: typing.Optional[str] = None,
        mode: typing.Union["OpenBinaryMode", "OpenTextMode"] = "r",
    ) -> None:
        name, content_type = _sanitize_input(path, name, content_type)
        async with await anyio.open_file(path, mode=mode) as f:
            self.attach(await f.read(), name, content_type)

    def attach_from_path_sync(
        self,
        path: typing.Union[str, os.PathLike],
        name: typing.Optional[str] = None,
        content_type: typing.Optional[str] = None,
        mode: str = "r",
    ) -> None:
        name, content_type = _sanitize_input(path, name, content_type)
        with open(path, mode) as f:
            self.attach(f.read(), name, content_type)

    def embed(
        self,
        body: typing.Union[str, bytes],
        name: typing.Optional[str] = None,
        content_type: typing.Optional[str] = None,
    ) -> None:
        self._attachments.append(Attachment(body=body, name=name, content_type=content_type, inline=True))

    async def embed_from_path(
        self,
        path: typing.Union[str, os.PathLike],
        name: typing.Optional[str] = None,
        content_type: typing.Optional[str] = None,
        mode: typing.Union["OpenTextMode", "OpenBinaryMode"] = "r",
    ) -> None:
        name, content_type = _sanitize_input(path, name, content_type)
        async with await anyio.open_file(path, mode) as f:
            self.embed(await f.read(), name, content_type)

    def embed_from_path_sync(
        self,
        path: typing.Union[str, os.PathLike],
        name: typing.Optional[str] = None,
        content_type: typing.Optional[str] = None,
        mode: str = "r",
    ) -> None:
        name, content_type = _sanitize_input(path, name, content_type)
        with open(path, mode) as f:
            self.embed(f.read(), name, content_type)

    def attach_part(self, part: MIMEBase) -> None:
        self._attachments.append(Attachment(part=part))

    def validate(self) -> None:
        if all([self.text is None, self.html is None, not self._attachments]):
            raise InvalidBodyError("Email message must have a text, or HTML part or attachments.")

    def build(self) -> EmailMessage:  # noqa: C901
        self.validate()

        if not self.id:
            domain = ""
            if self.sender:
                domain = self.sender.domain
            if self.from_address:
                first_address = self.from_address.first
                if first_address:
                    domain = first_address.domain
                else:  # pragma: no cover
                    raise ValueError("Could not read sender domain from From header.")
            self.id = email.utils.make_msgid(domain=domain)

        headers = {
            "From": self.from_address,
            "To": self.to,
            "Cc": self.cc,
            "Bcc": self.bcc,
            "Reply-To": self.reply_to,
            "Return-Path": self.return_path,
            "Sender": self.sender,
            "Message-ID": self.id,
            "Date": self.date,
            "Subject": self.subject,
            **self.headers,
        }
        inline_attachments = [a for a in self._attachments if a.inline and not a.part]
        attachments = [a for a in self._attachments if not a.inline and not a.part]
        extra_parts = [a for a in self._attachments if a.part]

        mime_message = EmailMessage(policy=EmailPolicy())

        for header_name, header_value in headers.items():
            if not header_value:  # ignore empty headers
                continue
            mime_message[header_name] = header_value

        # this is text only message
        if self.text and not any([self.html, inline_attachments, attachments]):
            mime_message.set_content(self.text, subtype="plain", charset=self.text_charset)
            return mime_message

        # this is HTML only message
        if self.html and not any([self.text, inline_attachments, attachments]):
            mime_message.set_content(self.html, subtype="html", charset=self.html_charset)
            return mime_message

        if self.text:
            mime_message.set_content(self.text, subtype="plain", charset=self.text_charset)

        if self.html:
            domain = str(self.id).split("@").pop()
            mime_message.add_alternative(self.html, subtype="html", charset=self.html_charset)
            html_part = mime_message.get_payload(1 if self.text else 0)
            for inline_attachment in inline_attachments:
                main_type, sub_type = inline_attachment.mime_type_parts
                cid = inline_attachment.name or _randon_string(16) + "@" + domain

                kwargs = {}
                if isinstance(inline_attachment.body, str):
                    kwargs["subtype"] = "plain" if sub_type not in ["html", "plain"] else sub_type
                else:
                    kwargs["maintype"] = main_type
                    kwargs["subtype"] = sub_type

                html_part.add_related(
                    inline_attachment.body,
                    disposition="inline",
                    filename=inline_attachment.name,
                    cid=cid,
                    headers=[
                        "Content-ID: <%s>" % cid,
                        "X-Attachment-ID: %s" % cid,
                    ],
                    **kwargs,
                )

        # this is attachments only message
        for attachment in attachments:
            main_type, sub_type = attachment.mime_type_parts
            mime_message.add_attachment(
                attachment.body,
                maintype=main_type,
                subtype=sub_type,
                disposition="attachment",
                filename=attachment.name,
            )

        for extra_part in extra_parts:
            if extra_part.part:
                mime_message.attach(extra_part.part)

        return mime_message

    def __str__(self) -> str:  # pragma: no cover
        return str(self.build())
