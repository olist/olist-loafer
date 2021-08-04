from dataclasses import asdict

from loafer.message_translators import AbstractMessageTranslator


class KafkaMessageTranslator(AbstractMessageTranslator):
    def translate(self, message):
        metadata = asdict(message)
        content = metadata.pop("value")
        translated = {"content": content, "metadata": metadata}
        return translated
