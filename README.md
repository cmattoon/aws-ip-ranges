cmattoon/aws-ip-ranges
======================

A small utility script to work with the AWS IP range list.

```
Usage:
    generate.py (-h | --help)
    generate.py query [--region <region> ... ] [--service <service> ... ] [(--only-ipv4|--only-ipv6)]
    generate.py list (regions|services)


Options:
    -h, --help                         Show this screen and exit.
    -r <region>, --region <region>     Specify one or more regions.
    -s <service>, --service <service>  Specify one or more services.
```

Filtering by region and service is an "AND" condition.

Both --service and --region accept the string 'all', which is replaced at runtime with all available regions and services from the JSON file.

Match all rows for the `EC2` service in `us-east-1`:

    $ generate.py <command> --region us-east-1 --service EC2

Both `--service` and `--region` can accept multiple arguments, which are evaluated as "OR" conditions before the final "AND" for (region, service).
This example would return rows for the `EC2` or `S3` services in `us-east-1` or `us-west-2`:

    $ generate.py <command> --service EC2 --service S3 --region us-east-1 --region us-west-2
