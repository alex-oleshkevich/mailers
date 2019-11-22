import pytest

from mailers import EmailURL, MailerRegistry
from mailers.exceptions import NotRegisteredMailer
from mailers.transports import ConsoleTransport


@pytest.fixture()
def registry():
    return MailerRegistry()


def test_add_get_mailer_and_contains(mailer, registry):
    registry.add('default', mailer)
    assert 'default' in registry
    assert registry.get('default') == mailer


def test_raises_when_not_registered(registry):
    with pytest.raises(NotRegisteredMailer) as ex:
        registry.get('invalid')
    assert (str(ex.value)) == 'Mailer with name "invalid" not registered.'


def test_creates_from_string(registry):
    registry.add('default', 'console://')
    assert isinstance(registry.get('default')._transport, ConsoleTransport)


def test_creates_from_url(registry):
    registry.add('default', EmailURL('console://'))
    assert isinstance(registry.get('default')._transport, ConsoleTransport)
