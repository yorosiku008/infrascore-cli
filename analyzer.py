from typing import Dict, List
import anthropic

SCORE_ANALYSIS_PROMPT = """あなたはAWSインフラ最適化の専門家です。
以下のインフラ健全性スコアを分析し、優先度の高い改善アクションを3件、日本語で簡潔に提示してください。

【スコアデータ】
総合スコア: {total}/100  グレード: {grade}
プロファイル: {profile}

軸別スコア:
{axes_summary}

主な問題点:
{issues}

【回答形式】
1. [具体的な改善アクション] → [期待効果]
2. [具体的な改善アクション] → [期待効果]
3. [具体的な改善アクション] → [期待効果]

実施優先度が高い順に、根拠のある具体的な内容で提案してください。"""


def analyze_score(score_data: Dict) -> List[str]:
    client = anthropic.Anthropic()

    axes = score_data.get('axes', {})
    axes_summary = '\n'.join(
        f"  {k}: {v['score']}点" for k, v in axes.items()
    )

    all_issues = []
    for v in axes.values():
        all_issues.extend(v.get('issues', []))
    issues_text = '\n'.join(f"  - {i}" for i in all_issues) or '  なし'

    prompt = SCORE_ANALYSIS_PROMPT.format(
        total=score_data['total'],
        grade=score_data['grade'],
        profile=score_data.get('profile', 'default'),
        axes_summary=axes_summary,
        issues=issues_text,
    )

    response = client.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=500,
        messages=[{'role': 'user', 'content': prompt}],
    )

    lines = response.content[0].text.strip().split('\n')
    return [line.strip() for line in lines if line.strip()]
