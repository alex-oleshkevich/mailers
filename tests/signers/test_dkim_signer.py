import dkim
import pytest
import tempfile
import typing
from email.message import EmailMessage

from mailers import InMemoryTransport, Mailer
from mailers.message import Email
from mailers.signers.dkim import DKIMSigner

KEY = """-----BEGIN RSA PRIVATE KEY-----
MIICWwIBAAKBgQCjoXCMgp381vHOdixYTXXxIb+znulOdvq9lWr8U/eJIC/hmAZh
CqbKJO/OIobDFn/eb68zSnzaxu0OUSkrAXCFoEeL/aBcnKGWxLQnxw7mEzYlC/n8
Swgn4OvwuQL2AMZ8d6oKSRvr7iVW9ZRUqw017IUSMbGDwgHnXAC/8dn9kwIDAQAB
AoGAEn79KeTZ1uq1CpFxEcovusIF2VftJ2FrlmJ9ZWhYYrewsd9tWSrLD659LN/a
O9MfQRV+yF1zH4e85BFohePzw/i9nmujbmBPSxdXSL056BeSKSf6skAOPqN/lOUt
Mng96MwzwccWXscQLaBVBlxUms1KxK6TcxGIxT6G4gzH94ECQQDT99D1eXKdV6Gq
iGjvgP21mZSRmVKS46VWxfou5bDPFSEybtWP+vwsqaPA83I3gMdnYqzlyDFBU7j7
YwSyUvGdAkEAxZ8aXco7JYVHQeYTSEH5dHrPtoMkpeEZbOe/FWB2NzV3rDFSwj8k
7KWPP5hcC8Y9zESbtlfZPevfnHcB5Q5c7wJAV3jr9XER2FaCc6JpU3Tyvg9L3S3d
gpqI758xmErXRQ3eLjbI0OrtR+0Vk5mjJ75wC30QBp8vnFrVeoApPwG1jQJAYKpP
olr+jX7g+SoKeojS9ZfxLGx/q6gs4KmHPXSevqinrhG+UofCjwL4y/nB5HyG0/kn
VY0pFXHgQk+wHJPm/wJAT3qfgDC/0pMQ4nyXeRwxyZaddchiapJ/iULO8abAlQK1
BBl2Fhu5KS56Hze6tHtREpeJttpI1TMxwjaqFIFC7A==
-----END RSA PRIVATE KEY-----"""

DNS_RECORD = (
    "v=DKIM1;"
    "t=s;"
    "p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCjoXCMgp381vHOdixYTXXxIb+znulOdvq9lWr8U/eJIC/hmAZhCqbKJO/OIobDFn/"
    "eb68zSnzaxu0OUSkrAXCFoEeL/aBcnKGWxLQnxw7mEzYlC/n8Swgn4OvwuQL2AMZ8d6oKSRvr7iVW9ZRUqw017IUSMbGDwgHnXAC/8dn9kwIDAQAB"
)


def _get_txt(*args: typing.Any, **kwargs: typing.Any) -> str:
    return DNS_RECORD


@pytest.mark.asyncio
async def test_dkim_signer() -> None:
    mailbox: typing.List[EmailMessage] = []
    signer = DKIMSigner(selector="default", private_key=KEY)
    email = Email(from_address="sender@localhost", to="root@localhost", text="This is text content.")
    mailer = Mailer(InMemoryTransport(mailbox), signer=signer)
    await mailer.send(email)
    message = mailbox[0]
    assert dkim.verify(message.as_bytes(), dnsfunc=_get_txt)


@pytest.mark.asyncio
async def test_dkim_plugin_reads_key_from_file() -> None:
    with tempfile.NamedTemporaryFile("w") as f:
        f.write(KEY)
        f.seek(0)

        mailbox: typing.List[EmailMessage] = []
        transport = InMemoryTransport(mailbox)
        signer = DKIMSigner(selector="default", private_key_path=f.name)
        mailer = Mailer(transport, signer=signer)
        message = Email(
            to="root@localhost",
            subject="DKIM check",
            text="Hello, this is a test message to check the DKIM signature.",
            from_address="reply@localhost",
        )
        await mailer.send(message)
        sent_message = mailbox[0]
        assert dkim.verify(sent_message.as_bytes(), dnsfunc=_get_txt)
