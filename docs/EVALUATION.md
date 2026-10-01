# Evaluation

Separate three questions: does the core enforce its contracts; does an implementation pass independent checks; does orchestration improve measured quality per total resource? Only the first two are exercised offline here.

## Suites

Routing cases cover fifteen classes: tiny bug, feature, refactor, API, UI, migration, flaky test, dependency upgrade, unfamiliar repository, multi-file bug, architecture, security, documentation, review and performance. Expected decision properties are authored independently of the router. These are policy tests, not implementation quality measurements.

Fixture cases create small repositories in fresh temporary directories, apply scripted tier-dependent patches, and run actual validators. Compare frontier-only, lightweight-only, intelligent, advanced-planning/lightweight-implementation, and progressive escalation. Planning and retry legs belong in the same task's accounting. Deliberately weak patches are synthetic test inputs; their rates must never be advertised as real-model success rates.

```sh
engineering-cascade eval --root . --mode routing
engineering-cascade eval --root . --mode fixtures --execute
```

Execution requires explicit opt-in. Report harness errors separately from task quality failures. Baseline quality failures may be expected; unresolved orchestration/check failures must remain visible. Identical validators grade every strategy. Do not change the grader to accommodate a patch.

## Telemetry

Every inference/workflow leg records run/project/task identity, strategy, category, stage, attempt, tier, reasoning setting if exposed, input/output tokens, metered usage/unit if available, cost/currency if available, latency, validation status, escalation delta, files changed, defects/rework and intervention. `task_success` is `null` on intermediate legs and a boolean on a terminal task record. Costs of failed tasks and all retries belong in the numerator.

Aggregate tokens/cost per successful task only when the full set of legs has compatible complete measurements and there is a success denominator. Otherwise return `null` with observed values and coverage. Never interpret unavailable counts as zero, mix currencies or metering units, or substitute context estimates for billed inference. Cost records may include zero for a genuinely free measured call; unknown remains `null`.

Completion, first-pass success, retries, validation failure rate, escalation rate and human intervention rate use explicit denominators. Interim planning legs cannot inflate completed task counts. Keep runs and strategies separate when comparing results. A defect needs an observation window and an independent definition; unavailable follow-up is unknown, not zero defects.

## Real trials

The [exploratory pilot kit](../evals/pilot/README.md) defines a matched eight-task feasibility comparison, capture boundaries and claim limits. [Improvement priorities](IMPROVEMENT_PLAN.md) separate this fixed-model orchestration experiment from a later capability-routing experiment. Draft pilot stage records are not version-1 CLI telemetry; preserve both formats until an explicit compatible integration is implemented.

For larger confirmatory trials, use held-out tasks, frozen policy/model bindings, recorded versions, identical tools/validators and repeated runs. Randomize strategy order. Account for planning, context loading, reviews, retries, latency and human attention. Choose uncertainty estimates appropriate to the design; the small pilot reports descriptive results, not precise general effects. Use task acceptance and a transparent importance rubric instead of inventing an engineering-value scalar.

Feedback excludes scripted/manual observations, requires a minimum measured sample, and emits reviewable category/tier recommendations. It never rewrites defaults. Low-tier evidence suggests a follow-up controlled experiment; it does not establish that the adjacent lower tier succeeds.

See [BOOTSTRAP_RESULTS.md](BOOTSTRAP_RESULTS.md) for the checked milestone and limitations.
