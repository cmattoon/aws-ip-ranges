from .formatter import Formatter

class NginxFormatter(Formatter):
    """
    Return an nginx-style configuration from the filtered IP ranges

    Returns something like:
        allow 203.0.113.0/24;
        allow 198.51.100.0/24;
        deny all;
    """
    code = 'nginx'
    def string(self):
        """
        @todo - deal with duplicate ranges:

        allow 54.80.0.0/13; # AWS AMAZON (us-east-1)
        allow 54.80.0.0/13; # AWS EC2 (us-east-1)       ---> allow 54.80.0.0/13; # AWS AMAZON, EC2 (us-east-1)

        
        allow 54.88.0.0/14; # AWS AMAZON (us-east-1)
        allow 54.88.0.0/14; # AWS EC2 (us-east-1)       ---> allow 54.88.0.0/14; # AWS AMAZON, EC2 (us-east-1)
        
        """
        if not self.is_list_of_ipranges():
            raise ValueError("This formatter is only intended to operate on lists of IPRanges")


        data = self.deduplicate()

        sort_key = lambda k,x: (x.ip_prefix or x.ipv6_prefix)
        ipv4 = sorted(filter(lambda x: data[x][0].ip_prefix, data))
        ipv6 = sorted(filter(lambda x: data[x][0].ipv6_prefix, data))

        nginx = ""
        for cidr in ipv4:
            items = data[cidr]
            services = ",".join([f"{i.service}/{i.region}" for i in items])
            nginx += f"allow {cidr}; # AWS {services}\n"

        nginx += "\n";
        for cidr in ipv6:
            items = data[cidr]
            services = ",".join([f"{i.service}/{i.region}" for i in items])
            nginx += f"allow {cidr}; # AWS {services}\n"

        nginx += "\n";
        nginx += "deny all;"
        return nginx
