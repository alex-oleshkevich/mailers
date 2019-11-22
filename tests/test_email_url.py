from mailers.config import EmailURL


def test_email_url_repr():
    u = EmailURL("smtp://localhost")
    assert repr(u) == "EmailURL('smtp://localhost')"

    u = EmailURL("smtp://username@localhost")
    assert repr(u) == "EmailURL('smtp://username@localhost')"

    u = EmailURL("smtp://username:password@localhost")
    assert repr(u) == "EmailURL('smtp://username:********@localhost')"


def test_email_url_properties():
    u = EmailURL("smtp+sync://username:password@localhost:1025/")
    assert u.transport == "smtp+sync"
    assert u.username == "username"
    assert u.password == "password"
    assert u.hostname == "localhost"
    assert u.netloc == "username:password@localhost:1025"
    assert u.port == 1025


def test_email_url_equals():
    u = EmailURL("smtp://localhost")
    u2 = EmailURL("smtp://localhost")
    assert u == u2

    u3 = EmailURL("file://localhost")
    assert u != u3


def test_email_url_options():
    u = EmailURL("smtp+sync://username:password@localhost:1025/?use_ssl=true&timeout=2")
    assert u.options == {"use_ssl": "true", "timeout": "2"}


def test_replace_email_url_components():
    # transport
    u = EmailURL("smtp://localhost")
    new = u.replace(transport="file")
    assert new.transport == "file"
    assert str(new) == "file://localhost"

    # username
    u = EmailURL("smtp://localhost")
    new = u.replace(username="username")
    assert new.username == "username"
    assert str(new) == "smtp://username@localhost"

    # password
    u = EmailURL("smtp://localhost")
    new = u.replace(username="username", password="password")
    assert new.password == "password"
    assert str(new) == "smtp://username:password@localhost"

    # hostname
    u = EmailURL("smtp://localhost")
    new = u.replace(hostname="otherhost")
    assert new.hostname == "otherhost"
    assert str(new) == "smtp://otherhost"

    # port
    u = EmailURL("smtp://localhost")
    new = u.replace(port=123)
    assert new.port == 123
    assert str(new) == "smtp://localhost:123"


def test_email_url_returns_path():
    u = EmailURL("file:///tmp/some/path")
    assert u.path == "/tmp/some/path"
