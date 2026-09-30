"""Task outcomes and measured resource accounting, without estimated usage."""

import math
from collections import Counter, defaultdict

from .contracts import validate


def _trials(records):
    if not isinstance(records, list):
        raise ValueError("Telemetry records must be a list")
    groups = defaultdict(list)
    for record in records:
        validate(record, "telemetry")
        key = tuple(record[field] for field in ("run_id", "project_id", "task_id", "strategy"))
        groups[key].append(record)
    trials = []
    for group in groups.values():
        attempts = {int(record["attempt"]) for record in group}
        # Positive unique integers are contiguous from 1 exactly when max == count.
        if max(attempts) != len(attempts):
            raise ValueError("Trial attempts must start at 1 and be contiguous")
        if len({record["category"] for record in group}) != 1:
            raise ValueError("A trial cannot change task category")
        if len({(record["attempt"], record["stage"]) for record in group}) != len(group):
            raise ValueError("Duplicate telemetry for the same attempt and stage")
        terminal = [record for record in group if record["task_success"] is not None]
        if len(terminal) > 1 or (terminal and terminal[0]["attempt"] != max(attempts)):
            raise ValueError("A trial has at most one terminal outcome, on its last attempt")
        if terminal and terminal[0] is not group[-1]:
            raise ValueError("The terminal outcome must be the trial's final stage record")
        if [record["attempt"] for record in group] != sorted(record["attempt"] for record in group):
            raise ValueError("Trial stage records must be in attempt order")
        if terminal and terminal[0]["task_success"] and terminal[0]["validation"] != "passed":
            raise ValueError("A successful terminal outcome must pass validation")
        trials.append({"records": group, "attempts": len(attempts),
                       "terminal": terminal[0] if terminal else None})
    return trials


def _rate(numerator, denominator):
    return numerator / denominator if denominator else None


def _measurement(records, field, successes, unit, unit_field=None):
    values = []
    units = set()
    missing_unit = False
    for record in records:
        value = record[field] if field != "total_tokens" else (
            record["input_tokens"] + record["output_tokens"]
            if record["input_tokens"] is not None and record["output_tokens"] is not None
            else None
        )
        if value is not None:
            record_unit = record[unit_field] if unit_field else unit
            if record_unit is None:
                missing_unit = True
            else:
                units.add(record_unit)
            values.append(int(value) if isinstance(value, bool) else value)
    compatible = len(units) == 1 and not missing_unit
    observed = sum(values) if values and compatible else None
    total = observed if len(values) == len(records) and records else None
    return {
        "total": total,
        "observed_total": observed,
        "coverage": {"records": len(values), "total_records": len(records),
                     "fraction": _rate(len(values), len(records))},
        "unit": next(iter(units)) if compatible else None,
        "units": sorted(units),
        "missing_unit": missing_unit,
        "per_successful_task": total / successes if total is not None and successes else None,
    }


def _quality_rate(trials, field):
    outcomes = []
    for trial in trials:
        values = [r[field] for r in trial["records"]]
        if any(value for value in values if value is not None):
            outcomes.append(True)
        elif all(value is not None for value in values):
            outcomes.append(False)
        else:
            outcomes.append(None)
    known = [value for value in outcomes if value is not None]
    observed = _rate(sum(known), len(known))
    return (observed if len(known) == len(trials) else None, observed,
            {"tasks": len(known), "completed_tasks": len(trials),
             "fraction": _rate(len(known), len(trials))})


def summarize(records):
    """Summarize trials keyed by run, project, task, and strategy.

    Attempt-stage records contain incremental resource/event counts, not cumulative
    snapshots. A single terminal boolean closes each trial; null is interim. Totals
    require complete, compatible measurements. Per-success resource denominators
    include every supplied record's resources, including failed/incomplete trials.
    Records within each trial are chronological, with the terminal stage last.
    Files changed counts file-touch events; it cannot infer distinct paths. Event
    rates describe observed tasks. Defect/rework rates use completed task outcomes,
    with separate coverage and observed rates when quality measurements are missing.
    """
    trials = _trials(records)
    complete = [trial for trial in trials if trial["terminal"] is not None]
    successful = [trial for trial in complete if trial["terminal"]["task_success"]]
    first_pass = sum(trial["attempts"] == 1 for trial in successful)
    checks = sum(record["validation"] != "skipped" for record in records)
    failures = sum(record["validation"] in {"failed", "timeout", "error"} for record in records)
    escalated = sum(any(r["escalations"] for r in t["records"]) for t in trials)
    intervened = sum(any(r["human_intervention"] for r in t["records"]) for t in trials)
    defect_rate, observed_defect_rate, defect_coverage = _quality_rate(complete, "defects")
    rework_rate, observed_rework_rate, rework_coverage = _quality_rate(complete, "rework")
    measurements = {}
    for field, unit, unit_field in [
        ("input_tokens", "tokens", None), ("output_tokens", "tokens", None),
        ("total_tokens", "tokens", None), ("total_metered_usage", None, "metered_unit"),
        ("cost", None, "currency"), ("latency_ms", "ms", None),
        ("defects", "defects", None), ("rework", "records_with_rework", None),
    ]:
        measurements[field] = _measurement(records, field, len(successful), unit, unit_field)
    return {
        "record_count": len(records), "task_count": len(trials),
        "completed_tasks": len(complete), "successful_tasks": len(successful),
        "failed_tasks": len(complete) - len(successful),
        "incomplete_tasks": len(trials) - len(complete),
        "completion_rate": _rate(len(complete), len(trials)),
        "success_rate": _rate(len(successful), len(complete)),
        "first_pass_successes": first_pass,
        "first_pass_success_rate": _rate(first_pass, len(complete)),
        "attempt_count": sum(trial["attempts"] for trial in trials),
        "retries": sum(trial["attempts"] - 1 for trial in trials),
        "validation_checks": checks, "validation_failures": failures,
        "validation_failure_rate": _rate(failures, checks),
        "human_interventions": sum(record["human_intervention"] for record in records),
        "human_intervention_tasks": intervened,
        "human_intervention_rate": _rate(intervened, len(trials)),
        "escalations": sum(record["escalations"] for record in records),
        "escalated_tasks": escalated, "escalation_rate": _rate(escalated, len(trials)),
        "defect_rate": defect_rate, "observed_defect_rate": observed_defect_rate,
        "defect_task_coverage": defect_coverage,
        "rework_rate": rework_rate, "observed_rework_rate": observed_rework_rate,
        "rework_task_coverage": rework_coverage,
        "files_changed": sum(record["files_changed"] for record in records),
        "tier_distribution": dict(sorted(Counter(str(int(r["tier"])) for r in records).items())),
        "reasoning_settings": dict(sorted(Counter(
            r["reasoning_setting"] for r in records if r["reasoning_setting"] is not None
        ).items())),
        "reasoning_unknown_records": sum(r["reasoning_setting"] is None for r in records),
        "measurement_provenance": dict(sorted(Counter(r["measurement"] for r in records).items())),
        "measurements": measurements,
    }


def recommend(records, minimum_samples=20, success_threshold=0.95):
    """Return reviewable escalation suggestions from terminal measured trials only.

    A high success rate at the current tier does not establish a lower tier's
    quality, so this function never recommends a downgrade without such trials.
    Synthetic and manual records, or a mix of provenance within a trial, are excluded.
    """
    if (isinstance(minimum_samples, bool) or not isinstance(minimum_samples, int)
            or minimum_samples < 2):
        raise ValueError("minimum_samples must be an integer of at least 2")
    if (isinstance(success_threshold, bool) or not isinstance(success_threshold, (int, float))
            or not math.isfinite(success_threshold) or not 0 <= success_threshold <= 1):
        raise ValueError("success_threshold must be between 0 and 1")
    grouped = defaultdict(list)
    for trial in _trials(records):
        group = trial["records"]
        if trial["terminal"] is None or any(r["measurement"] != "measured" for r in group):
            continue
        initial = next((r for r in group if r["attempt"] == 1 and r["stage"] == "implementation"),
                       next(r for r in group if r["attempt"] == 1))
        grouped[(initial["project_id"], initial["strategy"],
                 initial["category"], int(initial["tier"]))].append(trial)
    suggestions = []
    for (project_id, strategy, category, tier), trials in sorted(grouped.items()):
        if len(trials) < minimum_samples:
            continue
        success_rate = sum(t["terminal"]["task_success"] for t in trials) / len(trials)
        first_pass_rate = sum(
            t["terminal"]["task_success"] and t["attempts"] == 1 for t in trials
        ) / len(trials)
        if min(success_rate, first_pass_rate) >= success_threshold:
            continue
        suggestions.append({
            "project_id": project_id, "strategy": strategy, "category": category,
            "tier": tier, "task_samples": len(trials),
            "success_rate": success_rate, "first_pass_success_rate": first_pass_rate,
            "success_threshold": success_threshold,
            "action": "review_escalation" if tier < 4 else "review_human_support",
            "recommended_tier": tier + 1 if tier < 4 else None,
            "apply_automatically": False,
            "rationale": "Measured terminal trials missed the completion or first-pass quality target; "
                         "review task mix, risk, and held-out trials before changing policy.",
        })
    return suggestions
