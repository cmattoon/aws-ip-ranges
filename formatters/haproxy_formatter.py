from .formatter import Formatter

class HAProxyFormatter(Formatter):
    """
    acl aws_ips src 203.0.113.0/24 198.51.100.0/24
    http-request allow if aws_ips
    http-request deny
    """
    code = 'haproxy'
    def string(self):
        raise NotImplementedError("Not implemented yet!")
