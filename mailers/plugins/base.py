import typing
from email.message import EmailMessage

from mailers.message import Email


class Plugin(typing.Protocol):  # pragma: no cover
    def process_email(self, email: Email) -> Email:
        """Mailer calls it before sending."""

    async def on_before_send(self, message: EmailMessage) -> None:
        """Called right before sending the message."""

    async def on_after_send(self, message: EmailMessage) -> None:
        """Called right after sending the message."""


class BasePlugin:  # pragma: no cover
    def process_email(self, email: Email) -> Email:
        """Mailer calls it before sending."""
        return email

    async def on_before_send(self, message: EmailMessage) -> None:
        """Called right before sending the message."""

    async def on_after_send(self, message: EmailMessage) -> None:
        """Called right after sending the message."""
