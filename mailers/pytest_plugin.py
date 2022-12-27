import typing_extensions

import pytest
import typing
from email.message import EmailMessage

Mailbox: typing_extensions.TypeAlias = typing.List[EmailMessage]


@pytest.fixture
def mailbox() -> Mailbox:  # pragma: nocover
    return []
