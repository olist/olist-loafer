try:
    import aiobotocore  # noqa
except ImportError:
    pass
else:
    from .handlers import SNSHandler, SQSHandler
    from .message_translators import SNSMessageTranslator, SQSMessageTranslator
    from .providers import SQSProvider
    from .routes import SNSQueueRoute, SQSRoute

    __all__ = [
        "SNSHandler",
        "SNSMessageTranslator",
        "SNSQueueRoute",
        "SQSHandler",
        "SQSMessageTranslator",
        "SQSProvider",
        "SQSRoute",
    ]
