from setuptools import setup

setup(
    name="py-kafka-avro-django",
    packages=['pykavdjang'],
    version='0.0.1',
    author="Ross Crawford-d'Heureuse",
    license="MIT",
    author_email="sendrossemail@gmail.com",
    url="https://github.com/rosscdh/py-kafka-avro-django",
    description="An app for querying or producing for Kafka and doing useful things",
    zip_safe=False,
    include_package_data=True,
    install_requires = [
        'avro',
        'python-snappy',
        'kafka-python',
    ]
)
