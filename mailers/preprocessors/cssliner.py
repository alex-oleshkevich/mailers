from email.message import EmailMessage, MIMEPart

import css_inline


def _process(part: MIMEPart) -> MIMEPart:
    # https://github.com/Stranger6667/css-inline/tree/master/bindings/python
    inliner = css_inline.CSSInliner()

    content = part.get_content()
    part.set_content(
        # set_content requires a byte literal, not a string
        inliner.inline(content).encode("utf-8"),
        maintype="text",
        subtype="html",
    )
    return part


def css_inliner(message: EmailMessage) -> EmailMessage:
    """
    Search for any HTML part that is not attachment and inline CSS.

    Modified MIME part in-place.
    """
    if message.get_content_type() == "text/html":
        if not message["content-disposition"]:
            _process(message)

    if message.get_content_type() in [
        "multipart/alternative",
        "multipart/mixed",
        "multipart/related",
    ]:
        for part in message.get_payload():
            css_inliner(part)

    return message
