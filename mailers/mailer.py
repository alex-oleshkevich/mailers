from typing import Any, Dict, Union

from .config import EmailURL
from .exceptions import NotRegisteredMailer
from .message import EmailMessage
from .transports import BaseTransport, Transports


class Mailer:
    def __init__(self, url_or_transport: Union[str, EmailURL, BaseTransport]) -> None:
        if isinstance(url_or_transport, (str, EmailURL)):
            url_or_transport = Transports.from_url(url_or_transport)

        self._transport = url_or_transport

    async def send(self, message: EmailMessage) -> Any:
        return await self._transport.send(message)


class MailerRegistry:
    def __init__(self) -> None:
        self._mailers: Dict[str, Mailer] = {}

    def add(self, name: str, mailer: Union[str, EmailURL, Mailer]) -> None:
        if isinstance(mailer, (str, EmailURL)):
            mailer = Mailer(mailer)
        self._mailers[name] = mailer

    def get(self, name: str) -> Mailer:
        if name not in self:
            raise NotRegisteredMailer(f'Mailer with name "{name}" not registered.')

        return self._mailers[name]

    def __contains__(self, item: str) -> bool:
        return item in self._mailers


registry = MailerRegistry()
