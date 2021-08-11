import asyncio

import mailers


async def main():
    mailers.add_mailer('smtp://localhost:1025')
    await mailers.send(
        to=[('root@localhost', 'Root')],
        subject='Hello',
        text_body='This is message body',
    )


if __name__ == '__main__':
    asyncio.run(main())
