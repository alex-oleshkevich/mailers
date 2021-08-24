from __future__ import annotations

import abc
import aiosmtplib
import anyio as anyio
import datetime
import os
import sys
import typing as t
from email.message import Message
from typing import Any, List, Union

from .config import EmailURL
from .result import SentMessage


class Transport(abc.ABC):  # pragma: nocover
    @abc.abstractmethod
    async def send(self, message: Message) -> SentMessage:
        raise NotImplementedError()

    @classmethod
    def from_url(cls, url: t.Union[str, EmailURL]) -> t.Optional[Transport]:
        return None


class FileTransport(Transport):
    def __init__(self, directory: str):
        if directory is None or directory == "":
            raise ValueError('Argument "path" of FileTransport cannot be None.')

        self._directory = directory

    async def send(self, message: Message) -> SentMessage:
        file_name = "message_%s.eml" % datetime.datetime.today().isoformat()
        output_file = os.path.join(self._directory, file_name)
        async with await anyio.open_file(output_file, 'wb') as f:
            await f.write(message.as_bytes())
        return SentMessage(True, message, self)

    @classmethod
    def from_url(cls, url: Union[str, EmailURL]) -> FileTransport:
        url = EmailURL(url)
        return cls(url.path)


class NullTransport(Transport):
    async def send(self, message: Message) -> SentMessage:
        return SentMessage(True, message, self)

    @classmethod
    def from_url(cls, *args: Any) -> NullTransport:
        return cls()


class InMemoryTransport(Transport):
    @property
    def mailbox(self) -> List[Message]:
        return self._storage

    def __init__(self, storage: List[Message]):
        self._storage = storage

    async def send(self, message: Message) -> SentMessage:
        self._storage.append(message)
        return SentMessage(True, message, self)

    @classmethod
    def from_url(cls, *args: Any) -> InMemoryTransport:
        mailbox: List[Message] = []
        return cls(mailbox)


class StreamTransport(Transport):
    def __init__(self, output: t.IO):
        self._output = output

    async def send(self, message: Message) -> SentMessage:
        self._output.write(str(message))
        return SentMessage(True, message, self)


class ConsoleTransport(StreamTransport):
    def __init__(self, stream: t.Literal['stdout', 'stderr'] = 'stderr') -> None:
        assert stream in ['stdout', 'stderr'], 'Unsupported console stream type: %s.' % stream
        output = None
        if stream == 'stderr':
            output = sys.stderr
        elif stream == 'stdout':
            output = sys.stdout
        super().__init__(output)

    @classmethod
    def from_url(cls, url: t.Union[str, EmailURL]) -> t.Optional[Transport]:
        url = EmailURL(url)
        stream = url.options.get('stream')
        assert stream in ['stdout', 'stderr'], 'Unsupported console stream type: %s.' % stream
        return ConsoleTransport(stream)


class SMTPTransport(Transport):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 25,
        user: str = None,
        password: str = None,
        use_tls: bool = None,
        timeout: int = 10,
        key_file: str = None,
        cert_file: str = None,
    ):
        self._host = host
        self._user = user
        self._port = port
        self._password = password
        self._use_tls = use_tls or False
        self._timeout = timeout
        self._key_file = key_file
        self._cert_file = cert_file

    async def send(self, message: Message) -> SentMessage:
        try:
            await aiosmtplib.send(
                message,
                hostname=self._host,
                port=self._port,
                use_tls=self._use_tls,
                username=self._user,
                password=self._password,
                timeout=self._timeout,
                client_key=self._key_file,
                client_cert=self._cert_file,
            )
        except aiosmtplib.errors.SMTPException as ex:  # pragma: no cover
            return SentMessage(False, message, self, ex.message)
        return SentMessage(True, message, self)

    @classmethod
    def from_url(cls, url: Union[str, EmailURL]) -> SMTPTransport:
        url = EmailURL(url)

        def _cast_to_bool(value: str) -> bool:
            return value.lower() in ["yes", "1", "on", "true"]

        timeout = url.options.get("timeout", None)
        if timeout:
            timeout = int(timeout)

        use_tls = _cast_to_bool(url.options.get("use_tls", ""))
        key_file = url.options.get("key_file", None)
        cert_file = url.options.get("cert_file", None)

        return cls(
            url.hostname or "localhost",
            url.port or 25,
            url.username,
            url.password,
            use_tls=use_tls,
            timeout=timeout,
            key_file=key_file,
            cert_file=cert_file,
        )
