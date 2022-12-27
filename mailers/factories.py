import typing
from urllib.parse import parse_qsl, urlparse

from mailers.exceptions import NotRegisteredTransportError
from mailers.transports import ConsoleTransport, FileTransport, InMemoryTransport, NullTransport, Transport
from mailers.transports.smtp import SMTPTransport


def create_transport_from_url(url: str) -> Transport:
    """Create a transport instance from URL configuration."""
    components = urlparse(url)
    protocol = components.scheme
    options = dict(parse_qsl(components.query))

    if protocol == "console":
        assert "stream" in options

        stream = options.get("stream")
        assert stream in ["stdout", "stderr"], '"stream" must be one of "stdout", "stderr"'
        return ConsoleTransport(stream=typing.cast(typing.Literal["stdout", "stderr"], stream))

    if protocol == "file":
        return FileTransport(directory=components.path)

    if protocol == "memory":
        return InMemoryTransport()

    if protocol == "null":
        return NullTransport()

    if protocol == "smtp":

        def _cast_to_bool(value: str) -> bool:
            return value.lower() in ["yes", "1", "on", "true"]

        timeout: typing.Union[str, int, None] = options.get("timeout", None)
        if timeout is not None:
            timeout = int(timeout)

        use_tls = _cast_to_bool(options.get("use_tls", ""))
        key_file: typing.Optional[str] = options.get("key_file", None)
        cert_file: typing.Optional[str] = options.get("cert_file", None)

        return SMTPTransport(
            components.hostname or "localhost",
            components.port or 25,
            components.username,
            components.password,
            use_tls=use_tls,
            timeout=timeout or 10,
            key_file=key_file,
            cert_file=cert_file,
        )

    raise NotRegisteredTransportError(f"Don't know how to create transport for protocol '{protocol}'.")
