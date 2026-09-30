"""Offline routing checks and explicitly synthetic, executed fixture replays."""

import shutil
import sys
import tempfile
import uuid
from collections import Counter
from pathlib import Path

from .contracts import load_json, validate
from .routing import route
from .telemetry import summarize
from .validation import run_commands

STRATEGIES = (
    "frontier_only", "lightweight_only", "intelligent",
    "architecture_high_implementation_low", "progressive",
)
CATEGORIES = {
    "tiny_bug", "feature", "refactor", "api_integration", "ui_change", "migration",
    "flaky_test", "dependency_upgrade", "unfamiliar_repository", "multi_file_bug",
    "architecture", "security", "documentation", "review", "performance",
}


def _path(base, relative, directory=False):
    """Resolve a checkout-relative path without traversal or symlink indirection."""
    if not isinstance(relative, str) or not relative:
        raise ValueError("Invalid fixture or suite path")
    value = Path(relative)
    if (value.is_absolute() or relative != value.as_posix()
            or any(part in {"..", "."} for part in value.parts)):
        raise ValueError("Fixture or suite path must stay inside its bundled directory")
    candidate = base
    for part in value.parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise ValueError("Fixture or suite symlinks are forbidden")
    resolved = candidate.resolve()
    if not resolved.is_relative_to(base) or (directory and not resolved.is_dir()):
        raise ValueError("Invalid fixture or suite directory")
    if not directory and not resolved.is_file():
        raise ValueError("Missing fixture or suite file")
    return resolved


def _floor(task, policy):
    levels = {"low": 0, "medium": 2, "high": 3}
    floor = max(policy["risk_floors"][task["risk"]], levels[task["complexity"]],
                levels[task["ambiguity"]],
                *(policy["signal_floors"][signal] for signal in task["signals"]))
    if task["category"] in {"security", "migration"}:
        floor = max(floor, policy["category_tiers"][task["category"]])
    return int(floor)


def _decision(task, policy, strategy):
    decision = route(task, policy)
    floor = _floor(task, policy)
    if strategy == "frontier_only":
        tier = 4
    elif strategy == "lightweight_only":
        # A deliberately unguarded comparison baseline; report its floor violations.
        tier = 1
    elif strategy == "architecture_high_implementation_low":
        tier = max(floor, 3 if task["stage"] in {
            "understanding", "research", "architecture", "planning", "review"
        } else 1)
    elif strategy == "progressive":
        tier = max(1, floor)
    else:
        tier = int(decision["tier"])
    decision["tier"] = tier
    decision["context_budget_tokens"] = min(
        policy["context_budgets"][str(tier)], policy["max_context_tokens"]
    )
    validate(decision, "decision")
    return decision


def _case(document):
    allowed = {"task", "expected_floor", "expected_tiers", "rationale", "fixture"}
    if not isinstance(document, dict) or set(document) - allowed:
        raise ValueError("Invalid evaluation case fields")
    if not {"task", "expected_floor", "expected_tiers", "rationale"} <= set(document):
        raise ValueError("Missing evaluation case fields")
    validate(document["task"], "task")
    expected = document["expected_tiers"]
    tiers = [document["expected_floor"]] + list(expected.values()) if isinstance(expected, dict) else []
    if (not isinstance(expected, dict) or set(expected) != set(STRATEGIES) or not tiers
            or any(isinstance(tier, bool) or not isinstance(tier, int) or not 0 <= tier <= 4
                   for tier in tiers)):
        raise ValueError("Cases require an independent floor and tier for every strategy")
    return document


def _fixture(root, case):
    spec = case["fixture"]
    required = {"directory", "validation_commands", "patches", "script_choices", "expected_outcomes"}
    if not isinstance(spec, dict) or set(spec) != required:
        raise ValueError("Invalid fixture description")
    bundled = _path(root, "evals/fixtures", directory=True)
    source = _path(bundled, spec["directory"], directory=True)
    if any(path.is_symlink() for path in source.rglob("*")):
        raise ValueError("Fixture symlinks are forbidden")
    commands = spec["validation_commands"]
    if not isinstance(commands, list) or not commands:
        raise ValueError("Fixture requires real validation commands")
    validators = set()
    for command in commands:
        if (not isinstance(command, list) or len(command) != 2
                or command[0] not in {"python", "python3"}):
            raise ValueError("Fixture commands must execute a bundled Python validator")
        script = _path(source, command[1])
        if script.suffix != ".py":
            raise ValueError("Fixture validator must be a bundled Python file")
        validators.add(script)
    patches = spec["patches"]
    if not isinstance(patches, dict) or set(patches) != {str(tier) for tier in range(5)}:
        raise ValueError("Fixture must explicitly script each tier's patch")
    for patch in patches.values():
        if not isinstance(patch, dict) or not patch:
            raise ValueError("Fixture patch must contain file edits")
        for filename, content in patch.items():
            edited = _path(source, filename)
            if edited in validators or not isinstance(content, str):
                raise ValueError("Fixture patches cannot alter the quality gates")
    outcomes = spec["expected_outcomes"]
    if (not isinstance(outcomes, dict) or set(outcomes) != set(STRATEGIES)
            or any(not isinstance(value, bool) for value in outcomes.values())):
        raise ValueError("Fixture needs independent expected quality outcomes")
    if not isinstance(spec["script_choices"], str) or not spec["script_choices"]:
        raise ValueError("Fixture must disclose its synthetic script choices")
    return source


def _record(task, strategy, run_id, attempt, tier, previous_tier, changed, results, terminal):
    status = next((r["status"] for r in results if r["status"] != "passed"), "passed")
    result = {
        "schema_version": 1, "project_id": task["project_id"], "task_id": task["task_id"],
        "run_id": run_id, "category": task["category"], "strategy": strategy,
        "stage": "implementation", "tier": tier, "attempt": attempt,
        "task_success": terminal, "validation": status,
        "input_tokens": None, "output_tokens": None, "total_metered_usage": None,
        "metered_unit": None, "cost": None, "currency": None,
        "latency_ms": sum(r["duration_ms"] for r in results), "reasoning_setting": None,
        "escalations": int(previous_tier is not None and tier > previous_tier),
        "files_changed": changed, "defects": None, "rework": attempt > 1,
        "human_intervention": False, "measurement": "scripted",
    }
    validate(result, "telemetry")
    return result


def _replay(case, source, policy, strategy, run_id):
    task, spec = case["task"], case["fixture"]
    decision = _decision(task, policy, strategy)
    previous = None
    records, gates = [], []
    with tempfile.TemporaryDirectory(prefix="cascade-fixture-") as temporary:
        working = Path(temporary).resolve()
        shutil.copytree(source, working, dirs_exist_ok=True)
        for attempt in range(1, int(policy["max_attempts"]) + 1):
            tier = decision["tier"]
            changed = 0
            for filename, content in spec["patches"][str(tier)].items():
                path = _path(working, filename)
                changed += path.read_text(encoding="utf-8") != content
                path.write_text(content, encoding="utf-8")
            commands = [[sys.executable, "-E", "-B", command[1]]
                        for command in spec["validation_commands"]]
            results = run_commands(commands, working)
            gates.append({"attempt": attempt, "tier": tier, "results": results})
            success = all(result["status"] == "passed" for result in results)
            adaptive = strategy in {"intelligent", "progressive"}
            done = success or not adaptive or attempt == policy["max_attempts"]
            records.append(_record(task, strategy, run_id, attempt, tier, previous,
                                   changed, results, success if done else None))
            if done:
                break
            previous = tier
            decision = route(task, policy, {"attempts": attempt, "validation_failed": True,
                                            "previous_tier": tier})
            if decision["status"] == "needs_human":
                records[-1]["task_success"] = False
                break
    return records, gates


def _error(report, kind, task_id, error):
    report[kind] += 1
    report["checks_failed"] += 1
    report["errors"].append({"kind": kind, "task_id": task_id, "error": str(error)})


def run_suite(root, mode="routing", execute=False):
    """Compare five strategies using checked-in routing expectations or fixture scripts.

    ``execute=True`` authorizes only bundled fixture Python validators, copied into
    a fresh temporary directory per task/strategy. This is not an OS sandbox. No
    models execute. Script-selected patches and quality outcomes do not establish
    model quality, token consumption, pricing, or savings. Validator latency is real.
    """
    if mode not in {"routing", "fixtures"}:
        raise ValueError("mode must be routing or fixtures")
    if mode == "fixtures" and execute is not True:
        raise ValueError("Fixture execution requires execute=True")
    checkout = Path(root).resolve()
    policy = load_json(_path(checkout, "examples/policy.json"))
    validate(policy, "policy")
    tasks = _path(checkout, "evals/tasks", directory=True)
    report = {
        "mode": mode, "provenance": "routing_only" if mode == "routing" else "synthetic_scripted",
        "case_count": 0, "checks_passed": 0, "checks_failed": 0,
        "contract_failures": 0, "harness_errors": 0, "execution_failures": 0,
        "expected_quality_failures": 0, "cases": [], "errors": [], "strategies": {},
        "limitations": ["No model execution or model quality/cost claim.",
                        "Fixture patch choices are synthetic; validator latency is measured.",
                        "Temporary directories provide isolation, not an OS security sandbox."],
    }
    records = {strategy: [] for strategy in STRATEGIES}
    routing = {strategy: [] for strategy in STRATEGIES}
    categories = set()
    run_id = f"fixture-{uuid.uuid4().hex}"
    for path in sorted(tasks.glob("*.json")):
        try:
            case = _case(load_json(_path(tasks, path.name)))
        except (OSError, ValueError) as exc:
            _error(report, "contract_failures", path.stem, exc)
            continue
        task = case["task"]
        categories.add(task["category"])
        if mode == "fixtures" and "fixture" not in case:
            continue
        report["case_count"] += 1
        if mode == "fixtures":
            try:
                source = _fixture(checkout, case)
            except (OSError, ValueError) as exc:
                _error(report, "harness_errors", task["task_id"], exc)
                continue
        for strategy in STRATEGIES:
            if mode == "routing":
                decision = _decision(task, policy, strategy)
                floor_satisfied = decision["tier"] >= case["expected_floor"]
                passed = (decision["tier"] == case["expected_tiers"][strategy]
                          and (floor_satisfied or strategy == "lightweight_only"))
                item = {"task_id": task["task_id"], "category": task["category"],
                        "strategy": strategy, "measurement": "routing_only",
                        "tier": decision["tier"], "expected_tier": case["expected_tiers"][strategy],
                        "expected_floor": case["expected_floor"],
                        "floor_satisfied": floor_satisfied,
                        "passed": passed}
                routing[strategy].append(item)
                report["cases"].append(item)
                if passed:
                    report["checks_passed"] += 1
                else:
                    _error(report, "contract_failures", task["task_id"],
                           f"{strategy} violates its independent expected tier or protected floor")
            else:
                try:
                    trial, gates = _replay(case, source, policy, strategy, run_id)
                    success = trial[-1]["task_success"]
                    expected = case["fixture"]["expected_outcomes"][strategy]
                    records[strategy].extend(trial)
                    report["cases"].append({
                        "task_id": task["task_id"], "category": task["category"],
                        "strategy": strategy, "measurement": "scripted", "task_success": success,
                        "expected_success": expected, "attempts": len(trial), "gates": gates,
                        "script_choices": case["fixture"]["script_choices"],
                    })
                    if any(r["status"] == "error" for gate in gates for r in gate["results"]):
                        _error(report, "harness_errors", task["task_id"], "Validator launch error")
                    elif success != expected:
                        _error(report, "execution_failures", task["task_id"],
                               f"{strategy} quality outcome disagrees with the scripted replay expectation")
                    else:
                        report["checks_passed"] += 1
                        report["expected_quality_failures"] += not success
                except (OSError, ValueError) as exc:
                    _error(report, "harness_errors", task["task_id"], exc)
    missing = CATEGORIES - categories
    if missing:
        _error(report, "contract_failures", None, "Missing routing categories: " + ", ".join(sorted(missing)))
    for strategy in STRATEGIES:
        if mode == "fixtures":
            report["strategies"][strategy] = summarize(records[strategy])
        else:
            items = routing[strategy]
            report["strategies"][strategy] = {
                "cases": len(items), "checks_passed": sum(item["passed"] for item in items),
                "floor_violations": sum(not item["floor_satisfied"] for item in items),
                "tier_distribution": dict(sorted(Counter(str(item["tier"]) for item in items).items())),
            }
    return report
