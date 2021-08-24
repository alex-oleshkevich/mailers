import pytest
from email.message import Message
from unittest import mock

from mailers import Mailer, SentMessage, Transport, create_mailer
from mailers.message import Email
from mailers.plugins import BasePlugin
from mailers.result import SentMessages


class _DummyPlugin(BasePlugin):
    on_before_send_called = mock.MagicMock()
    on_send_error_called = mock.MagicMock()
    on_after_send_called = mock.MagicMock()

    async def on_before_send(self, message: Message) -> None:
        self.on_before_send_called(message)

    async def on_after_send(self, message: Message, sent_messages: SentMessages) -> None:
        self.on_after_send_called(message)

    async def on_send_error(self, message: Message, sent_messages: SentMessages) -> None:
        self.on_send_error_called(message)


class _FailingTransport(Transport):
    async def send(self, message: Message) -> SentMessage:
        return SentMessage(False, message, self)


@pytest.mark.asyncio
async def test_calls_before_send():
    plugin = _DummyPlugin()
    message = Email(to='root@localhost', from_address='reply@localhost', text='Test message.')
    mailer = create_mailer('null://', plugins=[plugin])
    await mailer.send(message)
    plugin.on_before_send_called.assert_called_once()
    plugin.on_after_send_called.assert_called_once()


@pytest.mark.asyncio
async def test_calls_send_error():
    plugin = _DummyPlugin()
    message = Email(to='root@localhost', from_address='reply@localhost', text='Test message.')
    mailer = Mailer(_FailingTransport(), plugins=[_DummyPlugin()])
    await mailer.send(message)
    plugin.on_send_error_called.assert_called_once()
