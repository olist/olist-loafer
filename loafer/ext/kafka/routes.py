from .message_translators import KafkaMessageTranslator
from .providers import KafkaProvider
from loafer.routes import Route


class KafkaRoute(Route):
    def __init__(self, topic_name, provider_options=None, *args, **kwargs):
        provider_options = provider_options or {}
        provider = KafkaProvider(topic_name, **provider_options)
        kwargs["provider"] = provider

        if "message_translator" not in kwargs:
            kwargs["message_translator"] = KafkaMessageTranslator()

        if "name" not in kwargs:
            kwargs["name"] = topic_name

        super().__init__(*args, **kwargs)
