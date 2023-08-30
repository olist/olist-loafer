class ProviderError(Exception):
    pass


class ProviderRuntimeError(ProviderError):
    pass


class LoaferException(Exception):
    pass


class DeleteMessage(LoaferException):
    pass
