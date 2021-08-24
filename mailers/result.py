import typing as t
from email.message import Message

if t.TYPE_CHECKING:  # pragma: no cover
    from .transports import Transport


class SentMessage:
    def __init__(self, ok: bool, message: Message, transport: 'Transport', error: str = None) -> None:
        self.ok = ok
        self.message = message
        self.transport = transport
        self.error = error


class SentMessages:
    def __init__(self) -> None:
        self._messages: t.List[SentMessage] = []

    @property
    def ok(self) -> bool:
        return all(m.ok for m in self._messages)

    def append(self, message: SentMessage) -> None:
        self._messages.append(message)

    def __bool__(self) -> bool:
        return self.ok

    def __len__(self) -> int:
        return len(self._messages)
