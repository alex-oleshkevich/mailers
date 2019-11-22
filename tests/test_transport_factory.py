from unittest import mock

import pytest

from mailers import EmailURL, NullTransport, Transports
from mailers.exceptions import NotRegisteredTransportError


def test_binds_url():
    Transports.bind_url("console", "klass")
    assert "console" in Transports.mapping
    assert Transports.mapping["console"] == "klass"


def test_binds_urls():
    Transports.bind_urls({"console": "klass"})
    assert "console" in Transports.mapping
    assert Transports.mapping["console"] == "klass"


def test_creates_from_url():
    Transports.bind_url("console", "mailers.transports:NullTransport")
    transport = Transports.from_url("console://")
    assert isinstance(transport, NullTransport)

    transport = Transports.from_url(EmailURL("console://"))
    assert isinstance(transport, NullTransport)


def test_creates_from_url_calls_from_url():
    spy = mock.MagicMock()

    class _transport:
        @classmethod
        def from_url(cls, url):
            spy(url)

    with mock.patch("mailers.transports.import_from_string", lambda x: _transport):
        Transports.from_url("console://")
        spy.assert_called_once()


def test_raises_when_no_transport():
    with pytest.raises(NotRegisteredTransportError) as ex:
        Transports.from_url("invalid://")
    assert str(ex.value) == 'No transport found with scheme "invalid".'
