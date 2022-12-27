# Mailers for asyncio

![PyPI](https://img.shields.io/pypi/v/mailers)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/alex-oleshkevich/mailers/Lint%20and%20test)
![GitHub](https://img.shields.io/github/license/alex-oleshkevich/mailers)
![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/mailers)
![PyPI - Downloads](https://img.shields.io/pypi/dm/mailers)
![GitHub Release Date](https://img.shields.io/github/release-date/alex-oleshkevich/mailers)
![Lines of code](https://img.shields.io/tokei/lines/github/alex-oleshkevich/mailers)

## Features

* fully typed
* full utf-8 support
* async and sync sending
* pluggable transports
* multiple built-in transports including: SMTP, file, null, in-memory, streaming, and console.
* message preprocessors
* embeddables
* attachments (with async and sync interfaces)
* message signing via Signer interface (DKIM bundled)
* message encryption via Encrypter interface
* trio support via anyio
* fallback transports
* global From address
* templated emails

## Usage

```bash
pip install mailers[aiosmtplib]
```

Then create mailer:

```python
from mailers import Mailer

mailer = Mailer("smtp://user:password@localhost:25?timeout=2")
await mailer.send_message(
    to="user@localhost", from_address="from@localhost", subject="Hello", text="World!"
)
```

## Compose messages

If you need more control over the message, you can use `Email` object to construct email message and then send it
using `mailer.send` method.

```python
from mailers import Email, Mailer

message = Email(
    to="user@localhost",
    from_address="from@example.tld",
    cc="cc@example.com",
    bcc=["bcc@example.com"],
    text="Hello world!",
    html="<b>Hello world!</b>",
)
mailer = Mailer("smtp://")
await mailer.send(message)
```

### Global From address

Instead of setting "From" header in every message, you can set it mailer-wide. Use `from_address` argument of Mailer
class:

```python
mailer = Mailer(from_address="sender@localhost")
```

The mailer will set From header with the given value to all messages that do not container From or Sender headers.

## Using Jinja templates

> Requires `jinja2` package installed

You can use Jinja to render templates. This way, your `text` and `html` can be rendered from a template.

Use `TemplatedMailer` instead of default `Mailer` and set a `jinja2.Environment` instance.
Then, call `send_templated_message`.

```python
import jinja2

from mailers import TemplatedMailer

env = jinja2.Environment(loader=jinja2.FileSystemLoader(["templates"]))
mailer = TemplatedMailer("smtp://", env)
mailer.send_templated_message(
    to="...",
    subject="Hello",
    text_template="mail.txt",
    html_template="mail.html",
    template_context={"user": "root"},
)
```

## Attachments

Use `attach`, `attach_from_path`, `attach_from_path_sync` methods to attach files.

```python
from mailers import Email

message = Email(
    to="user@localhost", from_address="from@example.tld", text="Hello world!"
)

# attachments can be added on demand
await message.attach_from_path("file.txt")

# or use blocking sync version
message.attach_from_path_sync("file.txt")

# attach from variable
message.attach("CONTENTS", "file.txt", "text/plain")
```

## Embedding files

In the same way as with attachments, you can inline file into your messages. This is commonly used to display embedded
images in the HTML body. Here are method you can use `embed`, `embed_from_path`, `embed_from_path_sync`.

```python
from mailers import Email

message = Email(
    to="user@localhost",
    from_address="from@example.tld",
    html='Render me <img src="cid:img1">',
)

await message.embed_from_path(path="/path/to/image.png", name="img1")
```

Note, that you have to add HTML part to embed files. Otherwise, they will be ignored.

## Message signatures

You can sign messages (e.g. with DKIM) by passing `signer` argument to the `Mailer` instance.

```python
signer = MySigner()
mailer = Mailer(..., signer=signer)
```

### DKIM signing

> Requires `dkimpy` package installed

You may wish to add DKIM signature to your messages to prevent them from being put into the spam folder.

Note, you need to install [`dkimpy`](https://pypi.org/project/dkimpy/) package before using this feature.

```python
from mailers import Mailer
from mailers.signers.dkim import DKIMSigner

signer = DKIMSigner(selector="default", private_key_path="/path/to/key.pem")

# or you can put key content using private_key argument
signer = DKIMSigner(selector="default", private_key="PRIVATE KEY GOES here...")

mailer = Mailer("smtp://", signer=signer)
```

Now all outgoing messages will be signed with DKIM method.

The plugin signs "From", "To", "Subject" headers by default. Use "headers" argument to override it.

## Custom signers

Extend `mailers.Signer` class and implement `sign` method:

```python
from email.message import Message
from mailers import Signer


class MySigner(Signer):
    def sign(self, message: Message) -> Message:
        # message signing code here...
        return message
```

## Encrypters

When encrypting a message, the entire message (including attachments) is encrypted using a certificate. Therefore, only
the recipients that have the corresponding private key can read the original message contents.

````python
encrypter = MyEncrypter()
mailer = Mailer(..., encrypter=encrypter)
````

Now all message content will be encrypted.

## Custom encrypters

Extend `mailers.Encrypter` class and implement `encrypt` method:

```python
from email.message import Message
from mailers import Encrypter


class MyEncrypter(Encrypter):
    def encrypt(self, message: Message) -> Message:
        # message encrypting code here...
        return message
```

## High Availability

Use `MultiTransport` to provide a fallback transport. By default, the first transport is used but if it fails to send
the message, it will retry sending using next configured transport.

```python
from mailers import Mailer, MultiTransport, SMTPTransport

primary_transport = SMTPTransport()
fallback_transport = SMTPTransport()

mailer = Mailer(MultiTransport([primary_transport, fallback_transport]))
```

## Preprocessors

Preprocessors are function that mailer calls before sending. Preprocessors are simple functions that modify message
contents.

Below you see an example preprocessor:

```python
from email.message import EmailMessage

from mailers import Mailer


def attach_html_preprocessor(message: EmailMessage) -> EmailMessage:
    message.add_alternative(b"This is HTML body", subtype="html", charset="utf-8")
    return message


mailer = Mailer(preprocessors=[attach_html_preprocessor])
```

### CSS inliner

> Requires `toronado` package installed

Out of the box we provide `mailers.preprocessors.css_inliner` utility that converts CSS classes into inline styles.

## Transports

### SMTP transport

> Requires `aiosmtplib` package installed

Send messages via third-party SMTP servers.

**Class:** `mailers.transports.SMTPTransport`
**directory** `smtp://user:pass@hostname:port?timeout=&use_tls=1`
**Options:**

* `host` (string, default "localhost") - SMTP server host
* `port` (string, default "25") - SMTP server port
* `user` (string) - SMTP server login
* `password` (string) - SMTP server login password
* `use_tls` (string, choices: "yes", "1", "on", "true") - use TLS
* `timeout` (int) - connection timeout
* `cert_file` (string) - path to certificate file
* `key_file` (string) - path to key file

### File transport

Write outgoing messages into a directory in EML format.

**Class:** `mailers.transports.FileTransport`
**DSN:** `file:///tmp/mails`
**Options:**

* `directory` (string) path to a directory

### Null transport

Discards outgoing messages. Takes no action on send.

**Class:** `mailers.transports.NullTransport`
**DSN:** `null://`

### Memory transport

Keeps all outgoing messages in memory. Good for testing.

**Class:** `mailers.transports.InMemoryTransport`
**DSN:** `memory://`
**Options:**

* `storage` (list of strings) - outgoing message container

You can access the mailbox via ".mailbox" attribute.

Example:

```python
from mailers import Mailer, InMemoryTransport, Email

transport = InMemoryTransport([])
mailer = Mailer(transport)

await mailer.send(Email(...))
assert len(transport.mailbox) == 1  # here are all outgoing messages
```

### Streaming transport

Writes all messages into a writable stream. Ok for local development.

**Class:** `mailers.transports.StreamTransport`
**DSN:** unsupported
**Options:**

* `output` (typing.IO) - a writable stream

Example:

```python
import io
from mailers import Mailer, StreamTransport

transport = StreamTransport(output=io.StringIO())
mailer = Mailer(transport)
```

### Console transport

This is a preconfigured subclass of streaming transport. Writes to `sys.stderr` by default.

**Class:** `mailers.transports.ConsoleTransport`
**DSN:** `console://`
**Options:**

* `output` (typing.IO) - a writeable stream

### Multi transport

The purpose of this transport is to provide a developer an option to provide a fallback transport.
You can configure several channels and `MultiTransport` will guarantee that at least one will deliver the message.

**Class:** `mailers.transports.MultiTransport`
**DSN:** `-`
**Options:**

* `transports` (list[Transport]) - subtransports

### Custom transports.

Each transport must extend `mailers.transports.Transport` base class.

```python
from email.message import Message
from mailers import Mailer, Transport


class PrintTransport(Transport):
    async def send(self, message: Message) -> None:
        print(str(message))


mailer = Mailer(PrintTransport())
```
