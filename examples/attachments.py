"""This example demonstrates how to add attachments to your message.

You need to setup several environment variables before you can use this script:

* MAILERS_RECIPIENT - a recipient's email ("To" header)
* MAILERS_FROM_ADDRESS - a sender address ("From" header)
* MAILER_URL - mailer configuration URL
"""
import asyncio
import os
import tempfile

from mailers import Attachment, EmailMessage, create_mailer


async def main():
    with tempfile.NamedTemporaryFile('w') as tmp_file:
        tmp_file.write('temp file contents')
        tmp_file.seek(0)

        message = EmailMessage(
            to=os.environ.get('MAILERS_RECIPIENT', 'root@localhost'),
            subject='Attachments test',
            text_body='Hello, this is a test message with attachments.',
            from_address=os.environ.get('MAILERS_FROM_ADDRESS', 'root@localhost'),
            attachments=[
                Attachment('file1_raw.txt', 'file1 content', 'text/plain'),
            ],
        )

        # inline attachments
        message.add_attachment(Attachment('file2_inline.txt', 'file2 content', 'text/plain', disposition='inline'))

        # attach files dynamically
        message.add_attachment(Attachment('file3_dyn.txt', 'file3 content', 'text/plain'))

        # unicode file names
        message.add_attachment(Attachment('имя файла_cyr.txt', 'file3 content', 'text/plain'))

        # unicode file contents
        message.add_attachment(Attachment('имя файла 2_cyr_content.txt', 'содержимое файла', 'text/plain'))

        # read from file
        await message.attach_file(tmp_file.name, 'file4.tmp')

        mailer = create_mailer(os.environ.get('MAILER_URL', 'null://'))
        await mailer.send(message)


if __name__ == '__main__':
    asyncio.run(main())
