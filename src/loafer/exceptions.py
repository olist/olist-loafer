class ProviderError(Exception):
    pass


class DeleteMessage(BaseException):  # technically not an Exception
    pass


class TerminateTaskGroup(BaseException):
    """Exception raised to terminate a task group."""
