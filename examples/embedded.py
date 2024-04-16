"""
This example demonstrates how to add inline attachments to your message.

You need to setup several environment variables before you can use this script:

* MAILERS_RECIPIENT - a recipient's email ("To" header)
* MAILERS_FROM_ADDRESS - a sender address ("From" header)
* MAILER_URL - mailer configuration URL
"""

import asyncio
import base64
import os
import pathlib
import tempfile

from mailers import Mailer, create_transport_from_url
from mailers.message import Email

RED_DOT = """iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAIAAAACDbGyAAABhWlDQ1BJQ0MgcHJvZmlsZQAAKJF9
kT1Iw0AcxV9TpUVaFOwgIpihCoIFURFHrUIRKoRaoVUHk0s/hCYNSYuLo+BacPBjserg4qyrg6sg
CH6AuLk5KbpIif9LCi1iPDjux7t7j7t3gFAvMc3qGAM0vWKmEnExk10RA68IIowejGBQZpYxK0lJ
eI6ve/j4ehfjWd7n/hxhNWcxwCcSzzDDrBCvE09tVgzO+8QRVpRV4nPiUZMuSPzIdcXlN84FhwWe
GTHTqTniCLFYaGOljVnR1IgniaOqplO+kHFZ5bzFWStVWfOe/IWhnL68xHWaA0hgAYuQIEJBFRso
oYIYrTopFlK0H/fw9zt+iVwKuTbAyDGPMjTIjh/8D353a+Unxt2kUBzofLHtjyEgsAs0arb9fWzb
jRPA/wxc6S1/uQ5Mf5Jea2nRI6B7G7i4bmnKHnC5A/Q9GbIpO5KfppDPA+9n9E1ZoPcW6Fp1e2vu
4/QBSFNXyRvg4BAYLlD2mse7g+29/Xum2d8PfP9yq/QP1TIAAAAJcEhZcwAALiMAAC4jAXilP3YA
AAAHdElNRQflCA0QKgFMDexDAAAAGXRFWHRDb21tZW50AENyZWF0ZWQgd2l0aCBHSU1QV4EOFwAA
ABFJREFUCNdj/M+AApgYKOMDAFCRAQngX9IjAAAAAElFTkSuQmCC"""

MAILER_URL = os.environ.get("MAILER_URL", "null://")
MAILERS_RECIPIENT = os.environ.get("MAILERS_RECIPIENT", "root@localhost")
MAILERS_FROM_ADDRESS = os.environ.get("MAILERS_FROM_ADDRESS", "sender@localhost")

DOT_FILE = pathlib.Path(__file__).parent / "dot.png"


async def main() -> None:
    with tempfile.NamedTemporaryFile("w") as tmp_file:
        tmp_file.write("temp file contents")
        tmp_file.seek(0)

        message = Email(
            to=MAILERS_RECIPIENT,
            subject="Attachments test",
            html='Do you see this red dot? <img src="cid:img1"> <img src="cid:img2"> <img src="cid:img3">',
            from_address=MAILERS_FROM_ADDRESS,
        )
        message.embed(base64.b64decode(RED_DOT), "img1", "image/png")
        await message.embed_from_path(DOT_FILE, "img2")
        message.embed_from_path_sync(DOT_FILE, "img3")

        mailer = Mailer(create_transport_from_url(MAILER_URL))
        await mailer.send(message)


if __name__ == "__main__":
    asyncio.run(main())
