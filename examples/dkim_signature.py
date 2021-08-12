"""This example demonstrates how to add DKIM signature to your outgoing messages."""
import asyncio

from mailers import EmailMessage, create_mailer
from mailers.plugins.dkim import DkimSignature

KEY = """
-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQDRVrMsRzzvL/Qu7iHK2eG6+45ffgde94m+Z4MDQahKlqetisYZ
pQM8XZbpM0ZGk8qA3/YnFhzviVQPM9NyRbSTbKNN6k2YoW35qncXH5EgC/Ck6+ko
p+pz3IsIiMo0x75NmiojLg40Ldmf++/8IFVwK9NjYQILlKZtjO4EdO+c0wIDAQAB
AoGANpKwoQFtTDmnIbjozFYit7kus4xKZaKIoT+g8u9h7Rf7XI2J+VOAVXNcjSzV
zD5pE1HPfP8Rygx2AoSTQf4UBcYH8ZSf/FgRXqNwud0fMlvv3gK6cxLWTSsgiubr
U49UmtLQDV1vOlqdgvK4HoJqlOmBUt+J9hZcLExe8NUrCrECQQDw2CNyledl4hgL
twXmIq2PaxaBMU++RtTMIxTFHDexKT7jmoGhVsnHDxCacIt6rrVdUN1I59fGpbn8
V/RcPtWLAkEA3oMGMrVLnGgaqqwHfLF6Xa5yu5B80TmJBC77o5SonTXNb95twgzf
O76YMBwfj6dPJWIMSsPyFJpd0ZkG0d0O2QJBAMtxyH/CoPUvR6Cduh3srS+5Bgmb
3gCdVKQb/i+C5oiAjt80ZMwkw82irCPJbgj0C8AHzuUG8v6af8Dpi0Fg0oECQEDP
pzGD7wcap5HI09F1HHBHDLInTsPeX1Nxn+gwt8A62KDaB9w6xZbwWAHDX0oHcJ0x
5uSsGEn6AJO5X+wm2FkCQFBoCCVACXeqN0Fs+PYwbdqrtn9vt4wO4WSypz6P1tXO
MuRuBEKTlsqG1tdkQQhwKMcv9mwnDTakFNzMPF3r+f0=
-----END RSA PRIVATE KEY-----
"""


async def main():
    message = EmailMessage(
        to=['alex.oleshkevich@gmail.com', 'test-rlmyki1by@srv1.mail-tester.com'],
        subject='Hello',
        text_body='World',
        from_address='reply@aliashkevich.com',
    )
    mailer = create_mailer(
        'smtp://localhost:25',
        plugins=[
            DkimSignature(
                dkim_selector='dkimtest._domainkey',
                dkim_key=KEY,
            )
        ],
    )
    await mailer.send(message)


if __name__ == '__main__':
    asyncio.run(main())
