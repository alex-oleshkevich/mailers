from .mailer import get_mailer
from .message import EmailMessage


async def send(message: EmailMessage, mailer: str = 'default') -> None:
    """Send a message."""
    await get_mailer(mailer).send(message)
