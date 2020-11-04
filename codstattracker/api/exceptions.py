class FetchError(Exception):
    pass


class PlayerNotFoundError(FetchError):
    pass


class UnrecoverableFetchError(Exception):
    pass
