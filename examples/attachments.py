"""This example demonstrates how to add attachments to your message.

You need to setup several environment variables before you can use this script:

* MAILERS_RECIPIENT - a recipient's email ("To" header)
* MAILERS_FROM_ADDRESS - a sender address ("From" header)
* MAILER_URL - mailer configuration URL
"""
import asyncio
import os
import tempfile

from mailers import create_mailer
from mailers.message import Email

MAILER_URL = os.environ.get('MAILER_URL', 'null://')
MAILERS_RECIPIENT = os.environ.get('MAILERS_RECIPIENT', 'root@localhost')
MAILERS_FROM_ADDRESS = os.environ.get('MAILERS_FROM_ADDRESS', 'sender@localhost')


async def main():
    with tempfile.NamedTemporaryFile('w') as tmp_file:
        tmp_file.write('temp file contents')
        tmp_file.seek(0)

        message = Email(
            to=MAILERS_RECIPIENT,
            subject='Attachments test',
            text='Hello, this is a test message with attachments.',
            from_address=MAILERS_FROM_ADDRESS,
        )

        # attach files dynamically
        message.attach('file3 content', 'file3_dyn.txt', 'text/plain')

        # unicode file names
        message.attach('file3 content', 'имя файла_cyr.txt', 'text/plain')

        # unicode file contents
        message.attach('содержимое файла', 'имя файла 2_cyr_content.txt', 'text/plain')

        # read from file asynchronously
        await message.attach_from_path(tmp_file.name, 'file_async.tmp')

        # read from file synchronously
        message.attach_from_path_sync(tmp_file.name, 'file_sync.tmp')

        mailer = create_mailer(MAILER_URL)
        await mailer.send(message)


if __name__ == '__main__':
    asyncio.run(main())
