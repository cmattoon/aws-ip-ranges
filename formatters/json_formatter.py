import json
import dataclasses

from .formatter import Formatter

class JSONEncoder(json.JSONEncoder):    
    def default(self, o):
        """Support json.dumps on dataclasses"""
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)    


class JSONFormatter(Formatter): #, json.JSONEncoder):
    code = 'json'

    def string(self) -> str:
        """
        Return the data as a JSON-encoded string.
        """
        return json.dumps(self.data, cls=JSONEncoder)
