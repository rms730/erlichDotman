import json
import shutil
from pathlib import Path

import pytest

from engineering_cascade.evaluation import run_suite

ROOT = Path(__file__).resolve().parents[1]
STRATEGIES = {
    "frontier_only", "lightweight_only", "intelligent",
    "architecture_high_implementation_low", "progressive",
}


def copied_suite(tmp_path):
    shutil.copytree(ROOT / "evals", tmp_path / "evals")
    shutil.copytree(ROOT / "examples", tmp_path / "examples")
    return tmp_path


def test_routing_suite_covers_all_categories_with_independent_expectations():
    report = run_suite(ROOT)
    assert report["mode"] == "routing"
    assert report["case_count"] >= 15
    assert len({case["category"] for case in report["cases"]}) == 15
    assert set(report["strategies"]) == STRATEGIES
    assert report["checks_failed"] == 0
    assert report["contract_failures"] == 0
    assert report["harness_errors"] == 0
    assert report["execution_failures"] == 0
    assert all(item["measurement"] == "routing_only" for item in report["cases"])


def test_fixture_execution_requires_explicit_opt_in():
    with pytest.raises(ValueError, match="execute=True"):
        run_suite(ROOT, mode="fixtures")


def test_fixture_replays_real_gates_and_synthetic_escalation():
    report = run_suite(ROOT, mode="fixtures", execute=True)
    assert report["case_count"] >= 5
    assert report["harness_errors"] == 0
    assert report["checks_failed"] == 0
    assert report["execution_failures"] == 0
    assert report["expected_quality_failures"] > 0
    assert report["strategies"]["progressive"]["successful_tasks"] == report["case_count"]
    assert report["strategies"]["progressive"]["retries"] > 0
    assert report["strategies"]["lightweight_only"]["failed_tasks"] > 0
    assert report["strategies"]["frontier_only"]["first_pass_success_rate"] == 1
    for summary in report["strategies"].values():
        assert summary["measurements"]["cost"]["total"] is None
        assert summary["measurements"]["total_tokens"]["total"] is None
        assert summary["measurements"]["latency_ms"]["total"] is not None
    assert all(case["measurement"] == "scripted" for case in report["cases"])
    assert all(case["attempts"] <= 3 for case in report["cases"])


def test_routing_expectation_mismatch_is_visible(tmp_path):
    root = copied_suite(tmp_path)
    path = root / "evals/tasks/tiny_bug.json"
    case = json.loads(path.read_text())
    case["expected_tiers"]["intelligent"] = 4
    path.write_text(json.dumps(case))
    report = run_suite(root)
    assert report["checks_failed"] == 1
    assert report["contract_failures"] == 1


def test_protected_strategy_floor_violation_fails_routing_gate(tmp_path):
    root = copied_suite(tmp_path)
    path = root / "evals/tasks/tiny_bug.json"
    case = json.loads(path.read_text())
    case["expected_floor"] = 4
    path.write_text(json.dumps(case))
    report = run_suite(root)
    assert report["checks_failed"] == 3
    assert report["strategies"]["intelligent"]["floor_violations"] == 1


def test_contract_integer_valued_policy_numbers_run_as_integer_counts(tmp_path):
    root = copied_suite(tmp_path)
    path = root / "examples/policy.json"
    policy = json.loads(path.read_text())
    policy["max_attempts"] = 3.0
    policy["risk_floors"]["medium"] = 2.0
    path.write_text(json.dumps(policy))
    report = run_suite(root, mode="fixtures", execute=True)
    assert report["harness_errors"] == 0
    assert report["checks_failed"] == 0


def test_unexpected_failed_validator_is_execution_failure(tmp_path):
    root = copied_suite(tmp_path)
    path = root / "evals/fixtures/boundary/check.py"
    path.write_text("raise AssertionError('broken gate')\n")
    report = run_suite(root, mode="fixtures", execute=True)
    assert report["execution_failures"] > 0
    assert report["checks_failed"] > 0
    assert report["harness_errors"] == 0


@pytest.mark.parametrize("fixture_path", ["../outside", "/tmp/outside"])
def test_fixture_escape_is_rejected_without_execution(tmp_path, fixture_path):
    root = copied_suite(tmp_path)
    path = root / "evals/tasks/tiny_bug.json"
    case = json.loads(path.read_text())
    case["fixture"]["directory"] = fixture_path
    path.write_text(json.dumps(case))
    report = run_suite(root, mode="fixtures", execute=True)
    assert report["harness_errors"] == 1
    assert report["errors"][0]["kind"] == "harness_errors"
    assert report["errors"][0]["task_id"] == "tiny_bug"


def test_fixture_symlinks_are_rejected(tmp_path):
    root = copied_suite(tmp_path)
    (root / "evals/fixtures/boundary/linked").symlink_to(ROOT / "pyproject.toml")
    report = run_suite(root, mode="fixtures", execute=True)
    assert report["harness_errors"] == 1


def test_patch_traversal_is_rejected(tmp_path):
    root = copied_suite(tmp_path)
    path = root / "evals/tasks/tiny_bug.json"
    case = json.loads(path.read_text())
    case["fixture"]["patches"]["1"]["../escape"] = "no"
    path.write_text(json.dumps(case))
    report = run_suite(root, mode="fixtures", execute=True)
    assert report["harness_errors"] == 1
    assert not (tmp_path / "escape").exists()


def test_patch_alias_cannot_overwrite_a_validator(tmp_path):
    root = copied_suite(tmp_path)
    path = root / "evals/tasks/tiny_bug.json"
    case = json.loads(path.read_text())
    case["fixture"]["patches"]["1"]["./check.py"] = "pass\n"
    path.write_text(json.dumps(case))
    report = run_suite(root, mode="fixtures", execute=True)
    assert report["harness_errors"] == 1
    assert not any(item["task_id"] == "tiny_bug" for item in report["cases"])


def test_fixture_retry_limit_stops_further_subprocesses(tmp_path):
    root = copied_suite(tmp_path)
    path = root / "examples/policy.json"
    policy = json.loads(path.read_text())
    policy["max_attempts"] = 1
    path.write_text(json.dumps(policy))
    report = run_suite(root, mode="fixtures", execute=True)
    assert all(item["attempts"] == 1 for item in report["cases"])
    assert report["execution_failures"] > 0
    assert report["strategies"]["progressive"]["failed_tasks"] == 2


def test_each_fixture_strategy_uses_a_fresh_directory_and_preserves_sources(tmp_path):
    root = copied_suite(tmp_path)
    sources = {}
    for path in (root / "evals/fixtures").rglob("check.py"):
        path.write_text("import os\nprint(os.getcwd())\n" + path.read_text())
        sources[path] = path.read_bytes()
    report = run_suite(root, mode="fixtures", execute=True)
    working_directories = {
        item["gates"][0]["results"][0]["stdout"].splitlines()[0] for item in report["cases"]
    }
    assert len(working_directories) == 30
    assert all(not Path(directory).exists() for directory in working_directories)
    assert all(path.read_bytes() == content for path, content in sources.items())


def test_fixture_command_cannot_execute_arbitrary_program(tmp_path):
    root = copied_suite(tmp_path)
    path = root / "evals/tasks/tiny_bug.json"
    case = json.loads(path.read_text())
    case["fixture"]["validation_commands"] = [["sh", "-c", "exit 0"]]
    path.write_text(json.dumps(case))
    report = run_suite(root, mode="fixtures", execute=True)
    assert report["harness_errors"] == 1
