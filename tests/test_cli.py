import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def call(*args):
    env = dict(os.environ, PYTHONPATH=str(ROOT / 'src'))
    return subprocess.run([sys.executable, '-m', 'engineering_cascade', *args],
                          cwd=ROOT, env=env, capture_output=True, text=True)


def test_route_cli_emits_machine_readable_decision():
    import json
    result = call('route', 'examples/task.json', '--policy', 'examples/policy.json')
    assert result.returncode == 0, result.stderr
    decision = json.loads(result.stdout)
    assert decision['tier'] == 1
    assert decision['project_id'] == 'sample-app'


def test_cli_invalid_input_is_nonzero_without_traceback(tmp_path):
    input_path = tmp_path / 'bad.json'
    input_path.write_text('{"objective": "private-brief-content"}')
    result = call('validate', str(input_path), '--kind', 'task')
    assert result.returncode == 2
    assert 'Traceback' not in result.stderr
    assert 'private-brief-content' not in result.stderr


def test_fixture_execution_is_opt_in():
    result = call('eval', '--root', '.', '--mode', 'fixtures')
    assert result.returncode == 2


def test_routing_suite_runs_through_cli():
    import json
    result = call('eval', '--root', '.', '--mode', 'routing')
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report['case_count'] >= 15
    assert report['checks_failed'] == 0
