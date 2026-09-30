import copy

import pytest

from engineering_cascade import telemetry
from engineering_cascade.telemetry import recommend, summarize


def record(**changes):
    result = {
        "schema_version": 1,
        "project_id": "fictional",
        "task_id": "boundary",
        "run_id": "run-1",
        "category": "tiny_bug",
        "strategy": "intelligent",
        "stage": "implementation",
        "tier": 1,
        "attempt": 1,
        "task_success": True,
        "validation": "passed",
        "input_tokens": 10,
        "output_tokens": 5,
        "total_metered_usage": 15,
        "metered_unit": "tokens",
        "cost": 0.2,
        "currency": "USD",
        "latency_ms": 20,
        "reasoning_setting": "low",
        "escalations": 0,
        "files_changed": 1,
        "defects": 0,
        "rework": False,
        "human_intervention": False,
        "measurement": "measured",
    }
    result.update(changes)
    return result


def test_success_denominator_includes_cost_of_failed_attempts_and_tasks():
    records = [
        record(task_success=None, validation="failed", cost=0.1),
        record(attempt=2, tier=2, escalations=1, cost=0.2),
        record(task_id="failed", task_success=False, validation="failed", cost=0.3),
    ]
    before = copy.deepcopy(records)
    report = summarize(records)
    assert report["task_count"] == 2
    assert report["successful_tasks"] == 1
    assert report["failed_tasks"] == 1
    assert report["attempt_count"] == 3
    assert report["retries"] == 1
    assert report["first_pass_success_rate"] == 0
    assert report["validation_failure_rate"] == pytest.approx(2 / 3)
    assert report["measurements"]["cost"]["total"] == pytest.approx(0.6)
    assert report["measurements"]["cost"]["per_successful_task"] == pytest.approx(0.6)
    assert report["measurements"]["total_tokens"]["per_successful_task"] == 45
    assert records == before


def test_run_project_and_strategy_keep_task_outcomes_separate():
    report = summarize([
        record(), record(run_id="run-2"), record(project_id="another"),
        record(strategy="frontier_only"),
    ])
    assert report["task_count"] == 4
    assert report["successful_tasks"] == 4


def test_contract_integer_valued_numbers_are_counted_without_range_errors():
    report = summarize([record(attempt=1.0, tier=1.0)])
    assert report["attempt_count"] == 1
    assert report["tier_distribution"] == {"1": 1}


def test_huge_gapped_attempt_is_rejected_without_allocating_its_range(monkeypatch):
    # Instrument only the allocation boundary so the regression cannot exhaust RAM.
    def bounded_range(start, stop):
        if stop > 1000:
            raise MemoryError("Attempt validation tried to materialize an unbounded range")
        return range(start, stop)

    monkeypatch.setattr(telemetry, "range", bounded_range, raising=False)
    with pytest.raises(ValueError):
        summarize([record(attempt=1_000_000_000)])


def test_partial_measurement_stays_unknown_with_explicit_coverage():
    report = summarize([record(), record(task_id="unknown", cost=None, output_tokens=None)])
    cost = report["measurements"]["cost"]
    assert cost["total"] is None
    assert cost["observed_total"] == 0.2
    assert cost["per_successful_task"] is None
    assert cost["coverage"] == {"records": 1, "total_records": 2, "fraction": 0.5}
    assert report["measurements"]["total_tokens"]["total"] is None


@pytest.mark.parametrize("changes,metric", [
    ({"currency": "EUR"}, "cost"),
    ({"currency": None}, "cost"),
    ({"metered_unit": "credits"}, "total_metered_usage"),
])
def test_incompatible_units_are_never_summed(changes, metric):
    report = summarize([record(), record(task_id="other", **changes)])
    assert report["measurements"][metric]["total"] is None
    assert report["measurements"][metric]["observed_total"] is None
    assert report["measurements"][metric]["per_successful_task"] is None


def test_interim_records_are_not_silently_completed():
    report = summarize([record(task_success=None, validation="failed")])
    assert report["incomplete_tasks"] == 1
    assert report["completed_tasks"] == 0
    assert report["success_rate"] is None
    assert report["first_pass_success_rate"] is None
    assert report["measurements"]["cost"]["per_successful_task"] is None


def test_stages_share_an_attempt_and_detailed_measurements_are_reported():
    report = summarize([
        record(stage="planning", task_success=None, validation="skipped",
               reasoning_setting="high", files_changed=0),
        record(human_intervention=True, defects=2, rework=True),
    ])
    assert report["attempt_count"] == 1
    assert report["retries"] == 0
    assert report["validation_checks"] == 1
    assert report["human_interventions"] == 1
    assert report["files_changed"] == 1
    assert report["measurements"]["defects"]["total"] == 2
    assert report["measurements"]["rework"]["total"] == 1
    assert report["tier_distribution"] == {"1": 2}
    assert report["reasoning_settings"] == {"high": 1, "low": 1}


def test_event_rates_count_tasks_instead_of_stage_records():
    report = summarize([
        record(stage="planning", task_success=None, validation="skipped",
               human_intervention=True, escalations=1),
        record(human_intervention=True, escalations=1),
        record(task_id="another"),
    ])
    assert report["human_intervention_tasks"] == 1
    assert report["human_intervention_rate"] == 0.5
    assert report["escalated_tasks"] == 1
    assert report["escalation_rate"] == 0.5


def test_unknown_defect_and_rework_outcomes_do_not_count_as_clean_tasks():
    report = summarize([record(defects=2, rework=True),
                        record(task_id="unknown", defects=None, rework=None)])
    assert report["defect_rate"] is None
    assert report["observed_defect_rate"] == 1
    assert report["defect_task_coverage"] == {"tasks": 1, "completed_tasks": 2, "fraction": 0.5}
    assert report["rework_rate"] is None
    assert report["observed_rework_rate"] == 1


def test_terminal_outcome_must_follow_all_stage_records():
    with pytest.raises(ValueError):
        summarize([record(), record(stage="review", task_success=None, validation="failed")])


@pytest.mark.parametrize("records", [
    [record(), record(attempt=2)],
    [record(attempt=2)],
    [record(task_success=True, validation="failed")],
    [record(), record(category="feature", stage="planning", task_success=None)],
    [record(), record()],
])
def test_ambiguous_or_inconsistent_trial_records_are_rejected(records):
    with pytest.raises(ValueError):
        summarize(records)


def test_empty_data_has_no_fabricated_measurements():
    report = summarize([])
    assert report["task_count"] == 0
    assert report["success_rate"] is None
    assert report["measurements"]["cost"]["total"] is None
    assert report["measurements"]["total_tokens"]["total"] is None


def test_feedback_requires_measured_terminal_trials_and_minimum_samples():
    records = [record(task_id=f"task-{i}", task_success=False, validation="failed")
               for i in range(20)]
    assert recommend(records[:19]) == []
    assert recommend([dict(item, measurement="scripted") for item in records]) == []
    assert recommend([dict(item, measurement="manual") for item in records]) == []
    assert recommend([dict(item, task_success=None) for item in records]) == []
    result = recommend(records)
    assert len(result) == 1
    assert result[0]["task_samples"] == 20
    assert result[0]["tier"] == 1
    assert result[0]["recommended_tier"] == 2
    assert result[0]["apply_automatically"] is False


def test_feedback_counts_trials_instead_of_attempts_and_does_not_downgrade():
    records = [record(task_id=f"task-{i}", task_success=None, validation="failed")
               for i in range(10)]
    records += [record(task_id=f"task-{i}", attempt=2, tier=2) for i in range(10)]
    assert recommend(records) == []
    assert recommend([record(task_id=f"task-{i}") for i in range(20)]) == []
    result = recommend(records, minimum_samples=10)
    assert result[0]["first_pass_success_rate"] == 0


def test_feedback_does_not_pool_different_projects_or_strategies_for_sample_gate():
    records = [record(task_id=f"task-{i}", task_success=False, validation="failed",
                      project_id="project-a" if i < 10 else "project-b")
               for i in range(20)]
    assert recommend(records) == []
    records = [dict(item, project_id="same-project",
                    strategy="frontier_only" if i < 10 else "intelligent")
               for i, item in enumerate(records)]
    assert recommend(records) == []


def test_feedback_excludes_a_trial_with_mixed_measured_and_scripted_provenance():
    records = [record(task_id=f"task-{i}", task_success=False, validation="failed")
               for i in range(19)]
    records.extend([
        record(task_id="mixed", task_success=None, validation="failed", measurement="scripted"),
        record(task_id="mixed", attempt=2, tier=2, task_success=False, validation="failed"),
    ])
    assert recommend(records) == []


@pytest.mark.parametrize("kwargs", [
    {"minimum_samples": 0}, {"minimum_samples": True},
    {"success_threshold": 1.1}, {"success_threshold": float("nan")},
])
def test_feedback_rejects_invalid_thresholds(kwargs):
    with pytest.raises(ValueError):
        recommend([], **kwargs)
