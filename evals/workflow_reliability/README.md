# Workflow reliability regressions — 2026-10-01

These synthetic cases evaluate an optional workflow boundary and conditional skill guidance. All projects, revisions and evidence locators are fictional. No real project was modified, no model-comparison experiment was run and no resource savings are asserted.

## Deterministic and executable checks

Run `python -m pytest tests/test_workflow.py tests/test_cli.py tests/test_routing.py tests/test_adapters.py`. [Cases](cases.json) supply compact records; [interface documentation](../../docs/WORKFLOW_BOUNDARIES.md) separates semantic checks from host judgments.

| Family | Failing case | Passing case |
| --- | --- | --- |
| Delegated streaming failure | No accountable owner; component/transport pass presented as journey acceptance; missing terminal capture | One owner, explicit accepted transfer when relevant, bounded evidence-capture retry with blocker/hypothesis and unknown effective tier |
| Priority interruption | Both tasks active above chosen limit; dropped task; missing continuation | Explicit decision, pause/displacement checkpoint and next step, one active task; parent inventory excluded from worker dispatch |
| Candidate assembly | Earlier critical behavior omitted, unchecked, failed or checked only at its old revision | Full final-candidate coverage; disclosed exclusions with reason/impact and separate acceptance |

The assembly test runs the same synthetic eligibility validator on an earlier repaired guard, an assembled baseline guard and a restored guard. The assembled candidate passes its unrelated new-feature check but fails the eligibility validator; restoring the repair passes. The workflow check rejects the failed candidate's acceptance claim and accepts the repaired record. Only supplied records are checked; the core does not execute or inspect their opaque evidence locators.

A schema-only negative control disabled the three semantic guards in memory without changing source files. Three targeted family tests failed; restoring the real guards made all three pass. This is a mutation check demonstrating that structural validity is insufficient, not a claim that the unmodified historical main had this new API or failed those tests. Existing contract definitions were compared against `21a1529` and remained identical; only the new version-1 `workflow` definition was added.

## Independent skill behavior

Two fresh read-only evaluators received identical [requests and raw artifacts](requests.json), one with the installed pre-change skill and one with the refined source skill. Neither received the intended answers, implementation, rubric or the other's conclusions. Each simulated all three requests in one session; project artifacts were not accessed and no work was dispatched.

Both handled all three cases adequately: they required terminal evidence rather than HTTP success, preserved an interrupted task and kept it out of the new worker's context, and withheld candidate acceptance pending final eligibility checks. Both left effective settings/usage unknown. The refined evaluator explicitly classified the stream stall as ownership/capture, kept the orchestrator accountable across browser delegation, confirmed stopping before freeing WIP capacity and produced a prior-behavior acceptance matrix. The old evaluator also proposed those substantive safeguards without the new explicit wording.

This supports instruction clarity and records no observed before/after failure in these simulations. It does not establish a causal skill improvement, actual owner acceptance, worker prompt contents, engineering quality or efficiency under concurrent live work. The added deterministic guards make selected supplied facts enforceable; host behavior still needs real-task evidence.

## Review and adoption

Independent implementation review found a stale-ready-decision retry gap. Dispatch now requires the active policy for a retry sidecar, verifies its policy ID and rejects exhaustion even with an older ready decision; a regression test covers this. The host must still reroute current tier/context choices and give diagnostic captures a finite stopping condition. No material implementation findings remained after that repair.

The installed skill was not changed. Adopt the reviewed source directory only after separate authorization; default context remains the thin skill plus target inputs, not these evaluation records. Publication/install instructions belong in the completion handoff, not routine runtime context.
