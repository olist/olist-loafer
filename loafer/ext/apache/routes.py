from ...routes import Route
from .providers import KafkaSimpleProvider


class KafkaRoute(Route):
    def __init__(self, provider_queue, provider_options=None, *args, **kwargs):
        provider_options = provider_options or {}
        provider = KafkaSimpleProvider(provider_queue, **provider_options)
        kwargs["provider"] = provider

        if "name" not in kwargs:
            kwargs["name"] = provider_queue

        super().__init__(*args, **kwargs)
