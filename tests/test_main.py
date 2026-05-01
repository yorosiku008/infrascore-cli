import pytest
from unittest.mock import MagicMock, patch


def test_parse_args_defaults():
    from main import parse_args
    args = parse_args([])
    assert args.profile == 'default'
    assert args.demo is False
    assert args.output_md is False


def test_parse_args_demo_flag():
    from main import parse_args
    args = parse_args(['--demo'])
    assert args.demo is True


def test_parse_args_profile():
    from main import parse_args
    args = parse_args(['--profile', 'mycompany'])
    assert args.profile == 'mycompany'


def test_parse_args_output_md():
    from main import parse_args
    args = parse_args(['--output-md'])
    assert args.output_md is True


@patch('main.print_report')
@patch('main.get_demo_score')
def test_run_demo_mode_uses_demo_data(mock_demo, mock_print):
    mock_demo.return_value = {'total': 72, 'grade': 'B', 'axes': {}}
    from main import run
    with patch('main.collect_metrics') as mock_collect:
        run(profile='default', demo=True, output_md=False)
        mock_collect.assert_not_called()
    mock_demo.assert_called_once()
    mock_print.assert_called_once()


@patch('main.print_report')
@patch('main.collect_metrics')
@patch('main.build_score')
def test_run_live_mode_collects_metrics(mock_build, mock_collect, mock_print):
    mock_collect.return_value = {}
    mock_build.return_value = {'total': 80, 'grade': 'A', 'axes': {}}
    from main import run
    run(profile='myprofile', demo=False, output_md=False)
    mock_collect.assert_called_once_with('myprofile')
    mock_build.assert_called_once()


@patch('main.save_md_report')
@patch('main.build_md_report')
@patch('main.print_report')
@patch('main.get_demo_score')
def test_run_saves_md_when_flag_set(mock_demo, mock_print, mock_build, mock_save):
    mock_demo.return_value = {'total': 72, 'grade': 'B', 'axes': {}}
    mock_build.return_value = '# Report'
    from main import run
    run(profile='default', demo=True, output_md=True)
    mock_build.assert_called_once()
    mock_save.assert_called_once()
