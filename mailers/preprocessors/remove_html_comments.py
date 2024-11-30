import re
from email.message import EmailMessage, MIMEPart
from typing import Callable


def remove_with_re(html: str):
    # https://stackoverflow.com/questions/28208186/how-to-remove-html-comments-using-regex-in-python
    return re.sub("(<!--.*?-->)", "", html, flags=re.DOTALL)


def remove_with_bs4(html: str):
    from bs4 import BeautifulSoup, Comment

    soup = BeautifulSoup(html, "html.parser")

    # Find all comments
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))

    # Remove each comment
    for comment in comments:
        comment.extract()

    # Return the modified HTML as a string
    return str(soup)


def update_part_inline(part: MIMEPart, callback: Callable) -> MIMEPart:
    content = part.get_content()
    updated_content = callback(content)

    # set_content requires a byte literal, not a string
    if isinstance(updated_content, str):
        updated_content = updated_content.encode("utf-8")
    elif not isinstance(updated_content, bytes):
        raise TypeError(f"Expected str or bytes, got {type(updated_content)}")

    part.set_content(
        updated_content,
        maintype="text",
        subtype="html",
    )

    return part


try:
    import bs4  # noqa

    removal_strategy = remove_with_bs4
except ImportError:
    removal_strategy = remove_with_re


def remove_html_comments(message: EmailMessage) -> EmailMessage:
    if message.get_content_type() == "text/html":
        if not message["content-disposition"]:
            update_part_inline(message, removal_strategy)

    if message.get_content_type() in [
        "multipart/alternative",
        "multipart/mixed",
        "multipart/related",
    ]:
        for part in message.get_payload():
            # recurse!
            remove_html_comments(part)  # type: ignore

    return message
