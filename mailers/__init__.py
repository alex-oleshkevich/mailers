from typing import Mapping, Optional, Union

from .config import EmailURL
from .exceptions import MailersError
from .mailer import Mailer, MailerRegistry, registry
from .message import Attachment, EmailMessage
from .shortcuts import get_mailer, send_mail
from .transports import (
    BaseTransport,
    FileTransport,
    GMailTransport,
    InMemoryTransport,
    MailgunTransport,
    NullTransport,
    SMTPTransport,
    StreamTransport,
    Transports,
)

__all__ = [
    "Transports",
    "InMemoryTransport",
    "SMTPTransport",
    "NullTransport",
    "FileTransport",
    "BaseTransport",
    "StreamTransport",
    "GMailTransport",
    "MailgunTransport",
    "MailersError",
    "EmailMessage",
    "Attachment",
    "EmailURL",
    "Mailer",
    "MailerRegistry",
    "registry",
    "send_mail",
    "get_mailer",
]

__version__ = "0.0.2"


def configure(
    mailers: Mapping[str, Union[str, EmailURL, Mailer]],
    transports: Optional[Mapping[str, str]] = None,
) -> None:
    for name, mailer in mailers.items():
        registry.add(name, mailer)

    if transports is not None:
        Transports.bind_urls(transports)
