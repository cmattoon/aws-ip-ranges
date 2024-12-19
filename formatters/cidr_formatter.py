from .formatter import Formatter

class CidrFormatter(Formatter):
    """
    Outputs a plaintext list of CIDR ranges only, like one might expect from a linux CLI tool.

    This is the same as the basic TextFormatter, but expects to work with "query" data instead of both "list" and "query".
    That is, it expects a list of IPRanges/dataclasses
    """
    code = 'cidr'
    def string(self):
        if not self.is_dataclass() and not type(self.data) is list:
            raise ValueError(f"This formatter expects to operate on a list of dataclasses")

        for item in self.data:
            try:
                v4 = getattr(item, 'ip_prefix')
                v6 = getattr(item, 'ipv6_prefix')
                if v4:
                    print(v4)
                elif v6:
                    print(v6)
            except AttributeError:
                raise ValueError(f"This formatter expects each list item to have 'ip_prefix' and 'ipv6_prefix'")
            
