import sys
import typing as t

from mailers.config import EmailURL
from mailers.transports.base import Transport
from mailers.transports.stream import StreamTransport


class ConsoleTransport(StreamTransport):
    def __init__(self, stream: t.Literal['stdout', 'stderr'] = 'stderr') -> None:
        assert stream in ['stdout', 'stderr'], 'Unsupported console stream type: %s.' % stream
        output = None
        if stream == 'stderr':
            output = sys.stderr
        elif stream == 'stdout':
            output = sys.stdout
        super().__init__(output)

    @classmethod
    def from_url(cls, url: t.Union[str, EmailURL]) -> t.Optional[Transport]:
        url = EmailURL(url)
        stream = url.options.get('stream')
        assert stream in ['stdout', 'stderr'], 'Unsupported console stream type: %s.' % stream
        return ConsoleTransport(stream)
