import pytest
import typing
from email.message import EmailMessage

Mailbox: typing.TypeAlias = typing.List[EmailMessage]


@pytest.fixture
def mailbox() -> Mailbox:  # pragma: nocover
    return []
