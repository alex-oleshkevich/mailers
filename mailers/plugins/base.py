import typing as t
from email.message import Message

from mailers.message import Email
from mailers.result import SentMessages


class Plugin(t.Protocol):  # pragma: no cover
    def process_email(self, email: Email) -> Email:
        """Mailer calls it before sending."""

    async def on_before_send(self, message: Message) -> None:
        """Called right before sending the message."""

    async def on_after_send(self, message: Message, sent_messages: SentMessages) -> None:
        """Called right after sending the message."""

    async def on_send_error(self, message: Message, sent_messages: SentMessages) -> None:
        """Called if no transport has delivered a message."""


class BasePlugin:  # pragma: no cover
    def process_email(self, email: Email) -> Email:
        """Mailer calls it before sending."""

    async def on_before_send(self, message: Message) -> None:
        """Called right before sending the message."""

    async def on_after_send(self, message: Message, sent_messages: SentMessages) -> None:
        """Called right after sending the message."""

    async def on_send_error(self, message: Message, sent_messages: SentMessages) -> None:
        """Called if no transport has delivered a message."""
