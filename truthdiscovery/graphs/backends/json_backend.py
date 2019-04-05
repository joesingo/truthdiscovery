import json

from truthdiscovery.graphs.backends.base import BaseBackend
from truthdiscovery.graphs.entities import Entity


class JsonBackend(BaseBackend):
    """
    Serialise entities to draw as a JSON document
    """
    def draw_entities(self, entities, outfile, width, height):
        obj = {
            "width": width,
            "height": height,
            "entities": [JsonBackend.entity_to_dict(e) for e in entities]
        }
        json.dump(obj, outfile)

    @classmethod
    def entity_to_dict(cls, entity):
        """
        :return: a dict representation of an :any:`Entity` object
        """
        if not isinstance(entity, Entity):
            return entity

        obj = {"type": entity.__class__.__name__.lower()}
        for name, val in entity.__dict__.items():
            obj[name] = cls.entity_to_dict(val)
        return obj
