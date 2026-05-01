import pytest
from unittest.mock import MagicMock, patch


# --- score_availability ---

def test_score_availability_returns_dict():
    from scorer import score_availability
    result = score_availability({'alarms': [], 'elb_5xx_rate': 0.0, 'rds_available': True})
    assert isinstance(result, dict)
    assert 'score' in result
    assert 'issues' in result


def test_score_availability_perfect_score():
    from scorer import score_availability
    data = {'alarms': [], 'elb_5xx_rate': 0.0, 'rds_available': True}
    result = score_availability(data)
    assert result['score'] == 100


def test_score_availability_alarm_reduces_score():
    from scorer import score_availability
    data = {'alarms': ['CPU_HIGH', 'MEM_LOW'], 'elb_5xx_rate': 0.0, 'rds_available': True}
    result = score_availability(data)
    assert result['score'] < 100
    assert len(result['issues']) > 0


def test_score_availability_high_5xx_reduces_score():
    from scorer import score_availability
    data = {'alarms': [], 'elb_5xx_rate': 5.0, 'rds_available': True}
    result = score_availability(data)
    assert result['score'] < 100


def test_score_availability_rds_unavailable_reduces_score():
    from scorer import score_availability
    data = {'alarms': [], 'elb_5xx_rate': 0.0, 'rds_available': False}
    result = score_availability(data)
    assert result['score'] < 100
    assert any('RDS' in issue for issue in result['issues'])


# --- score_performance ---

def test_score_performance_returns_dict():
    from scorer import score_performance
    result = score_performance({'avg_cpu_pct': 20.0, 'avg_mem_pct': 40.0, 'p95_latency_ms': 100})
    assert 'score' in result and 'issues' in result


def test_score_performance_low_utilization_is_perfect():
    from scorer import score_performance
    result = score_performance({'avg_cpu_pct': 20.0, 'avg_mem_pct': 40.0, 'p95_latency_ms': 100})
    assert result['score'] == 100


def test_score_performance_high_cpu_reduces_score():
    from scorer import score_performance
    result = score_performance({'avg_cpu_pct': 90.0, 'avg_mem_pct': 40.0, 'p95_latency_ms': 100})
    assert result['score'] < 100


def test_score_performance_high_latency_reduces_score():
    from scorer import score_performance
    result = score_performance({'avg_cpu_pct': 20.0, 'avg_mem_pct': 40.0, 'p95_latency_ms': 3000})
    assert result['score'] < 100
    assert any('レイテンシ' in issue for issue in result['issues'])


# --- score_security ---

def test_score_security_returns_dict():
    from scorer import score_security
    result = score_security({'open_ports': [], 'mfa_enabled': True, 'encryption_disabled_count': 0})
    assert 'score' in result and 'issues' in result


def test_score_security_no_issues_is_perfect():
    from scorer import score_security
    result = score_security({'open_ports': [], 'mfa_enabled': True, 'encryption_disabled_count': 0})
    assert result['score'] == 100


def test_score_security_open_port_reduces_score():
    from scorer import score_security
    result = score_security({'open_ports': [22, 3389], 'mfa_enabled': True, 'encryption_disabled_count': 0})
    assert result['score'] < 100
    assert len(result['issues']) > 0


def test_score_security_mfa_disabled_reduces_score():
    from scorer import score_security
    result = score_security({'open_ports': [], 'mfa_enabled': False, 'encryption_disabled_count': 0})
    assert result['score'] < 100


def test_score_security_unencrypted_buckets_reduces_score():
    from scorer import score_security
    result = score_security({'open_ports': [], 'mfa_enabled': True, 'encryption_disabled_count': 3})
    assert result['score'] < 100


# --- score_cost_efficiency ---

def test_score_cost_efficiency_returns_dict():
    from scorer import score_cost_efficiency
    result = score_cost_efficiency({'ri_coverage_pct': 80.0, 'idle_instances': 0, 'unattached_volumes': 0})
    assert 'score' in result and 'issues' in result


def test_score_cost_efficiency_full_ri_no_waste_is_perfect():
    from scorer import score_cost_efficiency
    result = score_cost_efficiency({'ri_coverage_pct': 100.0, 'idle_instances': 0, 'unattached_volumes': 0})
    assert result['score'] == 100


def test_score_cost_efficiency_low_ri_reduces_score():
    from scorer import score_cost_efficiency
    result = score_cost_efficiency({'ri_coverage_pct': 0.0, 'idle_instances': 0, 'unattached_volumes': 0})
    assert result['score'] < 100


def test_score_cost_efficiency_idle_instances_reduces_score():
    from scorer import score_cost_efficiency
    result = score_cost_efficiency({'ri_coverage_pct': 100.0, 'idle_instances': 5, 'unattached_volumes': 0})
    assert result['score'] < 100
    assert any('アイドル' in issue for issue in result['issues'])


# --- calculate_total_score ---

def test_calculate_total_score_returns_dict():
    from scorer import calculate_total_score
    axes = {
        'availability':    {'score': 80, 'issues': []},
        'performance':     {'score': 90, 'issues': []},
        'security':        {'score': 70, 'issues': []},
        'cost_efficiency': {'score': 60, 'issues': []},
    }
    result = calculate_total_score(axes)
    assert 'total' in result and 'grade' in result


def test_calculate_total_score_weights():
    from scorer import calculate_total_score
    # 可用性35%/パフォーマンス25%/セキュリティ25%/コスト15% → 100*0.35+100*0.25+100*0.25+100*0.15=100
    axes = {
        'availability':    {'score': 100, 'issues': []},
        'performance':     {'score': 100, 'issues': []},
        'security':        {'score': 100, 'issues': []},
        'cost_efficiency': {'score': 100, 'issues': []},
    }
    result = calculate_total_score(axes)
    assert result['total'] == 100


def test_calculate_total_score_grade_s():
    from scorer import calculate_total_score
    axes = {k: {'score': 95, 'issues': []} for k in
            ['availability', 'performance', 'security', 'cost_efficiency']}
    assert calculate_total_score(axes)['grade'] == 'S'


def test_calculate_total_score_grade_b():
    from scorer import calculate_total_score
    axes = {k: {'score': 75, 'issues': []} for k in
            ['availability', 'performance', 'security', 'cost_efficiency']}
    assert calculate_total_score(axes)['grade'] == 'B'


def test_calculate_total_score_grade_d():
    from scorer import calculate_total_score
    axes = {k: {'score': 55, 'issues': []} for k in
            ['availability', 'performance', 'security', 'cost_efficiency']}
    assert calculate_total_score(axes)['grade'] == 'D'
