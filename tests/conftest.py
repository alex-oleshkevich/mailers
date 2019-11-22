import asyncio

import pytest
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Message

from mailers import InMemoryTransport, Mailer, configure
from mailers.message import EmailMessage


async def amain(handler):
    cont = Controller(handler, hostname="localhost", port=10025)
    cont.start()
    return cont


class RecordingHandler(Message):
    def __init__(self, mailbox):
        self.messages = mailbox
        super().__init__()

    def handle_message(self, message):
        self.messages.append(message)

    async def handle_EHLO(self, server, session, envelope, hostname):
        """Advertise auth login support."""
        session.host_name = hostname
        return "250-AUTH LOGIN\r\n250 HELP"


@pytest.fixture(scope="function")
def mailbox():
    return []


@pytest.fixture(scope="function")
def smtpd_handler(mailbox):
    return RecordingHandler(mailbox)


@pytest.fixture(scope="function")
def smtpd_server(request, smtpd_handler):
    event_loop = asyncio.get_event_loop()
    server = event_loop.run_until_complete(amain(smtpd_handler))

    def close_server():
        server.stop()

    request.addfinalizer(close_server)

    return server


@pytest.fixture
def message():
    return EmailMessage(
        to="user@localhost",
        subject="subject",
        text_body="contents",
        from_address="root@localhost",
    )


@pytest.fixture()
def mailer(mailbox):
    transport = InMemoryTransport(mailbox)
    return Mailer(transport)


@pytest.fixture(autouse=True)
def configure_mailers(mailbox):
    configure(mailers={"default": Mailer(InMemoryTransport(mailbox))})
