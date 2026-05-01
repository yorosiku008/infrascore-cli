from typing import Dict


def get_demo_score() -> Dict:
    from scorer import score_availability, score_performance, score_security, score_cost_efficiency, calculate_total_score

    axes = {
        'availability': score_availability({
            'alarms': ['prod-api-cpu-high'],
            'elb_5xx_rate': 0.8,
            'rds_available': True,
        }),
        'performance': score_performance({
            'avg_cpu_pct': 72.0,
            'avg_mem_pct': 65.0,
            'p95_latency_ms': 480,
        }),
        'security': score_security({
            'open_ports': [22],
            'mfa_enabled': True,
            'encryption_disabled_count': 1,
        }),
        'cost_efficiency': score_cost_efficiency({
            'ri_coverage_pct': 42.0,
            'idle_instances': 2,
            'unattached_volumes': 5,
        }),
    }
    summary = calculate_total_score(axes)
    return {**summary, 'axes': axes, 'profile': 'demo-account'}
