import jinja2

from mailers.message import Email
from mailers.plugins import BasePlugin
from mailers.templated_mail import TemplatedEmail


class JinjaRendererPlugin(BasePlugin):
    def __init__(self, env: jinja2.Environment) -> None:
        self.env = env

    def process_email(self, email: Email) -> Email:
        """Mailer calls it before sending."""
        if not isinstance(email, TemplatedEmail):
            return email

        if not email.html and email.html_template:
            template = self.env.get_template(email.html_template)
            email.html = template.render(email.context)

        if not email.text and email.text_template:
            template = self.env.get_template(email.text_template)
            email.text = template.render(email.context)

        return email
