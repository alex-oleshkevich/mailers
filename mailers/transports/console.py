import sys
import typing

from mailers.transports.stream import StreamTransport


class ConsoleTransport(StreamTransport):
    def __init__(self, stream: typing.Literal["stdout", "stderr"] = "stderr") -> None:
        assert stream in ["stdout", "stderr"], "Unsupported console stream type: %s." % stream
        output = None
        if stream == "stderr":
            output = sys.stderr
        elif stream == "stdout":
            output = sys.stdout
        super().__init__(output)
