"""This is a very basic example."""
import asyncio

from mailers import EmailMessage, create_mailer


async def main():
    mailer = create_mailer('smtp://localhost:1025')
    await mailer.send(
        EmailMessage(
            to='root@localhost',
            subject='Hello',
            text_body='World',
            from_address='reply@localhost',
        )
    )


if __name__ == '__main__':
    asyncio.run(main())
