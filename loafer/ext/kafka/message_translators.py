from loafer.message_translators import AbstractMessageTranslator


class KafkaMessageTranslator(AbstractMessageTranslator):
    def translate(self, message):
        value = message.value
        translated = {"content": value, "metadata": {}}
        return translated
