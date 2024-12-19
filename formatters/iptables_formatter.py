
from .formatter import Formatter

class IptablesFormatter(Formatter):
    """
    Return iptables commands, like:
        iptables -A INPUT -s 203.0.113.0/24 -p tcp --dport 443 -j ACCEPT
        iptables -A INPUT -s 198.51.100.0/24 -p tcp --dport 80 -j ACCEPT
    """
    
    code = 'iptables'
    def string(self):
        pass

