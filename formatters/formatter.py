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
        return dataclasses.is_dataclass(self.data)
    
