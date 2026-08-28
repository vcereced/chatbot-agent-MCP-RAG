class HttpException(Exception):

    def __init__(
        self,
        status_code: int,
        message: str,
        url: str | None = None
    ):
        self.status_code = status_code
        self.url = url
        super().__init__(message)