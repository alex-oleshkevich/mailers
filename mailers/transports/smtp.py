from __future__ import annotations

import aiosmtplib
import typing
from email.message import Message

from mailers.exceptions import DeliveryError
from mailers.transports.base import Transport


class SMTPTransport(Transport):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 25,
        user: typing.Optional[str] = None,
        password: typing.Optional[str] = None,
        use_tls: typing.Optional[bool] = None,
        timeout: int = 10,
        key_file: typing.Optional[str] = None,
        cert_file: typing.Optional[str] = None,
    ):
        self._host = host
        self._user = user
        self._port = port
        self._password = password
        self._use_tls = use_tls or False
        self._timeout = timeout
        self._key_file = key_file
        self._cert_file = cert_file

    async def send(self, message: Message) -> None:
        _, status = await aiosmtplib.send(
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
        if status != "OK":
            raise DeliveryError(f"Failed to send email via SMTP transport: {status}")
