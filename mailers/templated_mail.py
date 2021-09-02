import typing as t

from mailers.message import Email


class TemplatedEmail(Email):
    """This is a special email type that allows you to define HTML and text templates.
    Then a corresponding plugin can use these templates to render HTML and plain text parts.

    See mailers.plugins.jinja_renderer for example."""

    def __init__(
        self,
        html_template: str = None,
        text_template: str = None,
        context: dict = None,
        *args: t.Any,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.html_template = html_template
        self.text_template = text_template
        self.context = context or {}
        self.context.update({'email': self})
