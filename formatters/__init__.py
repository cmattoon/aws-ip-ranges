"""
Formatters to support a variety of output formats.
"""
from typing import List

from .formatter import Formatter
from .json_formatter import JSONFormatter
from .yaml_formatter import YAMLFormatter
from .text_formatter import TextFormatter

from .cidr_formatter import CidrFormatter
from .iptables_formatter import IptablesFormatter
from .nginx_formatter import NginxFormatter
from .haproxy_formatter import HAProxyFormatter


def Get(code: str, data) -> Formatter:
    formatter = Formatter.get_formatter(code)
    return formatter(data)


def List() -> List[str]:
    return [s.code for s in Formatter.__subclasses__()]
