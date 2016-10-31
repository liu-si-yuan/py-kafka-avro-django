import io
import os
import avro.io
import avro.schema

from kafka import KafkaConsumer, KafkaProducer

import logging
logger = logging.getLogger(__name__)


class BaseKafkaService(object):
    """
    A Consumer for kafka that will produce json data
    provided for by converting from avro files
    """
    def __init__(self, config={}):
        self.auto_offset_reset = config.get('KAFKA_OFFSET', os.getenv('KAFKA_OFFSET', 'earliest'))
        self.avro_path = config.get('AVRO_PATH', os.getenv('KAFKA_AVRO_PATH', None))
        self.brokers = config.get('KAFKA_BROKERS', os.getenv('KAFKA_BROKERS', 'localhost:2181'))

        try:
            iter(self.brokers)
        except TypeError:
            raise Exception('KAFKA_BROKERS must be a list')

        self.client_id = 'dgl-%s-%s' % (config.get('PROJECT_ENVIRONMENT','development'), os.getenv('USER'))
        self.group_id = 'dgl-consumer-%s-%s' % (config.get('PROJECT_ENVIRONMENT','development'), os.getenv('USER'))

    def _decode(self, msg, schema):
        if schema is None:
            #
            # No schema defined must be plain json
            #
            return msg

        bytes_reader = io.BytesIO(msg.value)
        decoder = avro.io.BinaryDecoder(bytes_reader)
        reader = avro.io.DatumReader(schema)
        return reader.read(decoder)

    def _schema(self, topic, schema=None):
        """
        Read the passed in schema or try to guess the schema
        based on the topic name
        """
        if self.avro_path is None:
            return None

        schema = '%s.avsc' % topic if schema is None else schema
        avro_path = os.path.join(self.avro_path, schema)
        return avro.schema.parse(open(avro_path, "rb").read())

    def _writer(self, schema):
        schema = self._schema
        if schema is None:
            return None, None, None

        writer = avro.io.DatumWriter(self._schema)
        bytes_writer = io.BytesIO()
        encoder = avro.io.BinaryEncoder(bytes_writer)
        return (writer, bytes_writer, encoder)


class KafkaConsumerService(BaseKafkaService):
    """
    A Consumer for kafka that will produce json data
    provided for by converting from avro files
    """
    def __init__(self, *args, **kwargs):
        super(KafkaConsumerService, self).__init__(*args, **kwargs)
        self.consumer = None

    def process(self, topic, schema=None):
        """
        Iterator that yields json results and their message
        """
        self.consumer = KafkaConsumer(topic,
                                      client_id=self.client_id,
                                      group_id=self.group_id,
                                      auto_offset_reset=self.auto_offset_reset,
                                      enable_auto_commit=False,
                                      bootstrap_servers=self.brokers)

        schema = self._schema(topic=topic,
                              schema=schema)

        for message in self.consumer:
            # try:
            json_msg = self._decode(msg=message, schema=schema)
            # except Exception as e:
            #     logger.error('Exception decoding Kafka Message: %s' % e)
            #     import pdb;pdb.set_trace()
            #     json_msg = {}

            yield (json_msg, message)


class KafkaProducerService(BaseKafkaService):
    """
    A Consumer for kafka that will produce json data
    provided for by converting from avro files
    """
    def __init__(self, *args, **kwargs):
        super(KafkaProducerService, self).__init__(*args, **kwargs)
        self.producer = KafkaProducer(bootstrap_servers=self.brokers)

    def _transmit(self, topic, raw_bytes):
        return self.producer.send(topic, raw_bytes)

    def process(self, topic, data):
        """
        Loop over json data and write to binary and then send
        """
        writer, bytes_writer, encoder = self._writer()
        if writer is None and bytes_writer is None and encoder is None:
            raw_bytes = json.dumps(data)
        else:
            for msg in data:
                writer.write(msg, encoder)
            raw_bytes = bytes_writer.getvalue()

        return self._transmit(topic, raw_bytes)
