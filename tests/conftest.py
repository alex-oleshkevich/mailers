import asyncio
import pytest
import typing
from aiosmtpd import smtp
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Message as MessageHandler
from email.message import EmailMessage

from mailers import InMemoryTransport, Mailer
from mailers.message import Email


async def amain(handler: typing.Any) -> Controller:
    cont = Controller(handler, hostname="localhost", port=10025)
    cont.start()
    return cont


class RecordingHandler(MessageHandler):
    def __init__(self, mailbox: typing.List[EmailMessage]) -> None:
        self.messages = mailbox
        super().__init__()

    def handle_message(self, message: EmailMessage) -> None:
        self.messages.append(message)

    async def handle_EHLO(
        self,
        server: smtp.SMTP,
        session: smtp.Session,
        envelope: smtp.Envelope,
        hostname: str,
        responses: typing.List[str],
    ) -> typing.List[str]:
        """Advertise auth login support."""
        session.host_name = hostname  # type: ignore[assignment]
        return responses


@pytest.fixture(scope="function")
def mailbox() -> typing.List[EmailMessage]:
    return []


@pytest.fixture(scope="function")
def smtpd_handler(mailbox: typing.List[EmailMessage]) -> RecordingHandler:
    return RecordingHandler(mailbox)


@pytest.fixture(scope="function")
def smtpd_server(
    smtpd_handler: RecordingHandler, event_loop: asyncio.AbstractEventLoop
) -> typing.Generator[Controller, None, None]:
    server = event_loop.run_until_complete(amain(smtpd_handler))
    yield server
    server.stop()


@pytest.fixture
def message() -> EmailMessage:
    return Email(
        to="user@localhost",
        subject="subject",
        text="contents",
        from_address="root@localhost",
    ).build()


@pytest.fixture()
def mailer(mailbox: typing.List[EmailMessage]) -> Mailer:
    transport = InMemoryTransport(mailbox)
    return Mailer(transport)


@pytest.fixture
def email() -> Email:
    return Email()
