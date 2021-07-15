class ProviderError(Exception):
    pass


class ProviderRuntimeError(ProviderError):
    pass


class ConfigurationError(Exception):
    pass


class LoaferException(Exception):
    pass


class DeleteMessage(LoaferException):
    pass
