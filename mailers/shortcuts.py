from typing import Any, Iterable, Union

from .mailer import Mailer, registry
from .message import EmailMessage


def get_mailer(name: str = "default") -> Mailer:
    return registry.get(name)


async def send_mail(
    to: Union[str, Iterable[str]], message: EmailMessage, mailer: str = "default"
) -> Any:
    message.to = to
    return await registry.get(mailer).send(message)
