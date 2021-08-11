import typing as t

from .config import EmailURL
from .exceptions import MailerIsRegisteredError, NotRegisteredMailer
from .message import EmailMessage
from .transports import Transport, create_from_url


class Mailer:
    """A facade for sending mails."""

    def __init__(self, transport: Transport) -> None:
        self.transport = transport

    async def send(self, message: EmailMessage) -> t.Any:
        return await self.transport.send(message)


_mailers: t.Dict[str, Mailer] = {}


def add_mailer(
    url: t.Union[str, EmailURL] = None,
    *,
    mailer: Mailer = None,
    transport: Transport = None,
    name: str = 'default',
) -> None:
    """Add a new mailer. Later you can obtain this mailer using it's name.
    If the name is taken an exception will be raised."""

    if url:
        mailer = Mailer(create_from_url(url))
    elif mailer:
        pass
    elif transport:
        mailer = Mailer(transport)
    else:
        raise ValueError('Either url, or mailer, or transport arguments required.')

    if name in _mailers:
        raise MailerIsRegisteredError('Mailer with name "%s" is already registered.' % name)

    _mailers[name] = mailer


def remove_mailer(name: str) -> None:
    """Remove previously registered mailer."""
    _mailers.pop(name, None)


def clear_mailers() -> None:
    """Remove all mailers."""
    _mailers.clear()


def get_mailer(name: str = 'default') -> Mailer:
    """Get a registered mailer.
    If mailer cannot be found an NotRegisteredMailer will be raised.
    You can register mailer with `add_mailer` function."""

    try:
        return _mailers[name]
    except KeyError:
        raise NotRegisteredMailer('Mailer with name "%s" is not registered.' % name) from None
