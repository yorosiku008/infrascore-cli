import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import MagicMock, patch

SAMPLE_SCORE_DATA = {
    'total': 74,
    'grade': 'B',
    'profile': 'production',
    'axes': {
        'availability': {'score': 90, 'issues': ['CloudWatch アラート発生中: prod-api-cpu-high']},
        'performance': {'score': 85, 'issues': ['CPU使用率が高め: 平均72%']},
        'security': {'score': 55, 'issues': ['危険ポートが全公開されています: SSH(22)']},
        'cost_efficiency': {'score': 60, 'issues': ['Reserved Instance カバレッジ: 42%']},
    },
}


def make_mock_response(text: str):
    mock_content = MagicMock()
    mock_content.text = text
    mock_response = MagicMock()
    mock_response.content = [mock_content]
    return mock_response


@patch('analyzer.anthropic.Anthropic')
def test_analyze_score_returns_list(mock_cls):
    mock_client = MagicMock()
    mock_cls.return_value = mock_client
    mock_client.messages.create.return_value = make_mock_response(
        "1. SSHポートを特定IPに制限してください → セキュリティスコア+20\n"
        "2. Reserved Instanceを60%以上に → コスト削減\n"
        "3. CloudWatchアラートを確認して解消してください"
    )
    from analyzer import analyze_score
    result = analyze_score(SAMPLE_SCORE_DATA)
    assert isinstance(result, list)
    assert len(result) >= 1


@patch('analyzer.anthropic.Anthropic')
def test_analyze_score_returns_strings(mock_cls):
    mock_client = MagicMock()
    mock_cls.return_value = mock_client
    mock_client.messages.create.return_value = make_mock_response("1. 提案A\n2. 提案B\n3. 提案C")
    from analyzer import analyze_score
    result = analyze_score(SAMPLE_SCORE_DATA)
    for item in result:
        assert isinstance(item, str) and len(item) > 0


@patch('analyzer.anthropic.Anthropic')
def test_analyze_score_calls_claude(mock_cls):
    mock_client = MagicMock()
    mock_cls.return_value = mock_client
    mock_client.messages.create.return_value = make_mock_response("1. 提案")
    from analyzer import analyze_score
    analyze_score(SAMPLE_SCORE_DATA)
    mock_client.messages.create.assert_called_once()
    kwargs = mock_client.messages.create.call_args[1]
    assert kwargs['model'] == 'claude-sonnet-4-6'


@patch('analyzer.anthropic.Anthropic')
def test_analyze_score_prompt_includes_score(mock_cls):
    mock_client = MagicMock()
    mock_cls.return_value = mock_client
    mock_client.messages.create.return_value = make_mock_response("1. 提案")
    from analyzer import analyze_score
    analyze_score(SAMPLE_SCORE_DATA)
    kwargs = mock_client.messages.create.call_args[1]
    prompt = kwargs['messages'][0]['content']
    assert '74' in prompt or 'B' in prompt
