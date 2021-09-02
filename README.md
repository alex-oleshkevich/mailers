# Mailers for asyncio

![PyPI](https://img.shields.io/pypi/v/mailers)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/alex-oleshkevich/mailers/Lint)
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
* plugin system
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
pip install mailers
```

```python
from mailers import create_mailer, Email

message = Email(to='user@localhost', from_address='from@localhost', subject='Hello', text='World!')
mailer = create_mailer('smtp://user:password@localhost:25?timeout=2')
await mailer.send(message)
```

You can also send to multiple recipients by passing an iterable int `to` argument:

```python
message = Email(to=['user@localhost', 'user2@localhost', 'user@localhost'], ...)
```

also you can change addresses any time you want:

```python
message.to.add('anotheruser@example.com', 'me@example.com')
```

same rule applies to `to`, `from_address`, `cc`, `bcc`, `reply_to` fields.

## Compose messages

The arguments and methods of `Email ` class are self-explanatory so here is an kick-start example:

```python
from mailers import Email

message = Email(
    to='user@localhost',
    from_address='from@example.tld',
    cc='cc@example.com',
    bcc=['bcc@example.com'],
    text='Hello world!',
    html='<b>Hello world!</b>',
)
```

`cc`, `bcc`, `to`, `reply_to` can be either strings or lists of strings.

### Global From address

Instead of setting "From" header in every message, you can set it mailer-wide. Use `from_address` argument of Mailer
class:

```python
mailer = Mailer(from_address="sender@localhost")
```

The mailer will set From header with the given value to all messages that do not container From or Sender headers.

## Using templates

You can use any template engine with a special email class called `TemplatedEmail`. This class extends `Email` with
following arguments:

* `html_template`  - a template for use in HTML part
* `text_template`  - a template for use in text part
* `context` - a template context

Then, you need to use appropriate plugin that can render the email message.

Out of the box, we provide a Jinja adapter.

### Use Jinja2 engine

You can use Jinja template engine to render your emails. Add `JinjaRendererPlugin` with a
preconfigured `jinja2.Environment` instance. Then, use `mailers.TemplatedEmail` instead of `mailers.Email` to configure
templated mail.

```python
import jinja2

from mailers import Mailer, TemplatedEmail
from mailers.plugins.jinja_renderer import JinjaRendererPlugin

env = jinja2.Environment(loader=jinja2.FileSystemLoader(['templates']))
mailer = Mailer(plugins=[JinjaRendererPlugin])

email = TemplatedEmail(subject='Hello', text_template='mail.txt', html_template='mail.html', context={'user': 'root'})
mailer.send(email)
```

## Attachments

Use `attach`, `attach_from_path`, `attach_from_path_sync` methods to attach files.

```python
from mailers import Email

message = Email(to='user@localhost', from_address='from@example.tld', text='Hello world!')

# attachments can be added on demand
await message.attach_from_path('file.txt')

# or use blocking sync version
message.attach_from_path_sync('file.txt')

# attach from variable
message.attach('CONTENTS', 'file.txt', 'text/plain')
```

## Embedding files

In the same way as with attachments, you can inline files into your messages. This is commonly used to display embedded
images in the HTML body. Here are method you can use `embed`, `embed_from_path`, `embed_from_path_sync`.

```python
from mailers import Email

message = Email(
    to='user@localhost',
    from_address='from@example.tld',
    html='Render me <img src="cid:img1">',
)

await message.embed_from_path(path='/path/to/image.png', name='img1')
```

Note, that you have to add HTML part to embed files. Otherwise, they will be ignored.

## Message signatures

You can sign messages (e.g. with DKIM) by passing `signer` argument to the `Mailer` instance.

```python
signer = MySigner()
mailer = Mailer(..., signer=signer)

# or
mailer = create_mailer(..., signer=signer)
```

### DKIM signing

You may wish to add DKIM signature to your messages to prevent them from being put into the spam folder.

Note, you need to install [`dkimpy`](https://pypi.org/project/dkimpy/) package before using this feature.

```python
from mailers import create_mailer
from mailers.signers.dkim import DKIMSigner

signer = DKIMSigner(selector='default', private_key_path='/path/to/key.pem')

# or you can put key content using private_key argument
signer = DKIMSigner(selector='default', private_key='PRIVATE KEY GOES here...')

mailer = create_mailer('smtp://', signer=signer)
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

You can pass multiples transports to the Mailer instance and it will iterate over them asking each to send a message. By
default, the first transport is used but if it fails to send the message, the mailer will retry sending with the next
transport in the chain.

```python
mailer = Mailer([transport1, transport2, ..., transportN])
```

## Plugins

Plugins let you inspect and modify outgoing messages before or after they are sent. The plugin is a class that
implements `mailers.plugins.Plugin` protocol. Plugins are added to mailers via `plugins` argument.

Below you see an example plugin:

```python
from email.message import Message

from mailers import BasePlugin, create_mailer, Mailer, SentMessages


class PrintPlugin(BasePlugin):

    async def on_before_send(self, message: Message) -> None:
        print('sending message %s.' % message)

    async def on_after_send(self, message: Message, sent_messages: SentMessages) -> None:
        print('message has been sent %s.' % message)

    async def on_send_error(self, message: Message, sent_messages: SentMessages) -> None:
        print('error sending message %s.' % message)


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

### Custom transports.

Each transport must extend `mailers.transports.Transport` base class.

```python
import typing as t
from email.message import Message
from mailers import Mailer, Transport, EmailURL, SentMessage


class PrintTransport(Transport):
    @classmethod
    def from_url(cls, url: t.Union[str, EmailURL]) -> t.Optional[Transport]:
        # this method is optional,
        # if your transport does not support instantiation from URL then return None here.
        # returning None is the default behavior
        return None

    async def send(self, message: Message) -> SentMessage:
        print(str(message))
        return SentMessage(True, message, self)


mailer = Mailer(PrintTransport())
```

The library will call `Transport.from_url` when it needs to instantiate the transport instance from the URL. It is ok to
return `None` as call result then the transport will be instantiated using construction without any arguments passed.

Once you have defined a new transport, register a URL protocol for it:

```python
add_protocol_handler('print', PrintTransport)
mailer = Mailer('print://')
```
