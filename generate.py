#!/usr/bin/env python3
"""
Tools for working with the AWS IP list.


Usage:
    generate.py (-h | --help)
    generate.py query [--region <region> ... ] [--service <service> ... ] [--border-group <border-group> ... ] [(--only-ipv4|--only-ipv6)] [options]
    generate.py list (regions|services|border-groups) [options]


Options:
    -h, --help                                        Show this screen and exit.
    -r <region>, --region <region>                    Specify one or more regions.
    -s <service>, --service <service>                 Specify one or more services.
    -b <border-group>, --border-group <border-group>  The network border group to filter by.
    -f <format>, --format <format>                    Output format [default: text].
    -o <outfile>, --output <outfile>                  Writes results to a file [default: stdout].
"""
import sys
import re
import requests
import dataclasses
import json, yaml

from argparse import ArgumentParser
from dataclasses import dataclass
from docopt import docopt
from typing import List, Optional

import formatters

IP_RANGES_URL = "https://ip-ranges.amazonaws.com/ip-ranges.json"

RAW_DATA = None # Raw data from IP_RANGES_URL.json()
ALL_DATA = None # RangeData

# These are populated as RangeData is constructed from the JSON response.
ALL_SERVICES = set([])
ALL_REGIONS = set([])
ALL_NETWORK_BORDER_GROUPS = set([])

class EnhancedJSONEncoder(json.JSONEncoder):
    """Support json.dumps on dataclasses"""
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)

class EnhancedYAMLDumper(yaml.Dumper):
    """Support YAML dumping for dataclasses"""
    def represent_data(self, data):
        if dataclasses.is_dataclass(data):
            return super().represent_data(dataclasses.asdict(data))
        return super().represent_data(data)

@dataclass
class IPRange:
    """
    Represents the individual line items from ip-ranges.json
    """
    ip_prefix: str = None
    ipv6_prefix: str = None
    region: str = None
    service: str = None
    network_border_group: str = None

    def to_dict(self):
        return dict(
            ip_prefix=self.ip_prefix,
            ipv6_prefix=self.ipv6_prefix,
            region=self.region,
            service=self.service,
            network_border_group=self.network_border_group)

    def __iter__(self):
        for k, v in self.to_dict().items():
            yield k, v

    def __getitem__(self, key):
        attrs = dict(self)
        return attrs[key]
    
@dataclass
class PrefixList:
    """
    The return type of RangeData.query, containing separate lists of IPRanges for IPv4 and IPv6.
    """
    ipv4: List[IPRange]
    ipv6: List[IPRange]

    def all(self):
        return self.ipv4 + self.ipv6
    
@dataclass
class RangeData:
    """
    RangeData represents the data structure of the ip-ranges.json file.
    """
    syncToken: str
    createDate: str
    prefixes: List[IPRange]
    ipv6_prefixes: List[IPRange]

    @staticmethod
    def from_dict(data: dict):
        def _tally(i):
            ALL_REGIONS.add(i.get('region'))
            ALL_SERVICES.add(i.get('service'))
            ALL_NETWORK_BORDER_GROUPS.add(i.get('network_border_group'))
            return IPRange(**i)

        ip4 = [_tally(item) for item in data.get('prefixes', [])]
        ip6 = [_tally(item) for item in data.get('ipv6_prefixes', [])]
        
        return RangeData(
            syncToken=data['syncToken'],
            createDate=data['createDate'],
            prefixes=ip4,
            ipv6_prefixes=ip6
        )
        

    def query(self,
              service: str = '*',
              region: str = '*',
              network_border_group: str = '*',
              prefix_pattern: str = '',
              prefix_match_type: str = 'prefix',
              re_flags: Optional[re.RegexFlag] = None) -> PrefixList:
        """
        Filter the IPRanges by basic criteria like service and/or region, or regex/substring matching against the CIDR string.

        Currently, only the `prefix_pattern` supports pattern matching; `region`, `service`, and `network_border_group` are evaluated with "==".

        Examples:
            data.query(service='EC2')                                      # All EC2 IP ranges in all regions.
            data.query(service='EC2', region='us-east-1')                  # EC2 IP ranges in us-east-1.
            data.query(network_border_group='us-east-1-wl1-bos-wlz-1')     # All services in the 'us-east-1-wl1-bos-wlz-1' network border group.
            data.query(prefix_pattern='12.34', prefix_match_type='prefix') # Returns all addresses starting with `12.34`.

        Args:
            service (str): Return only rows matching this service.
            region (str): Return only rows matching this region.
            network_border_group (str): Return only rows matching this network border group.
            prefix_pattern (str): A regular expression or substring to match.
            prefix_match_type (str): Whether to treat `prefix_pattern` as `regex`, `substr`, or `prefix` (startswith)
            re_flags (re.RegexFlag): A way to pass in regex flags as needed. When re_flags is None, assumes `re.MULTILINE`.

        Raises:
            ValueError: when an invalid prefix_match_type is specified.
        
        Returns:
            result (PrefixList): A list of IPv4 and IPv6 matches.
        """
        def _match_prefix(prefix: str, pattern: str, method: str):
            if pattern == '':
                return True # N/A
            
            if method == 'substr':
                return pattern in prefix
            elif method == 'prefix':
                return prefix.startswith(pattern)
            elif method == 'regex':
                if re_flags is None:
                    re_flags = re.MULTILINE
                g = re.search(prefix_pattern, prefix, re_flags)
                return g is not None and len(g.group()) > 0
            raise ValueError(f"Unknown match method '{method}'")
        
        def _query(items):
            result = []
            for item in items:
                prefix = item.ip_prefix if item.ip_prefix is not None else item.ipv6_prefix
                matches = {
                    'region_match': region == '*' or item.region.lower() == region,
                    'service_match': service == '*' or item.service.upper() == service,
                    'network_match': network_border_group == '*' or item.network_border_group == network_border_group,
                    'prefix_match': _match_prefix(prefix, prefix_pattern, prefix_match_type),
                }

                if all(matches.values()):
                    result.append(item)
            return result

        ip4 = _query(self.prefixes)
        ip6 = _query(self.ipv6_prefixes)

        return PrefixList(**{
            "ipv4": ip4,
            "ipv6": ip6,
        })

            
def download(url=IP_RANGES_URL):
    global RAW_DATA
    global ALL_DATA
    try:
        response = requests.get(url)
        response.raise_for_status()
        RAW_DATA = response.json()
        ALL_DATA = RangeData.from_dict(RAW_DATA)
        return ALL_DATA
    except requests.RequestException as e:
        print(f"Error downloading IP ranges: {e}")
        return None

def datatable(data: List[any]):
    if not data:
        raise RuntimeError(f"Can't display the data if you don't have any data!")

    row = data[0]
    fields = dataclasses.fields(row)
    headers = [f.name for f in fields]
    pads = [len(h) for h in headers]
    rows = []
    for item in data:
        for i, field in enumerate(dataclasses.fields(item)):
            value = str(getattr(item, field.name))
            vlen = max(pads[i], len(value))
            rows.append(value)

            
    table = " | ".join(header.ljust(pads[i]) for i, header in enumerate(headers)) + "\n"
    table += "-+-".join("-" * width for width in pads) + "\n"
    
    data_rows = "\n".join(
        " | ".join(row[i].ljust(pads[i]) for i, _ in enumerate(headers))
        for row in data
    )
    return f"{header_row}\n{divider}\n{data_rows}"

    
def encode_text(data):
    """
    Plain text output

    With "list" command, `data` will be `List[str]`
    With "query" command, `data` will be a `PrefixList`
    """
    print(type(data))
    if type(data) is list:
        if all(isinstance(v, str) for v in data):
            for row in data:
                print(row)
            return
        if all(isinstance(v, IPRange) for v in data):
            return datatable(data)
                
    elif type(data) is PrefixList:
        print(f">> {data}")
        datatable(data)

    raise ValueError(f"Unsupported data type {type(data)}")

def encode_data(data, fmt: str = 'json') -> str:
    if fmt not in formatters.List():
        raise ValueError(f"Invalid format type '{fmt}'. Valid values are: {formatters.List()}")
    return formatters.Get(fmt, data).string()

# OUTPUT_FORMATS = {
#     'json': lambda d: json.dumps(d, cls=EnhancedJSONEncoder),
#     'yaml': lambda d: yaml.dump(d, default_flow_style=False, Dumper=EnhancedYAMLDumper),
#     'text': encode_text
# }
# def encode_data(data, fmt: str = 'json'):
#     try:
#         func = OUTPUT_FORMATS[fmt]
#     except KeyError:
#         raise ValueError(f"Invalid output format '{fmt}'. Valid options are: {OUTPUT_FORMATS}")
#     return func(data)

def write_data(opts, data):
    if opts['--output'] == 'stdout':
        print(data)
        return None
    
    with open(opts['--output'], 'w') as fd:
        fd.write(data)

def cmd_query_data(opts):
    """
    Primary command function that queries data
    """
    regions = opts['--region'] if opts['--region'] else ALL_REGIONS
    services = opts['--service'] if opts['--service'] else ALL_SERVICES

    results = []

    for region in regions:
        for svc in services:
            r = ALL_DATA.query(svc, region)
            if not opts['--only-ipv6']:
                for ip4 in r.ipv4:
                    results.append(ip4)
            if not opts['--only-ipv4']:
                for ip6 in r.ipv6:
                    results.append(ip6)

    write_data(opts, encode_data(results, opts['--format']))
    
    return results

def cmd_list(opts):
    """List things"""
    things_to_list = {'regions': ALL_REGIONS, 'services': ALL_SERVICES, 'border-groups': ALL_NETWORK_BORDER_GROUPS}
    for k, v in opts.items():
        if k in things_to_list and opts[k] is True:
            return write_data(opts, encode_data(things_to_list[k], opts['--format']))
    raise RuntimeError(f"Expected to match one of {things_to_list.keys()}, but apparently that didn't happen.")

def main(opts):
    if opts['list']:
        return cmd_list(opts)
    
    elif opts['query']:
        return cmd_query_data(opts)


if __name__ == '__main__':
    opts = docopt(__doc__)
    #print(opts)

    data = download()

    # Sort the lists populated during the download() process.
    # These are used by the "list" command to ensure up-to-date info.
    ALL_REGIONS = sorted(ALL_REGIONS)
    ALL_SERVICES = sorted(ALL_SERVICES)
    ALL_NETWORK_BORDER_GROUPS = sorted(ALL_NETWORK_BORDER_GROUPS)

    # support '--region all'
    if 'all' in opts['--region']:
        opts['--region'] = ALL_REGIONS

    # support '--service all'
    if 'all' in opts['--service']:
        opts['--service'] = ALL_SERVICES

    # support '--border-group all'
    if 'all' in opts['--border-group']:
        opts['--border-group'] = ALL_NETWORK_BORDER_GROUPS

    results = main(opts)
