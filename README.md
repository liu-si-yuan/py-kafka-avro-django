Django Kafka, Avro
==================

(optional*) Django, integration with kafka, (optionally*) with avro .avsc files

Simple services that __consumes__ or __produces__ data from and to a kafka instance.
Optionally, you are able to encode and decode json data into binary serialized form with avro .avsc files.

A simple KafkaConsumerService and KafkaProducerService that you dependency inject settings into.

Consumer
--------

```
from django-kafka-avro.services import KafkaConsumerservice
service = KafkaConsumerService()
topic = 'MyKafkaTopic'
service.process(topic)

# Optionally you can pass in a path to a .avsc schema file
# Please note: process yields data
for json_message, original_message in service.process(topic, schema='/path/to/MyKafkaTopic.avsc'):
    print((json_message, original_message))

# Otherwise the path will be calculated from the KAFKA_CONFIG.AVRO_PATH setting
# If no KAFKA_CONFIG.AVRO_PATH is present then no decoding will take place (assumes its just json on the kafka instance
```


Producer
--------

```
from django-kafka-avro.services import KafkaProducerService
service = KafkaProducerService()
topic = 'MyKafkaTopic'
data = json.load('/path/to/data.json') # or json data from somwhere else
service.process(topic, data)

# Optionally you can pass in a path to a .avsc schema file
service.process(topic, data, schema='/path/to/MyKafkaTopic.avsc')
# Otherwise the path will be calculated from the KAFKA_CONFIG.AVRO_PATH setting
# If no KAFKA_CONFIG.AVRO_PATH is present then no decoding will take place (assumes its just json on the kafka instance
```
