from datetime import datetime
from pathlib import Path
from typing import Dict

from rich.console import Console
from rich.table import Table
from rich import box

AXIS_LABELS = {
    'availability':    ('可用性',       '35%'),
    'performance':     ('パフォーマンス', '25%'),
    'security':        ('セキュリティ',  '25%'),
    'cost_efficiency': ('コスト効率',   '15%'),
}

GRADE_COLORS = {'S': 'bright_cyan', 'A': 'green', 'B': 'yellow', 'C': 'orange3', 'D': 'red', 'E': 'bright_red'}


def _score_bar(score: int, width: int = 20) -> str:
    filled = round(score / 100 * width)
    return '█' * filled + '░' * (width - filled)


def print_report(score_data: Dict) -> None:
    console = Console(legacy_windows=False)
    total = score_data['total']
    grade = score_data['grade']
    profile = score_data.get('profile', 'default')
    color = GRADE_COLORS.get(grade, 'white')

    console.print(f'\n[bold]*** InfraScore JP -- Infrastructure Health Score[/bold]')
    console.print('=' * 60)
    console.print(f'Profile : {profile}')
    console.print(f'Scanned : {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    console.print()
    console.print(f'[bold {color}]Total Score : {total} / 100   Grade : {grade}[/bold {color}]')
    console.print()

    table = Table(box=box.SIMPLE, show_header=True, header_style='bold dim')
    table.add_column('軸', style='white', width=14)
    table.add_column('重み', width=5)
    table.add_column('スコア', width=6)
    table.add_column('バー', width=22)
    table.add_column('主な問題', style='dim')

    for axis_key, (label, weight) in AXIS_LABELS.items():
        axis = score_data['axes'].get(axis_key, {'score': 0, 'issues': []})
        s = axis['score']
        c = 'green' if s >= 80 else ('yellow' if s >= 60 else 'red')
        bar = _score_bar(s)
        issue_text = axis['issues'][0] if axis['issues'] else '問題なし'
        table.add_row(label, weight, f'[{c}]{s}[/{c}]', f'[{c}]{bar}[/{c}]', issue_text)

    console.print(table)

    all_issues = []
    for axis_key in AXIS_LABELS:
        all_issues.extend(score_data['axes'].get(axis_key, {}).get('issues', []))

    if all_issues:
        console.print('[bold]改善が必要な項目:[/bold]')
        for i, issue in enumerate(all_issues, 1):
            console.print(f'  {i}. {issue}')
    console.print()


def build_md_report(score_data: Dict) -> str:
    total = score_data['total']
    grade = score_data['grade']
    lines = [
        f'# InfraScore JP — Infrastructure Health Report',
        f'',
        f'**スキャン日時:** {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        f'**総合スコア:** {total} / 100  **グレード:** {grade}',
        f'',
        f'## 軸別スコア',
        f'',
        f'| 軸 | 重み | スコア |',
        f'|---|---|---|',
    ]
    for axis_key, (label, weight) in AXIS_LABELS.items():
        s = score_data['axes'].get(axis_key, {}).get('score', 0)
        lines.append(f'| {label} | {weight} | {s} |')

    lines += ['', '## 改善項目', '']
    for axis_key, (label, _) in AXIS_LABELS.items():
        issues = score_data['axes'].get(axis_key, {}).get('issues', [])
        for issue in issues:
            lines.append(f'- [{label}] {issue}')

    return '\n'.join(lines)


def save_md_report(content: str, path: str) -> None:
    Path(path).write_text(content, encoding='utf-8')
