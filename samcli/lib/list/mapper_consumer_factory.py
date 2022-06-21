"""
The factory for returning the appropriate mapper and consumer
"""
from samcli.lib.list.list_interfaces import MapperConsumerFactoryInterface
from samcli.lib.list.data_to_json_mapper import DataToJsonMapper
from samcli.commands.list.json_consumer import JsonConsumer
from samcli.lib.list.mapper_consumer_container import MapperConsumerContainer


class MapperConsumerFactory(MapperConsumerFactoryInterface):
    def create(self, producer, output):
        # Will add conditions here to return different sorts of containers later on
        data_to_json_mapper = DataToJsonMapper()
        json_consumer = JsonConsumer()
        container = MapperConsumerContainer(mapper=data_to_json_mapper, consumer=json_consumer)
        return container
