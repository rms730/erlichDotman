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


def test_workflow_cli_distinguishes_schema_shape_from_declared_consistency(tmp_path):
    import json
    record = json.loads((ROOT / 'evals/workflow_reliability/cases.json').read_text())['stream']
    path = tmp_path / 'workflow.json'
    path.write_text(json.dumps(record))
    result = call('workflow-check', str(path))
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['scope'] == 'supplied_workflow_facts_only'
    record['journey']['owner'] = None
    record['retry']['hypothesis'] = 'private-reproduction-details'
    path.write_text(json.dumps(record))
    assert call('validate', str(path), '--kind', 'workflow').returncode == 0
    failed = call('workflow-check', str(path))
    assert failed.returncode == 2
    assert 'Traceback' not in failed.stderr
    assert 'private-reproduction-details' not in failed.stderr


def test_route_cli_uses_classified_capture_retry(tmp_path):
    import json
    record = json.loads((ROOT / 'evals/workflow_reliability/cases.json').read_text())['stream']
    task = json.loads((ROOT / 'examples/task.json').read_text())
    task.update(project_id=record['project_id'], task_id=record['task_id'])
    workflow_path, task_path = tmp_path / 'workflow.json', tmp_path / 'task.json'
    workflow_path.write_text(json.dumps(record))
    task_path.write_text(json.dumps(task))
    result = call('route', str(task_path), '--policy', 'examples/policy.json',
                  '--workflow', str(workflow_path))
    assert result.returncode == 0, result.stderr
    decision = json.loads(result.stdout)
    assert decision['tier'] == 1 and 'capture_failure_evidence' in decision['reason_codes']


def test_dispatch_cli_enforces_retry_policy_and_keeps_usage_unknown(tmp_path):
    import json

    from engineering_cascade.handoff import build_packet
    from engineering_cascade.routing import route

    workflow = json.loads((ROOT / 'evals/workflow_reliability/cases.json').read_text())['stream']
    task = json.loads((ROOT / 'examples/task.json').read_text())
    task.update(project_id=workflow['project_id'], task_id=workflow['task_id'])
    policy = json.loads((ROOT / 'examples/policy.json').read_text())
    project = json.loads((ROOT / 'examples/project.json').read_text())
    project.update(project_id=task['project_id'], revision=workflow['revision'], repository=str(ROOT))
    decision = route(task, policy, workflow=workflow)
    details = json.loads((ROOT / 'examples/packet-details.json').read_text())
    packet = build_packet(task, project, decision, [], **details)
    paths = {name: tmp_path / f'{name}.json' for name in ['workflow', 'decision', 'packet']}
    for name, value in [('workflow', workflow), ('decision', decision), ('packet', packet)]:
        paths[name].write_text(json.dumps(value))
    arguments = ['dispatch', str(paths['packet']), '--decision', str(paths['decision']),
                 '--workflow', str(paths['workflow'])]
    assert call(*arguments).returncode == 2
    result = call(*arguments, '--policy', 'examples/policy.json')
    assert result.returncode == 0, result.stderr
    request = json.loads(result.stdout)
    assert request['retry_attempt_limit'] == policy['max_attempts']
    assert request['effective_tier'] is None and request['usage'] is None
    workflow['retry']['completed_attempts'] = policy['max_attempts']
    paths['workflow'].write_text(json.dumps(workflow))
    assert call(*arguments, '--policy', 'examples/policy.json').returncode == 2
