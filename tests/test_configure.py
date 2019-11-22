from mailers import Transports, configure, registry


def test_adds_mailers():
    configure(mailers={"test_transport": "console://"})
    assert "test_transport" in registry


def test_adds_transports():
    configure(mailers={}, transports={"test_transport": "TransportClass"})
    assert "test_transport" in Transports.mapping
