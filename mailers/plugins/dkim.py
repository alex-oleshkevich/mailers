import aiofiles
import dkim
import typing as t
from email.message import Message

from . import BasePlugin


class DkimSignature(BasePlugin):
    def __init__(
        self,
        selector: str,
        private_key: str = None,
        private_key_path: str = None,
        headers: t.Iterable[str] = None,
    ) -> None:
        assert private_key or private_key_path, 'Either "dkim_key" or "dkim_key_path" must be passed.'
        self.dkim_selector = selector
        self.dkim_key = private_key
        self.dkim_key_path = private_key_path
        self.headers = headers or ['From', 'To', 'Subject']

    async def on_before_send(self, message: Message) -> None:
        key = self.dkim_key or ''
        if self.dkim_key_path:
            async with aiofiles.open(self.dkim_key_path, 'r') as f:
                key = await f.read()
                self.dkim_key = key  # cache

        from_address = message['From']
        sender_domain = from_address.split('@')[-1]

        signature = dkim.sign(
            message=message.as_bytes(),
            selector=self.dkim_selector.encode(),
            domain=sender_domain.encode(),
            privkey=key.encode(),
            include_headers=self.headers,
        )
        message.add_header("DKIM-Signature", signature[len("DKIM-Signature: ") :].decode().replace('\r\n', ' '))
