"""This example demonstrates how to add attachments to your message."""
import asyncio
import os
import tempfile

from mailers import Attachment, EmailMessage, create_mailer


async def main():
    with tempfile.NamedTemporaryFile('w') as tmp_file:
        tmp_file.write('temp file contents')
        tmp_file.seek(0)

        message = EmailMessage(
            to=['root@localhost'],
            subject='Attachments test',
            text_body='Hello, this is a test message with attachments.',
            from_address='reply@localhost',
            attachments=[
                Attachment('file1.txt', 'file1 content', 'text/plain'),
            ],
        )

        # inline attachments
        message.add_attachment(Attachment('file2.txt', 'file2 content', 'text/plain', disposition='inline'))

        # attach files dynamically
        message.add_attachment(Attachment('file3.txt', 'file2 content', 'text/plain'))

        # unicode file names
        message.add_attachment(Attachment('имя файла.txt', 'file2 content', 'text/plain'))

        # unicode file contents
        message.add_attachment(Attachment('имя файла 2.txt', 'содержимое файла', 'text/plain'))

        # read from file
        await message.attach_file(tmp_file.name)

        mailer = create_mailer(os.environ.get('MAILER_URL', 'smtp://localhost:1025'))
        await mailer.send(message)


if __name__ == '__main__':
    asyncio.run(main())
