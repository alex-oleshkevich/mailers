"""Configuration via URL.

Based on https://github.com/encode/databases/blob/master/databases/core.py#L323
"""
import typing
from urllib.parse import SplitResult, parse_qsl, urlsplit


class EmailURL:
    _components: SplitResult

    def __init__(self, url: typing.Union[str, "EmailURL"]):
        self._url = str(url)

    @property
    def components(self) -> SplitResult:
        if not hasattr(self, "_components"):
            self._components: SplitResult = urlsplit(self._url)
        return self._components

    @property
    def transport(self) -> str:
        return self.components.scheme

    @property
    def username(self) -> typing.Optional[str]:
        return self.components.username

    @property
    def password(self) -> typing.Optional[str]:
        return self.components.password

    @property
    def hostname(self) -> typing.Optional[str]:
        return self.components.hostname

    @property
    def port(self) -> typing.Optional[int]:
        return self.components.port

    @property
    def netloc(self) -> str:
        return self.components.netloc

    @property
    def path(self) -> str:
        return self.components.path

    @property
    def options(self) -> typing.Dict:
        if not hasattr(self, "_options"):
            options = dict(parse_qsl(self.components.query))
            self._options = options
        return self._options

    def replace(self, **kwargs: typing.Any) -> "EmailURL":
        if "username" in kwargs or "password" in kwargs or "hostname" in kwargs or "port" in kwargs:
            hostname = kwargs.pop("hostname", self.hostname)
            port = kwargs.pop("port", self.port)
            username = kwargs.pop("username", self.username)
            password = kwargs.pop("password", self.password)

            netloc = hostname
            if port is not None:
                netloc += f":{port}"
            if username is not None:
                userpass = username
                if password is not None:
                    userpass += f":{password}"
                netloc = f"{userpass}@{netloc}"

            kwargs["netloc"] = netloc

        if "transport" in kwargs:
            transport = kwargs.pop("transport", self.transport)
            kwargs["scheme"] = f"{transport}"

        components = self.components._replace(**kwargs)
        return self.__class__(components.geturl())

    def __str__(self) -> str:
        return self._url

    def __repr__(self) -> str:
        url = str(self)
        if self.password:
            url = str(self.replace(password="********"))
        return f"{self.__class__.__name__}({repr(url)})"

    def __eq__(self, other: typing.Any) -> bool:
        return str(self) == str(other)
