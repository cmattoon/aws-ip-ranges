from typing import List

from .formatter import Formatter

class IptablesFormatter(Formatter):
    """
    Return iptables commands, like:
        iptables -A INPUT -s 203.0.113.0/24 -p tcp --dport 443 -j ACCEPT
        iptables -A INPUT -s 198.51.100.0/24 -p tcp --dport 80 -j ACCEPT
    """
    
    code = 'iptables'
    rule_template = "iptables -A OUTPUT -d {ip} -p tcp --dport {port} -j ACCEPT"

    def string(self):
        data = self.deduplicate()

        ipv4 = sorted(filter(lambda x: data[x][0].ip_prefix, data))
        ipv6 = sorted(filter(lambda x: data[x][0].ipv6_prefix, data))

        rules = ""
        for ip in ipv4:
            items = data[ip]
            ports = set([])
            services = []
            for i in items:
                for p in self.port_map(i.service):
                    ports.add(p)
                services.append(f"{i.service}/{i.region}")
            for port in ports:
                rules += f"# Allow outbound access to AWS {','.join(services)}\n"
                rules += self.rule_template.format(ip=ip, port=port) + "\n"
        return rules
    
    def port_map(self, aws_service_name: str) -> List[int]:
        """
        Generated by ChatGPT. YMMV.
        """
        service_ports = {
            "AMAZON": [443],
            "AMAZON_APPFLOW": [443],
            "AMAZON_CONNECT": [443, 5060, 5061],
            "API_GATEWAY": [443],
            "CHIME_MEETINGS": [443, 3478, 5349],
            "CHIME_VOICECONNECTOR": [443, 5060, 5061, 1024],
            "CLOUD9": [443, 22],
            "CLOUDFRONT": [443, 80],
            "CLOUDFRONT_ORIGIN_FACING": [443, 80],
            "CODEBUILD": [443],
            "DYNAMODB": [443],
            "EBS": [443],
            "EC2": [443],
            "EC2_INSTANCE_CONNECT": [443, 22],
            "GLOBALACCELERATOR": [443],
            "IVS_REALTIME": [443, 1935],
            "KINESIS_VIDEO_STREAMS": [443],
            "MEDIA_PACKAGE_V2": [443],
            "ROUTE53": [53, 443],
            "ROUTE53_HEALTHCHECKS": [443],
            "ROUTE53_HEALTHCHECKS_PUBLISHING": [443],
            "ROUTE53_RESOLVER": [53],
            "S3": [443, 80],
            "WORKSPACES_GATEWAYS": [443],
        }
        return service_ports[aws_service_name]
