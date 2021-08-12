from .config import EmailURL
from .exceptions import MailersError
from .factories import add_protocol_handler, create_mailer, create_transport_from_url
from .mailer import Mailer
from .message import Attachment, EmailMessage
from .plugins import BasePlugin, Plugin
from .transports import (
    BaseTransport,
    FileTransport,
    InMemoryTransport,
    NullTransport,
    SMTPTransport,
    StreamTransport,
    Transport,
)

__all__ = [
    "Transport",
    "InMemoryTransport",
    "SMTPTransport",
    "NullTransport",
    "FileTransport",
    "BaseTransport",
    "StreamTransport",
    "MailersError",
    "EmailMessage",
    "Attachment",
    "EmailURL",
    "Plugin",
    "BasePlugin",
    "Mailer",
    "create_mailer",
    "create_transport_from_url",
    "add_protocol_handler",
]
