import yaml
import dataclasses
from .formatter import Formatter

class YAMLDumper(yaml.Dumper):
    def represent_data(self, data):
        """Implements yaml.Dumper"""
        if dataclasses.is_dataclass(data):
            data = dataclasses.asdict(data)
        return super().represent_data(data)

class YAMLFormatter(Formatter):
    """Support YAML dumping for dataclasses"""
    code = 'yaml'

    def string(self):
        """Implements Formatter.string"""
        return yaml.dump(
            self.data,
            default_flow_style=False,
            Dumper=YAMLDumper
        )
