import pytest
from unittest import mock

from mailers import EmailMessage, create_mailer
from mailers.plugins import BasePlugin


class _DummyPlugin(BasePlugin):
    on_before_send_called = mock.MagicMock()
    on_send_error_called = mock.MagicMock()
    on_after_send_called = mock.MagicMock()

    async def on_before_send(self, message: EmailMessage) -> None:
        self.on_before_send_called(message)

    async def on_after_send(self, message: EmailMessage) -> None:
        self.on_after_send_called(message)


@pytest.mark.asyncio
async def test_calls_before_send():
    plugin = _DummyPlugin()
    message = EmailMessage(to='root@localhost', from_address='reply@localhost')
    mailer = create_mailer('null://', plugins=[plugin])
    await mailer.send(message)
    plugin.on_before_send_called.assert_called_with(message)
    plugin.on_after_send_called.assert_called_with(message)