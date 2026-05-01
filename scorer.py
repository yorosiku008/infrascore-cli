from typing import Dict, List

WEIGHTS = {
    'availability':    0.35,
    'performance':     0.25,
    'security':        0.25,
    'cost_efficiency': 0.15,
}

GRADES = [(90, 'S'), (80, 'A'), (70, 'B'), (60, 'C'), (50, 'D'), (0, 'E')]


def score_availability(data: Dict) -> Dict:
    score = 100
    issues: List[str] = []

    for alarm in data.get('alarms', []):
        score -= 10
        issues.append(f'CloudWatch アラート発生中: {alarm}')

    elb_rate = data.get('elb_5xx_rate', 0.0)
    if elb_rate >= 5.0:
        score -= 20
        issues.append(f'ELB 5xxエラー率が高い: {elb_rate:.1f}%')
    elif elb_rate >= 1.0:
        score -= 10
        issues.append(f'ELB 5xxエラー率: {elb_rate:.1f}%')

    if not data.get('rds_available', True):
        score -= 30
        issues.append('RDS インスタンスが利用不可状態です')

    return {'score': max(0, score), 'issues': issues}


def score_performance(data: Dict) -> Dict:
    score = 100
    issues: List[str] = []

    cpu = data.get('avg_cpu_pct', 0.0)
    if cpu >= 85:
        score -= 30
        issues.append(f'CPU使用率が高い: 平均{cpu:.0f}%')
    elif cpu >= 70:
        score -= 15
        issues.append(f'CPU使用率が高め: 平均{cpu:.0f}%')

    mem = data.get('avg_mem_pct', 0.0)
    if mem >= 90:
        score -= 20
        issues.append(f'メモリ使用率が高い: 平均{mem:.0f}%')

    latency = data.get('p95_latency_ms', 0)
    if latency >= 2000:
        score -= 30
        issues.append(f'p95レイテンシが高い: {latency}ms')
    elif latency >= 500:
        score -= 15
        issues.append(f'p95レイテンシが高め: {latency}ms')

    return {'score': max(0, score), 'issues': issues}


def score_security(data: Dict) -> Dict:
    score = 100
    issues: List[str] = []

    PORT_NAMES = {22: 'SSH(22)', 3389: 'RDP(3389)', 3306: 'MySQL(3306)', 5432: 'PostgreSQL(5432)'}
    for port in data.get('open_ports', []):
        name = PORT_NAMES.get(port, str(port))
        score -= 20
        issues.append(f'危険ポートが全公開されています: {name}')

    if not data.get('mfa_enabled', True):
        score -= 25
        issues.append('rootアカウントのMFAが無効です')

    enc_count = data.get('encryption_disabled_count', 0)
    if enc_count > 0:
        score -= min(enc_count * 5, 20)
        issues.append(f'暗号化が無効なS3バケット: {enc_count}件')

    return {'score': max(0, score), 'issues': issues}


def score_cost_efficiency(data: Dict) -> Dict:
    score = 100
    issues: List[str] = []

    ri_coverage = data.get('ri_coverage_pct', 100.0)
    if ri_coverage < 30:
        score -= 30
        issues.append(f'Reserved Instance カバレッジが低い: {ri_coverage:.0f}%')
    elif ri_coverage < 60:
        score -= 15
        issues.append(f'Reserved Instance カバレッジ: {ri_coverage:.0f}%（推奨: 60%以上）')

    idle = data.get('idle_instances', 0)
    if idle > 0:
        score -= min(idle * 5, 25)
        issues.append(f'アイドル状態のEC2インスタンス: {idle}台（削除を検討してください）')

    unattached = data.get('unattached_volumes', 0)
    if unattached > 0:
        score -= min(unattached * 3, 15)
        issues.append(f'アタッチされていないEBSボリューム: {unattached}個')

    return {'score': max(0, score), 'issues': issues}


def calculate_total_score(axes: Dict) -> Dict:
    total = sum(
        axes[axis]['score'] * weight
        for axis, weight in WEIGHTS.items()
        if axis in axes
    )
    total = round(total)

    grade = 'E'
    for threshold, g in GRADES:
        if total >= threshold:
            grade = g
            break

    return {'total': total, 'grade': grade}


def build_score(metrics: Dict) -> Dict:
    axes = {
        'availability':    score_availability(metrics.get('availability', {})),
        'performance':     score_performance(metrics.get('performance', {})),
        'security':        score_security(metrics.get('security', {})),
        'cost_efficiency': score_cost_efficiency(metrics.get('cost_efficiency', {})),
    }
    summary = calculate_total_score(axes)
    return {**summary, 'axes': axes}
