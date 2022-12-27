import typing
from email.message import EmailMessage

from mailers.exceptions import MailersError
from mailers.transports.base import Transport


class MultiDeliveryError(MailersError):
    def __init__(self, message: str, exceptions: typing.List[Exception]) -> None:
        super().__init__(message)
        self.exceptions = exceptions


class MultiTransport(Transport):
    def __init__(self, transports: typing.Iterable[Transport]) -> None:
        self.transports = list(transports)

    async def send(self, message: EmailMessage) -> None:
        exceptions: typing.List[Exception] = []
        for transport in self.transports:
            try:
                await transport.send(message)
            except Exception as ex:
                exceptions.append(ex)
            else:
                return

        raise MultiDeliveryError("Failed to deliver message via configured mailers.", exceptions)
