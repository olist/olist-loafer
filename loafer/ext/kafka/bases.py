import inspect

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer


class KafkaService:
    def __init__(self, topic_name, client_options):
        self._topic_name = topic_name

        producer_arguments = inspect.getfullargspec(AIOKafkaProducer.__init__)
        self._producer_options = {
            name: value for name, value in client_options.items() if name in producer_arguments.kwonlyargs
        }

        consumer_arguments = inspect.getfullargspec(AIOKafkaConsumer.__init__)
        self._consumer_options = {
            name: value for name, value in client_options.items() if name in consumer_arguments.kwonlyargs
        }

    def get_producer(self):
        return AIOKafkaProducer(**self._producer_options)

    def get_consumer(self):
        return AIOKafkaConsumer(self._topic_name, **self._consumer_options)
