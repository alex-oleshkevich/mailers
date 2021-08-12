import aiofiles
import dkim

from .. import EmailMessage
from . import BasePlugin


class DkimSignature(BasePlugin):
    def __init__(
        self,
        dkim_selector: str,
        dkim_key: str = None,
        dkim_key_path: str = None,
        headers: str = None,
    ) -> None:
        assert dkim_key or dkim_key_path, 'Either "dkim_key" or "dkim_key_path" must be passed.'
        self.dkim_selector = dkim_selector
        self.dkim_key = dkim_key
        self.dkim_key_path = dkim_key_path
        if headers:
            self.headers = [h.encode() for h in headers]
        else:
            self.headers = [
                b'Content-Transfer-Encoding',
                b'Content_type',
                b'MIME-Version',
                b'To',
                b'From',
                b'Subject',
                b'Date',
                b'Message-ID',
                b'Sender',
            ]

    async def on_before_send(self, message: EmailMessage) -> None:
        key = self.dkim_key.encode() if self.dkim_key else ''
        if self.dkim_key_path:
            async with aiofiles.open(self.dkim_key_path, 'rb') as f:
                key = await f.read()

        assert message.from_address
        sender_domain = message.from_address.split('@')[-1]
        signature = dkim.sign(
            message=message.as_string().encode(),
            selector=str(self.dkim_selector).encode(),
            domain=sender_domain.encode(),
            privkey=key,
            include_headers=self.headers,
        )
        message.headers["DKIM-Signature"] = signature[len("DKIM-Signature: ") :].decode()
