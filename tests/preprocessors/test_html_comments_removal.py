import base64
from email.message import EmailMessage

from mailers import Email
from mailers.preprocessors.remove_html_comments import remove_html_comments


def test_css_inliner_with_no_comment() -> None:
    html = """<p class="text">hello</p>\n"""
    message = EmailMessage()
    message.set_content(html, subtype="html", charset="utf-8")
    message = remove_html_comments(message)

    assert message.get_content() == '<p class="text">hello</p>\n'


def test_html_comment_remover_with_single_comment() -> None:
    html = """<!-- I am a comment --><p class="text">hello</p>\n"""
    message = EmailMessage()
    message.set_content(html, subtype="html", charset="utf-8")
    message = remove_html_comments(message)

    assert message.get_content() == '<p class="text">hello</p>\n'


def test_html_comment_remover_with_multiple_comment() -> None:
    html = """<!-- I am a comment --><p class="text">hello</p><!-- me too -->\n"""
    message = EmailMessage()
    message.set_content(html, subtype="html", charset="utf-8")
    message = remove_html_comments(message)

    assert message.get_content() == '<p class="text">hello</p>\n'


def test_css_inliner_with_text_only_message() -> None:
    html = """<!-- I am a comment -->but I am not html\n"""
    message = EmailMessage()
    message.set_content(html, subtype="plain", charset="utf-8")
    message = remove_html_comments(message)
    assert message.get_content() == html


def test_css_inliner_with_multipart_message() -> None:
    html = """<!-- I am a comment --><p class="text">hello</p>\n"""
    message = EmailMessage()
    message.set_content(html, subtype="plain", charset="utf-8")
    message.add_alternative(html, subtype="html", charset="utf-8")
    message = remove_html_comments(message)

    assert (
        message.get_payload()[0].get_content()
        == '<!-- I am a comment --><p class="text">hello</p>\n'
    )
    assert message.get_payload()[1].get_content() == '<p class="text">hello</p>\n'


def test_css_inliner_with_multipart_with_attachments_message() -> None:
    html = """<!-- I am a comment --><p class="text">hello</p>\n"""
    email = Email(text=html, html=html)
    email.attach(html, "index.html", "text/html")
    message = email.build()

    message = remove_html_comments(message)
    assert (
        message.get_payload()[0].get_payload()[0].get_content()
        == '<!-- I am a comment --><p class="text">hello</p>\n'
    )

    assert (
        message.get_payload()[0].get_payload()[1].get_content()
        == '<p class="text">hello</p>\n'
    )

    assert base64.b64decode(message.get_payload(1).get_payload()) == html.encode()
