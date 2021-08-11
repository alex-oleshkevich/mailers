# Mailers for asyncio

![PyPI](https://img.shields.io/pypi/v/mailers)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/alex-oleshkevich/mailers/Lint)
![GitHub](https://img.shields.io/github/license/alex-oleshkevich/mailers)
![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/mailers)
![PyPI - Downloads](https://img.shields.io/pypi/dm/mailers)
![GitHub Release Date](https://img.shields.io/github/release-date/alex-oleshkevich/mailers)
![Lines of code](https://img.shields.io/tokei/lines/github/alex-oleshkevich/mailers)


## Installation

```bash
pip install mailers
```

## Usage

The package uses two main concepts: mailers and transports. The mailer is a class which abstracts you from the
underlying transport and the transport does the actual message delivery.

```python
from mailers import add_mailer, EmailMessage, send

add_mailer('smtp://user:password@localhost:25?timeout=2', name='default')

message = EmailMessage(
    to='user@localhost', from_address='from@localhost',
    subject='Hello', text_body='World!'
)
await send('user@localhost', message)
```

Or if you prefer more control on what is going one, take this more verbose path:

```python
from mailers import Mailer, SMTPTransport, EmailMessage

mailer = Mailer(SMTPTransport('localhost', 25))

message = EmailMessage(
    to='user@localhost', from_address='from@localhost',
    subject='Hello', text_body='World!'
)
await mailer.send(message)
```

## Compose messages

The arguments and methods of `EmailMessage ` class are self-explanatory so here is some basic example:

```python
from mailers import EmailMessage, Attachment

message = EmailMessage(
    to='user@localhost',
    from_address='from@example.tld',
    cc='cc@example.com',
    bcc=['bcc@example.com'],
    text_body='Hello world!',
    html_body='<b>Hello world!</b>',
    attachments=[
        Attachment('CONTENTS', 'file.txt', 'text/plain'),
    ]
)

# attachments can be added on demand:

with open('file.txt', 'r') as f:
    message.attach(f.read(), f.name, 'text/plain')

    # alternatively
    message.add_attachment(
        Attachment(f.read(), f.name, 'text/plain')
    )
```

`cc`, `bcc`, `to`, `reply_to` can be either strings or lists of strings.

### A note about attachments

Accessing files is a blocking operation. You may want to use `aiofiles` or alternate library which reads files in
non-blocking mode.

This package does not implement direct access to files at moment. This is something to do at later stage.

## Transports

### Preinstalled transports

All transport classes can be found in `mailers.transports` module.

| Class             | Example URL                                       | Description                                                       |
|-------------------|---------------------------------------------------|-------------------------------------------------------------------|
| SMTPTransport     | smtp://user:pass@hostname:port?timeout=&use_tls=1 | Sends mails using SMTP protocol.                                  |
| InMemoryTransport | not available                                     | Stores sent messages in the local variable. See an example below. |
| FileTransport     | file:///path/to/directory                         | Writes sent messages into directory.                              |
| NullTransport     | null://                                           | Does not perform any sending.                                     |
| StreamTransport   | not available                                     | Writes message to an open stream. See an example below.           |
| ConsoleTransport  | console://                                        | Prints messages into stdout.                                      |
| GMailTransport    | gmail://username:password                         | Sends via GMail.                                                  |
| MailgunTransport  | mailgun://username:password                       | Sends via Mailgun.                                                |

### Special notes

#### InMemoryTransport

`InMemoryTransport` takes a list and writes outgoing mail into it. Read this list to inspect the outbox.

```python
from mailers import InMemoryTransport, EmailMessage

message = EmailMessage(from_address='noreply@localhost')
mailbox = []
transport = InMemoryTransport(mailbox)
await transport.send(message)

assert message in mailbox
```

#### StreamTransport

Writes messages into the open stream.

```python
from mailers import StreamTransport, EmailMessage
from io import StringIO

message = EmailMessage(from_address='noreply@localhost')

transport = StreamTransport(output=StringIO())
await transport.send(message)
```

`output` is any IO compatible object.

### Custom transports.

Each transport must implement `async def send(self, message: EmailMessage) -> None` method. Preferably, inherit
from `BaseTransport` class:

```python
from mailers import BaseTransport, Mailer, EmailMessage


class PrintTransport(BaseTransport):
    async def send(self, message: EmailMessage) -> None
        print(str(message))


mailer = Mailer(transport=PrintTransport())
```

In order to make your transport to accept `EmailURL` instances, your transport class has to implement `from_url`
class method:

```python
from mailers import BaseTransport, EmailURL


class PrintTransport(BaseTransport):
    @classmethod
    def from_url(cls, url: EmailURL) -> "PrintTransport":
        return cls()
```

### Add custom transport protocols.

Once you build a custom transport you can add it's URL to enable URL-based configurations.

```python
from mailers import add_protocol_handler, Mailer, BaseTransport, EmailURL, create_from_url

class PrintTransport(BaseTransport):
    @classmethod
    def from_url(cls, url: EmailURL) -> "PrintTransport":
        return cls()

add_protocol_handler('myprotocol', PrintTransport)

mailer = Mailer(transport=create_from_url('myprotocol://'))
```

Note that the transport must to implement `from_url` method to accept URL parameters. Otherwise it will be constructed
without any arguments passed to the `__init__` method.
