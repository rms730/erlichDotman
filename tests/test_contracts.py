import json
from pathlib import Path

import pytest

from engineering_cascade.contracts import load_json, validate

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('kind', ['task', 'project', 'policy'])
def test_public_examples_conform(kind):
    validate(load_json(ROOT / f'examples/{kind}.json'), kind)


def test_unknown_fields_are_rejected():
    task = load_json(ROOT / 'examples/task.json')
    task['api_key'] = 'example-private-value'
    with pytest.raises(ValueError) as exc:
        validate(task, 'task')
    assert 'example-private-value' not in str(exc.value)


def test_missing_required_fields_are_rejected():
    task = load_json(ROOT / 'examples/task.json')
    del task['project_id']
    with pytest.raises(ValueError):
        validate(task, 'task')


def test_shell_string_is_not_a_validation_command():
    task = load_json(ROOT / 'examples/task.json')
    task['validation_commands'] = ['python -m unittest; echo surprise']
    with pytest.raises(ValueError):
        validate(task, 'task')


def test_unknown_contract_name_rejected():
    with pytest.raises(ValueError):
        validate({}, '../other')


@pytest.mark.parametrize('content', ['{"x": 1, "x": 2}', '{"x": NaN}', '{"x": Infinity}'])
def test_ambiguous_json_is_rejected(tmp_path, content):
    path = tmp_path / 'input.json'
    path.write_text(content)
    with pytest.raises(ValueError):
        load_json(path)


def test_oversized_json_is_rejected(tmp_path):
    path = tmp_path / 'input.json'
    path.write_text(json.dumps({'text': 'x' * 100}))
    with pytest.raises(ValueError):
        load_json(path, max_bytes=30)


def test_excessively_nested_json_is_rejected_without_parser_traceback(tmp_path):
    path = tmp_path / 'nested.json'
    path.write_text('[' * 2000 + '0' + ']' * 2000)
    with pytest.raises(ValueError):
        load_json(path)


def test_overflowing_json_number_is_rejected(tmp_path):
    path = tmp_path / 'overflow.json'
    path.write_text('{"value": 1e999}')
    with pytest.raises(ValueError):
        load_json(path)


def test_json_nesting_budget_is_independent_of_interpreter_stack(tmp_path):
    path = tmp_path / 'nesting-limit.json'
    path.write_text('[' * 65 + '0' + ']' * 65)
    with pytest.raises(ValueError):
        load_json(path)


def test_json_at_nesting_budget_is_accepted(tmp_path):
    path = tmp_path / 'nesting-boundary.json'
    path.write_text('[' * 64 + '0' + ']' * 64)
    value = load_json(path)
    for _ in range(64):
        value = value[0]
    assert value == 0


def test_brackets_in_json_text_do_not_consume_nesting_budget(tmp_path):
    path = tmp_path / 'brackets.json'
    path.write_text(json.dumps({'text': '[' * 2000}))
    assert load_json(path)['text'] == '[' * 2000
