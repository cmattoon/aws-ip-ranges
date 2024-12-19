from __future__ import annotations

import dataclasses

from abc import ABC, abstractmethod

class Formatter(ABC):
    # The --format <code> value
    code: str = ''
    
    def __init__(self, data, *args, **kwargs):
        self.data = data
        
        self._args = args
        self._kwargs = kwargs

    @abstractmethod
    def string(self) -> str:
        """
        Return a string representation of the data.

        This is the main function that subclasses must implement.
        Many of them will want to also take advantage of 'asdict()'
        """
        pass

    @classmethod
    def get_formatter(cls, code: str) -> Formatter:
        """
        Returns the formatter based on the code (flag value)

        Raises:
            ValueError when no format code is matched.

        Returns:
            Formatter
        """
        for sub in cls.__subclasses__():
            if sub.code == code:
                return sub
        raise ValueError(f"Unsupported format: {code}")

    def asdict(self):
        """Alias for dataclasses.asdict(self.data)"""
        return dataclasses.asdict(self.data)

    def is_dataclass(self):
        """Return True if self.data is a dataclass"""
        if type(self.data) is list:
            return any(dataclasses.is_dataclass(i) for i in self.data)
        elif type(self.data) is dict:
            return any(dataclasses.is_dataclass(v) for k,v in self.data.items())
        return dataclasses.is_dataclass(self.data)

    def is_list_of_ipranges(self):
        return \
            type(self.data) is list \
        and len(self.data) > 0 \
        and hasattr(self.data[0], 'ip_prefix') \
        and hasattr(self.data[0], 'ipv6_prefix')

    def deduplicate(self):
        """
        By default, Formatters simply format the data.
        However, it's useful for the ones that generate config files to deduplicate the data,
        since many IP ranges are used by multiple services.

        This is done by simple string matching and isn't subnet-aware.
        
        allow 98.88.0.0/13; # AWS AMAZON (us-east-1)
        allow 98.88.0.0/13; # AWS EC2 (us-east-1)
        
        allow 99.82.165.0/24; # AWS AMAZON (us-east-1)
        allow 99.82.165.0/24; # AWS GLOBALACCELERATOR (us-east-1)
        """
        if not self.is_list_of_ipranges():
            raise ValueError("This function is only meant to deduplicate IPRange data")
        
        data = {}
        for ip in self.data:
            prefix = ip.ip_prefix or ip.ipv6_prefix
            if prefix not in data:
                data[prefix] = []
            data[prefix].append(ip)
        return data

                
