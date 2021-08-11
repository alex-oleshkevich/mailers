from __future__ import annotations

import abc
import aiofiles
import aiosmtplib
import datetime
import os
import ssl
import sys
import typing as t
from typing import Any, List, Optional, Union

from .config import EmailURL
from .exceptions import NotRegisteredTransportError
from .message import EmailMessage


class Transport(t.Protocol):  # pragma: nocover
    async def send(self, message: EmailMessage) -> None:
        ...

    @classmethod
    def from_url(cls, url: t.Union[str, EmailURL]) -> t.Optional[Transport]:
        ...


class BaseTransport(abc.ABC):  # pragma: nocover
    @abc.abstractmethod
    async def send(self, message: EmailMessage) -> None:
        raise NotImplementedError()

    @classmethod
    def from_url(cls, url: t.Union[str, EmailURL]) -> t.Optional[Transport]:
        return None


class FileTransport(BaseTransport):
    def __init__(self, directory: str):
        if directory is None or directory == "":
            raise ValueError('Argument "path" of FileTransport cannot be None.')

        self._directory = directory

    async def send(self, message: EmailMessage) -> None:
        file_name = "message_%s.eml" % datetime.datetime.today().isoformat()
        output_file = os.path.join(self._directory, file_name)
        async with aiofiles.open(output_file, "wb") as stream:
            await stream.write(message.as_string().encode("utf8"))

    @classmethod
    def from_url(cls, url: Union[str, EmailURL]) -> FileTransport:
        url = EmailURL(url)
        return cls(url.path)


class NullTransport(BaseTransport):
    async def send(self, message: EmailMessage) -> None:
        pass

    @classmethod
    def from_url(cls, *args: Any) -> NullTransport:
        return cls()


class InMemoryTransport(BaseTransport):
    @property
    def mailbox(self) -> List[EmailMessage]:
        return self._storage

    def __init__(self, storage: List[EmailMessage]):
        self._storage = storage

    async def send(self, message: EmailMessage) -> None:
        self._storage.append(message)

    @classmethod
    def from_url(cls, *args: Any) -> InMemoryTransport:
        mailbox: List[EmailMessage] = []
        return cls(mailbox)


class StreamTransport(BaseTransport):
    def __init__(self, output: Any):
        self._output = output

    async def send(self, message: EmailMessage) -> None:
        self._output.write(str(message))


class ConsoleTransport(StreamTransport):
    def __init__(self) -> None:
        super().__init__(sys.stdout)


class SMTPTransport(BaseTransport):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 25,
        user: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: Optional[bool] = None,
        timeout: int = 10,
        key_file: Optional[str] = None,
        cert_file: Optional[str] = None,
    ):
        self._host = host
        self._user = user
        self._port = port
        self._password = password
        self._use_tls = use_tls
        self._timeout = timeout
        self._key_file = key_file
        self._cert_file = cert_file

    async def send(self, message: EmailMessage) -> None:
        context = ssl.create_default_context()
        client = aiosmtplib.SMTP(
            hostname=self._host,
            port=self._port,
            use_tls=self._use_tls,
            username=self._user,
            password=self._password,
            timeout=self._timeout,
            tls_context=context,
            client_key=self._key_file,
            client_cert=self._cert_file,
        )
        async with client:
            await client.send_message(message.build_message())

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


class GMailTransport(SMTPTransport):
    def __init__(self, user: Optional[str], password: Optional[str], timeout: int = 10):
        super().__init__(
            host="smtp.gmail.com",
            port=465,
            user=user,
            password=password,
            use_tls=True,
            timeout=timeout,
        )

    @classmethod
    def from_url(cls, url: Union[str, EmailURL]) -> GMailTransport:
        url = EmailURL(str(url) + "@default")
        return cls(url.username, url.password)


class MailgunTransport(SMTPTransport):
    def __init__(self, user: Optional[str], password: Optional[str], timeout: int = 10):
        super().__init__(
            host="smtp.mailgun.org",
            port=465,
            user=user,
            password=password,
            use_tls=True,
            timeout=timeout,
        )

    @classmethod
    def from_url(cls, url: Union[str, EmailURL]) -> MailgunTransport:
        url = EmailURL(str(url) + "@default")
        return cls(url.username, url.password)


_protocol_handlers: t.Dict[str, t.Type[Transport]] = {
    'smtp': SMTPTransport,
    'file': FileTransport,
    'null': NullTransport,
    'memory': InMemoryTransport,
    'console': ConsoleTransport,
    'gmail': GMailTransport,
    'mailgun': MailgunTransport,
}


def create_from_url(url: t.Union[str, EmailURL]) -> Transport:
    """Create a transport instance from URL configuration."""

    url = EmailURL(url)
    if url.transport not in _protocol_handlers:
        raise NotRegisteredTransportError(f'No transport found with scheme "{url.transport}".')

    klass = _protocol_handlers[url.transport]
    instance = klass.from_url(url)
    if instance is None:
        instance = klass()
    return instance


def add_protocol_handler(protocol: str, transport: t.Type[Transport]) -> None:
    """Register a new protocol handler.

    Example:
        import mailers

        class MyTransport:
            async def send(self, email_message: EmailMessage) -> None: ...

        mailers.add_transport('myproto', MyTransport)

        # then you can use it like this:
        mailers.add_mailer('myproto://')
    """
    _protocol_handlers[protocol] = transport
