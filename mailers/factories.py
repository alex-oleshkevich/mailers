import typing as t

from .config import EmailURL
from .exceptions import NotRegisteredTransportError
from .mailer import Mailer
from .plugins import Plugin
from .transports import ConsoleTransport, FileTransport, InMemoryTransport, NullTransport, SMTPTransport, Transport

_protocol_handlers: t.Dict[str, t.Type[Transport]] = {
    'smtp': SMTPTransport,
    'file': FileTransport,
    'null': NullTransport,
    'memory': InMemoryTransport,
    'console': ConsoleTransport,
}


def create_transport_from_url(url: t.Union[str, EmailURL]) -> Transport:
    """Create a transport instance from URL configuration."""

    url = EmailURL(url)
    if url.transport not in _protocol_handlers:
        raise NotRegisteredTransportError(f'No transport found with scheme "{url.transport}".')

    klass = _protocol_handlers[url.transport]
    instance = klass.from_url(url)
    if instance is None:
        instance = klass()
    return instance


def create_mailer(url: t.Union[str, EmailURL], plugins: t.Iterable[Plugin] = None) -> Mailer:
    """Create mailer from URL configuration."""
    transport = create_transport_from_url(url)
    return Mailer(transport, plugins=plugins)


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
