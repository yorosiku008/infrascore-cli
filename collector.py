import boto3
from typing import Dict


def collect_metrics(profile: str) -> Dict:
    session = boto3.Session(profile_name=profile)
    cw = session.client('cloudwatch', region_name='ap-northeast-1')
    ec2 = session.client('ec2', region_name='ap-northeast-1')
    s3 = session.client('s3')

    alarms = _get_active_alarms(cw)
    open_ports = _get_open_dangerous_ports(ec2)
    encryption_disabled = _count_unencrypted_buckets(s3)

    return {
        'availability': {
            'alarms': alarms,
            'elb_5xx_rate': 0.0,
            'rds_available': True,
        },
        'performance': {
            'avg_cpu_pct': _get_avg_cpu(cw),
            'avg_mem_pct': 0.0,
            'p95_latency_ms': 0,
        },
        'security': {
            'open_ports': open_ports,
            'mfa_enabled': True,
            'encryption_disabled_count': encryption_disabled,
        },
        'cost_efficiency': {
            'ri_coverage_pct': 100.0,
            'idle_instances': 0,
            'unattached_volumes': _count_unattached_volumes(ec2),
        },
    }


def _get_active_alarms(cw) -> list:
    resp = cw.describe_alarms(StateValue='ALARM')
    return [a['AlarmName'] for a in resp.get('MetricAlarms', [])]


def _get_open_dangerous_ports(ec2) -> list:
    dangerous = {22, 3389, 3306, 5432}
    open_ports = set()
    paginator = ec2.get_paginator('describe_security_groups')
    for page in paginator.paginate():
        for sg in page['SecurityGroups']:
            for rule in sg.get('IpPermissions', []):
                cidrs = [r['CidrIp'] for r in rule.get('IpRanges', [])]
                cidrs6 = [r['CidrIpv6'] for r in rule.get('Ipv6Ranges', [])]
                if '0.0.0.0/0' in cidrs or '::/0' in cidrs6:
                    fp = rule.get('FromPort', 0)
                    tp = rule.get('ToPort', 65535)
                    for p in dangerous:
                        if fp <= p <= tp:
                            open_ports.add(p)
    return list(open_ports)


def _get_avg_cpu(cw) -> float:
    from datetime import datetime, timedelta
    resp = cw.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[],
        StartTime=datetime.utcnow() - timedelta(hours=1),
        EndTime=datetime.utcnow(),
        Period=3600,
        Statistics=['Average'],
    )
    points = resp.get('Datapoints', [])
    return points[0]['Average'] if points else 0.0


def _count_unencrypted_buckets(s3) -> int:
    count = 0
    for bucket in s3.list_buckets().get('Buckets', []):
        try:
            s3.get_bucket_encryption(Bucket=bucket['Name'])
        except Exception:
            count += 1
    return count


def _count_unattached_volumes(ec2) -> int:
    resp = ec2.describe_volumes(Filters=[{'Name': 'status', 'Values': ['available']}])
    return len(resp.get('Volumes', []))
