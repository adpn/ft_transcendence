import json
from django.core.serializers.json import DjangoJSONEncoder

class ItemSerializer:

    @staticmethod
    def serialize(item):
        return {
            'id': item.id,
            'name': item.name,
            'description': item.description,
        }

    @staticmethod
    def serialize_many(items):
        return [ItemSerializer.serialize(item) for item in items]
