import argparse
from datetime import datetime
from pathlib import Path

from scorer import build_score
from collector import collect_metrics
from demo_data import get_demo_score
from report import print_report, build_md_report, save_md_report


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description='InfraScore JP — AWSインフラ健全性スコアリングCLI')
    parser.add_argument('--profile', default='default', help='AWS profile名')
    parser.add_argument('--demo', action='store_true', help='デモデータで動作確認（AWS不要）')
    parser.add_argument('--ai', action='store_true', help='Claude AIによる改善提案を生成（ANTHROPIC_API_KEY必要）')
    parser.add_argument('--output-md', action='store_true', help='MDレポートを出力')
    return parser.parse_args(argv)


def run(profile: str, demo: bool = False, ai: bool = False, output_md: bool = False) -> None:
    if demo:
        score_data = get_demo_score()
    else:
        metrics = collect_metrics(profile)
        score_data = build_score(metrics)
        score_data['profile'] = profile

    ai_suggestions = []
    if ai:
        from analyzer import analyze_score
        ai_suggestions = analyze_score(score_data)

    print_report(score_data, ai_suggestions=ai_suggestions)

    if output_md:
        content = build_md_report(score_data, ai_suggestions=ai_suggestions)
        filename = f"infrascore_report_{datetime.now().strftime('%Y%m%d')}.md"
        output_path = str(Path('C:/claude_c') / filename)
        save_md_report(content, output_path)
        print(f'\n MDレポートを保存しました: {output_path}')


if __name__ == '__main__':
    args = parse_args()
    run(profile=args.profile, demo=args.demo, output_md=args.output_md)
