import typing as t
from email.message import Message

try:  # pragma: no cover
    import dkim
except ImportError:  # pragma: no cover
    raise ImportError(
        'Please install dkimpy (https://pypi.org/project/dkimpy/) library ' 'to sign messages with DKIM method.'
    )

from mailers.signers.base import Signer


class DKIMSigner(Signer):
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

    def sign(self, message: Message) -> Message:
        key = self.dkim_key or ''
        if self.dkim_key_path:
            # we read file once and then cache in this instance
            # so it shouldn't bottleneck the flow.
            # this is intentional, to avoid marking this method async
            # if it doesn't work for you then pass key using "private_key" argument.
            with open(self.dkim_key_path, 'r') as f:
                key = f.read()
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
        return message
