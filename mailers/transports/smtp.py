from __future__ import annotations

import aiosmtplib
from email.message import Message
from typing import Union

from mailers.config import EmailURL
from mailers.result import SentMessage
from mailers.transports.base import Transport


class SMTPTransport(Transport):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 25,
        user: str = None,
        password: str = None,
        use_tls: bool = None,
        timeout: int = 10,
        key_file: str = None,
        cert_file: str = None,
    ):
        self._host = host
        self._user = user
        self._port = port
        self._password = password
        self._use_tls = use_tls or False
        self._timeout = timeout
        self._key_file = key_file
        self._cert_file = cert_file

    async def send(self, message: Message) -> SentMessage:
        try:
            await aiosmtplib.send(
                message,
                hostname=self._host,
                port=self._port,
                use_tls=self._use_tls,
                username=self._user,
                password=self._password,
                timeout=self._timeout,
                client_key=self._key_file,
                client_cert=self._cert_file,
            )
        except aiosmtplib.errors.SMTPException as ex:  # pragma: no cover
            return SentMessage(False, message, self, ex.message)
        return SentMessage(True, message, self)

    @classmethod
    def from_url(cls, url: Union[str, EmailURL]) -> SMTPTransport:
        url = EmailURL(url)

        def _cast_to_bool(value: str) -> bool:
            return value.lower() in ["yes", "1", "on", "true"]

        timeout = url.options.get("timeout", None)
        if timeout:
            timeout = int(timeout)

        use_tls = _cast_to_bool(url.options.get("use_tls", ""))
        key_file = url.options.get("key_file", None)
        cert_file = url.options.get("cert_file", None)

        return cls(
            url.hostname or "localhost",
            url.port or 25,
            url.username,
            url.password,
            use_tls=use_tls,
            timeout=timeout,
            key_file=key_file,
            cert_file=cert_file,
        )
