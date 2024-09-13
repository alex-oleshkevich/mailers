from __future__ import annotations

import typing
from email.message import Message

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
        cert_bundle: typing.Optional[str] = None,
        validate_certs: typing.Optional[bool] = None,
    ):
        self._host = host
        self._user = user
        self._port = port
        self._password = password
        self._use_tls = use_tls or False
        self._timeout = timeout
        self._key_file = key_file
        self._cert_file = cert_file
        self._cert_bundle = cert_bundle
        self._validate_certs = validate_certs if validate_certs is not None else True

    async def send(self, message: Message) -> None:
        import aiosmtplib

        sender = message.get("Sender")
        if sender:
            del message["Sender"]
        return_path = message.get("Return-Path")
        if return_path:
            del message["Return-Path"]
        if sender is None and return_path:
            sender = return_path

        await aiosmtplib.send(
            message,
            sender=sender,
            hostname=self._host,
            port=self._port,
            use_tls=self._use_tls,
            username=self._user,
            password=self._password,
            timeout=self._timeout,
            client_key=self._key_file,
            client_cert=self._cert_file,
            cert_bundle=self._cert_bundle,
            validate_certs=self._validate_certs,
        )
