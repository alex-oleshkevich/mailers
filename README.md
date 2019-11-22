# Mailers for asyncio

## Installation

```bash
pip install mailers
```

If you plan to use `FileTransport` you would also need to install 
[`aiofiles`](https://github.com/Tinche/aiofiles) extra:

```bash
pip install mailers[aiofiles]
```

Or install all optional dependencies at once:

```bash
pip install mailers[full]
```


## Usage

The package uses two main concepts: mailers and transports. 
The mailer is a class which abstracts you from the underlying transport
and the transport does the actual message delivery.

```python
from mailers import EmailMessage, configure, send_mail

configure(mailers={
    'default': 'smtp://user:password@localhost:25?timeout=2'
})

message = EmailMessage(
    to='user@localhost', from_address='from@localhost',
    subject='Hello', text_body='World!'
)
await send_mail('user@localhost', message)
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

### Shortcuts

The packages exports some utility methods to simplify the work: `configure` and `send_mail`.

`configure` methods allows to configure multiple mailers and bind URL specs at once.

```python
from mailers import configure

configure(
    mailers={
        'default': 'smtp://localhost',
        'admin': 'smtp://localhost'   
    },
    transports={
        'myproto': 'myproto.ImplementationClass'            
    }
)
``` 

In case you have multiple mailers, the `send_mail` shortcut accepts `mailer` argument to specify the mailer to use:
```python
send_mail(to, message, mailer='admin')
```


### Selecting mailers

When you have more 

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

`InMemoryTransport` takes a list and writes outgoing mail into it. 
Read this list to inspect the outbox.

```python
from mailers import InMemoryTransport, EmailMessage

message = EmailMessage()
mailbox = []
transport = InMemoryTransport(mailbox)
await transport.send(message)

assert message in mailbox
```

#### StreamTransport

Writes messages into the open stream.

```python
from mailers import StreamTransport, EmailMessage
from io import TextIO

message = EmailMessage()

transport = StreamTransport(output=TextIO())
await transport.send(message)
```

`output` is any IO compatible object.


### Custom transports.

Each transport must implement `async def send(self, message: EmailMessage) -> None` method. 
Preferably, inherit from `BaseTransport` class:

```python
from mailers import BaseTransport, Mailer, EmailMessage

class PrintTransport(BaseTransport):
    async def send(self, message: EmailMessage) -> None
        print(str(message))

mailer = Mailer(PrintTransport())
```

In order to make your transport to accept `EmailURL` instances, your transport class has to implement `from_url` 
class method:

```python
from mailers import BaseTransport, EmailMessage, EmailURL

class PrintTransport(BaseTransport):
    @classmethod
    def from_url(cls, url: EmailURL) -> "PrintTransport":
        return cls()
```

### Add custom transport protocols.

Once you build a custom transport you can add it's URL to enable URL-based configurations.
```python
from mailers import Transports, Mailer

Transports.bind_url('myprotocol', 'my.transport.Name')

mailer = Mailer('myprotocol://')
``` 

Note that the transport must to implement `from_url` method to accept URL parameters.
Otherwise it will be constructed without any arguments passed to the `__init__` method.
