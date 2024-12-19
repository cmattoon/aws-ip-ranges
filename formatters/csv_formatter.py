from .formatter import Formatter

class CSVFormatter(Formatter):
    """
    IP Prefix,Region,Service,Network Border Group
    203.0.113.0/24,us-west-2,AMAZON,us-west-2
    198.51.100.0/24,us-east-1,S3,us-east-1
    """
    code = 'csv'
    
    def string(self):
        raise NotImplementedError("Not implemented!")
