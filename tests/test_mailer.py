import pytest

from mailers import NullTransport, add_mailer, get_mailer
from mailers.exceptions import MailerIsRegisteredError, NotRegisteredMailer
from mailers.mailer import Mailer, clear_mailers, remove_mailer
from mailers.message import EmailMessage


@pytest.mark.asyncio
async def test_mailer_send(mailer, mailbox):
    message = EmailMessage(to="root@localhost", subject="SUBJECT", from_address='noreply@localhost')
    await mailer.send(message)
    assert len(mailbox) == 1


def test_add_mailer_wo_params():
    with pytest.raises(ValueError):
        add_mailer()


def test_add_mailer_forbids_duplicates():
    add_mailer('null://', name='error')
    with pytest.raises(MailerIsRegisteredError):
        add_mailer('null://', name='error')


def test_add_mailer_by_url():
    add_mailer('null://', name='by_url')
    assert type(get_mailer('by_url').transport) == NullTransport


def test_add_mailer_by_mailer():
    add_mailer(mailer=Mailer(NullTransport()), name='by_mailer')
    assert type(get_mailer('by_mailer').transport) == NullTransport


def test_add_mailer_by_transport():
    add_mailer(transport=NullTransport(), name='by_transport')
    assert type(get_mailer('by_transport').transport) == NullTransport


def test_remove_mailer():
    add_mailer(transport=NullTransport(), name='by_transport')
    remove_mailer('by_transport')
    with pytest.raises(NotRegisteredMailer):
        get_mailer('by_transport')


def test_clear_mailers():
    add_mailer(transport=NullTransport(), name='by_transport')
    clear_mailers()
    with pytest.raises(NotRegisteredMailer):
        get_mailer('by_transport')
