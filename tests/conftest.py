import asyncio
import pytest
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Message

from mailers import InMemoryTransport, Mailer, add_mailer
from mailers.mailer import clear_mailers
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

    async def handle_EHLO(self, server, session, envelope, hostname, responses):
        """Advertise auth login support."""
        session.host_name = hostname
        return responses


@pytest.fixture(scope="function")
def mailbox():
    return []


@pytest.fixture(scope="function")
def smtpd_handler(mailbox):
    return RecordingHandler(mailbox)


@pytest.fixture(scope="function")
def smtpd_server(smtpd_handler):
    event_loop = asyncio.get_event_loop()
    server = event_loop.run_until_complete(amain(smtpd_handler))
    print('start server' * 10)
    yield server
    print('stop server' * 10)
    server.stop()


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
    add_mailer(mailer=Mailer(InMemoryTransport(mailbox)), name='default')
    yield
    clear_mailers()
