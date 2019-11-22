import abc
import datetime
import os
import ssl
import sys
from typing import Any, Dict, List, Mapping, Optional, Type, Union, cast

from mailers.importer import import_from_string

from .config import EmailURL
from .exceptions import (
    DependencyNotFound,
    ImproperlyConfiguredError,
    NotRegisteredTransportError,
)
from .message import EmailMessage

try:
    import aiofiles
except ImportError:  # pragma: nocover
    aiofiles = None

try:
    import aiosmtplib
except ImportError:  # pragma: nocover
    aiosmtplib = None


class BaseTransport(abc.ABC):
    @abc.abstractmethod
    async def send(self, message: EmailMessage) -> None:  # pragma: nocover
        raise NotImplementedError()


class FileTransport(BaseTransport):
    def __init__(self, directory: str):
        if aiofiles is None:
            raise DependencyNotFound(
                '%s requires "aiofiles" library installed.' % self.__class__.__name__
            )

        if directory is None or directory == "":
            raise ImproperlyConfiguredError(
                'Argument "path" of FileTransport cannot be None.'
            )

        self._directory = directory

    async def send(self, message: EmailMessage) -> None:
        file_name = "message_%s.eml" % datetime.datetime.today().isoformat()
        output_file = os.path.join(self._directory, file_name)
        async with aiofiles.open(output_file, "wb") as stream:
            await stream.write(message.as_string().encode("utf8"))

    @classmethod
    def from_url(cls, url: Union[str, EmailURL]) -> "FileTransport":
        url = EmailURL(url)
        return cls(url.path)


class NullTransport(BaseTransport):
    async def send(self, message: EmailMessage) -> None:
        pass

    @classmethod
    def from_url(cls, *args: Any) -> "NullTransport":
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
    def from_url(cls, *args: Any) -> "InMemoryTransport":
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
        if aiosmtplib is None:
            raise DependencyNotFound(
                '%s requires "aiosmtplib" library installed.' % self.__class__.__name__
            )

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
    def from_url(cls, url: Union[str, EmailURL]) -> "SMTPTransport":
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
    def from_url(cls, url: Union[str, EmailURL]) -> "GMailTransport":
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
    def from_url(cls, url: Union[str, EmailURL]) -> "MailgunTransport":
        url = EmailURL(str(url) + "@default")
        return cls(url.username, url.password)


class Transports:
    mapping: Dict[str, Union[str, Type[BaseTransport]]] = {
        "smtp": "mailers.transports:SMTPTransport",
        "file": "mailers.transports:FileTransport",
        "null": "mailers.transports:NullTransport",
        "memory": "mailers.transports:InMemoryTransport",
        "console": "mailers.transports:ConsoleTransport",
        "gmail": "mailers.transports:GMailTransport",
        "mailgun": "mailers.transports:MailgunTransport",
    }

    @classmethod
    def bind_url(cls, protocol: str, factory: Union[str, Type[BaseTransport]]) -> None:
        cls.mapping[protocol] = factory

    @classmethod
    def bind_urls(cls, urls: Mapping[str, Union[str, Type[BaseTransport]]]) -> None:
        for protocol, factory in urls.items():
            cls.bind_url(protocol, factory)

    @classmethod
    def from_url(cls, url: Union[str, EmailURL]) -> BaseTransport:
        url = EmailURL(url)
        if url.transport not in cls.mapping:
            raise NotRegisteredTransportError(
                f'No transport found with scheme "{url.transport}".'
            )

        klass = cls.mapping[url.transport]
        if isinstance(klass, str):
            klass = import_from_string(klass)

        klass = cast(Type[BaseTransport], klass)
        factory = getattr(klass, "from_url", None)
        if factory is not None:
            return factory(url)

        return klass()
