import toronado
from email.message import EmailMessage, MIMEPart


def _process(part: MIMEPart) -> MIMEPart:
    content = part.get_content()
    part.set_payload(toronado.from_string(content))
    return part


def css_inliner(message: EmailMessage) -> EmailMessage:
    """
    Search for any HTML part that is not attachment and inline CSS.

    Modified MIME part in-place.
    """
    if message.get_content_type() == "text/html":
        if not message["content-disposition"]:
            _process(message)

    if message.get_content_type() in ["multipart/alternative", "multipart/mixed"]:
        for part in message.get_payload():
            css_inliner(part)

    return message
