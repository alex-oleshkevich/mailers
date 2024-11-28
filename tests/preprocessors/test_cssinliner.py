import base64
from email.message import EmailMessage

from mailers import Email
from mailers.preprocessors.cssliner import css_inliner


def test_css_inliner_with_html_only_message() -> None:
    html = """<style>.text {color: red; }</style><p class="text">hello</p>"""
    message = EmailMessage()
    message.set_content(html, subtype="html", charset="utf-8")
    message = css_inliner(message)

    assert message.get_content() == (
        '<html><head></head><body><p class="text" style="color: red;">hello</p>\n</body></html>'
    )


def test_css_inliner_with_text_only_message() -> None:
    html = """<style>.text {color: red; }</style><p class="text">hello</p>"""
    message = EmailMessage()
    message.set_content(html, subtype="plain", charset="utf-8")
    message = css_inliner(message)
    assert message.get_content() == ('<style>.text {color: red; }</style><p class="text">hello</p>\n')


def test_css_inliner_with_multipart_message() -> None:
    html = """<style>.text {color: red; }</style><p class="text">hello</p>"""
    message = EmailMessage()
    message.set_content(html, subtype="plain", charset="utf-8")
    message.add_alternative(html, subtype="html", charset="utf-8")
    message = css_inliner(message)
    assert message.get_payload()[0].get_content() == '<style>.text {color: red; }</style><p class="text">hello</p>\n'
    assert message.get_payload()[1].get_content() == (
        '<html><head></head><body><p class="text" style="color: red;">hello</p>\n</body></html>'
    )


def test_css_inliner_with_multipart_with_attachments_message() -> None:
    html = """<style>.text {color: red; }</style><p class="text">hello</p>"""
    email = Email(text=html, html=html)
    email.attach(html, "index.html", "text/html")
    message = email.build()

    message = css_inliner(message)
    assert message.get_payload()[0].get_payload()[0].get_content() == (
        '<style>.text {color: red; }</style><p class="text">hello</p>\n'
    )
    assert message.get_payload()[0].get_payload()[1].get_content() == (
        '<html><head></head><body><p class="text" style="color: red;">hello</p>\n</body></html>'
    )
    assert base64.b64decode(message.get_payload(1).get_payload()) == html.encode()
