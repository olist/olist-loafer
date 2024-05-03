class ProviderError(Exception):
    pass


class ProviderRuntimeError(ProviderError):
    pass


class LoaferError(Exception):
    pass


class DeleteMessage(LoaferError):  # noqa: N818
    pass
