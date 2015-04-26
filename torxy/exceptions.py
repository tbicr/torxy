class BaseException(Exception):

    pass


class BrowserNotFound(BaseException):

    pass


class IdentityNotChanged(BaseException):

    pass


class RestartTor(BaseException):

    pass
