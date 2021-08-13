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

## Features

* full utf-8 support
* fully async
* pluggable transports
* multiple built-in transports including: SMTP, file, null, in-memory, streaming, and console.
* plugin system
* DKIM signing

## Usage

A little of theory. This library exposes two main concepts: mailers and transports. Mailers are high-level interfaces
that you should use to send emails while transports are low-level drivers for mailers.

Here is the example:

```python
from mailers import create_mailer, EmailMessage

message = EmailMessage(to='user@localhost', from_address='from@localhost', subject='Hello', text_body='World!')
mailer = create_mailer('smtp://user:password@localhost:25?timeout=2')
await mailer.send(message)
```

You can also send to multiple recipients by passing an iterable int `to` argument:

```python
message = EmailMessage(to=['user@localhost', 'user2@localhost', 'user@localhost'], ...)
```

## Compose messages

The arguments and methods of `EmailMessage ` class are self-explanatory so here is an kick-start example:

```python
from mailers import EmailMessage, Attachment

message = EmailMessage(
    to='user@localhost',
    from_address='from@example.tld',
    cc='cc@example.com',
    bcc=['bcc@example.com'],
    text_body='Hello world!',
    html_body='<b>Hello world!</b>',
)
```

`cc`, `bcc`, `to`, `reply_to` can be either strings or lists of strings.

## Attachments

Use `attach_file` and `attach_content` to add attachments. Also, you can use `Attachment` class for more control.

```python
from mailers import EmailMessage, Attachment

message = EmailMessage(
    to='user@localhost',
    from_address='from@example.tld',
    text_body='Hello world!',
    attachments=[
        Attachment('CONTENTS', 'file.txt', 'text/plain'),
    ]
)

# attachments can be added on demand:
await message.attach_file(path='file.txt')

# attach using a class
message.add_attachment(Attachment('CONTENTS', 'file.txt', 'text/plain'))

# or you may pass attachment contents directory
message.attach_content(file_name='file.txt', content='HERE GO ATTACHMENT CONTENTS', mime_type='text/plain')
```

## Inline attachments

You can add inline attachments (eg. images) and then reference them in HTML. For that, set `inline=True` and
specify `content_id=SOMEUNIQID` arguments in `attach_*` functions. Then you can reference images in HTML part like
that `<img src="cid:SOMEUNIQID">"`.

```python
from mailers import EmailMessage, Attachment

message = EmailMessage(
    to='user@localhost',
    from_address='from@example.tld',
    html_body='Render me <img src="cid:img1">',
)

await message.attach_file(path='/path/to/image.png', inline=True, content_id='img1')
```

## DKIM signing

You may wish to add DKIM signature to your messages to prevent them from being put into the spam folder. We provide a
plugin for it.

Note, you need to install [`dkimpy`](https://pypi.org/project/dkimpy/) package to start using this plugin.

```python
from mailers import create_mailer
from mailers.plugins.dkim import DkimSignature

dkim_plugin = DkimSignature(selector='default', private_key_path='/path/to/key.pem')

# or you can put key content using private_key argument
dkim_plugin = DkimSignature(selector='default', private_key='PRIVATE KEY GOES here...')

mailer = create_mailer('smtp://')
```

The plugin signs "From", "To", "Subject" headers by default. Use "headers" argument to override it.

It is recommended to place DKIM plugin to the last place in the plugins list.

## Plugins

Plugins let you inspect and modify outgoing messages before or after they are sent. The plugin is a class that
implements `mailers.plugins.Plugin` protocol. Plugins are added to mailers via `plugins` argument.

Below you see an example plugin:

```python
from email.message import Message

from mailers import BasePlugin, create_mailer, Mailer


class PrintPlugin(BasePlugin):

    async def on_before_send(self, message: Message) -> None:
        print('sending message %s.' % message)

    async def on_after_send(self, message: Message) -> None:
        print('message has been sent %s.' % message)


mailer = Mailer(plugins=[PrintPlugin()])

# or if you use create_mailer shortcut
mailer = create_mailer(plugins=[PrintPlugin()])
```

## Transports

### SMTP transport

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
from mailers import Mailer, InMemoryTransport, EmailMessage

transport = InMemoryTransport([])
mailer = Mailer(transport=transport)

await mailer.send(EmailMessage(...))
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
mailer = Mailer(transport=transport)
```

### Console transport

This is a preconfigured subclass of streaming transport. Writes to `sys.stderr` by default.

**Class:** `mailers.transports.ConsoleTransport`
**DSN:** `console://`
**Options:**

* `output` (typing.IO) - a writable stream

### Custom transports.

Each transport must implement `mailers.transports.Transport` protocol. Preferably, inherit from `BaseTransport` class:

```python
import typing as t
from email.message import Message
from mailers import BaseTransport, Mailer, EmailMessage, Transport, EmailURL


class PrintTransport(BaseTransport):
    @classmethod
    def from_url(cls, url: t.Union[str, EmailURL]) -> t.Optional[Transport]:
        # this method is optional,
        # if your transport does not support instantiation from URL then return None here.
        # returning None is the default behavior
        return None

    async def send(self, message: Message) -> None:
        print(str(message))


mailer = Mailer(transport=PrintTransport())
```

The library will call `Transport.from_url` when it needs to instantiate the transport instance from the URL. It is ok to
return `None` as call result then the transport will be instantiated using construction without any arguments passed.

Once you have defined a new transport, register a URL protocol for it:

```python
add_protocol_handler('print', PrintTransport)
mailer = Mailer('print://')
```
