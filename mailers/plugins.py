import typing as t

from .message import EmailMessage


class Plugin(t.Protocol):
    async def on_before_send(self, message: EmailMessage) -> None:
        """Called right before sending the message."""

    async def on_after_send(self, message: EmailMessage) -> None:
        """Called right after sending the message."""
