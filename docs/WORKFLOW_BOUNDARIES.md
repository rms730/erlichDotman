# Optional workflow boundaries

The `workflow` version-1 contract supplements existing packets; it does not replace them. Use only sections needed for diagnostic delegation, competing work, a failed implementation retry or candidate assembly. Trivial tasks need no sidecar. Keep records and evidence in ignored private state; [synthetic cases](../evals/workflow_reliability/cases.json) demonstrate the format.

## Interfaces and compatibility

`check_workflow(record)` checks shape and supplied facts. `route(task, policy, evidence=None, workflow=None)` optionally checks task identity and uses a classified retry. `ManualAdapter.prepare(packet, decision, workflow=None, policy=None)` additionally checks project/task/revision binding and preserves the sidecar in its returned dispatch request. A retry sidecar requires the active policy: dispatch checks its policy ID and attempt limit, and includes that limit in the request. Priority inventories are rejected at worker dispatch to preserve project isolation.

```sh
engineering-cascade workflow-check .cascade/workflow.json
engineering-cascade route examples/task.json --policy examples/policy.json --workflow .cascade/workflow.json
engineering-cascade dispatch .cascade/packet.json --decision .cascade/decision.json --workflow .cascade/workflow.json --policy examples/policy.json
```

The example task must have the same project/task identity as the private record. `validate --kind workflow` checks JSON shape only; `workflow-check`, routing and dispatch apply semantic checks. Neither command executes work, verifies evidence content or grants permission.

Before retry dispatch, reroute with the same current sidecar and active policy, then build the packet from that decision. Dispatch enforces supplied attempt exhaustion even if given an older ready decision; it does not recompute tier/context choices from a packet. Policy freshness, stall classification and actual execution limits remain host responsibilities. Evidence collection may occur before any implementation (`completed_attempts: 0`) and does not increment that counter; the host must give diagnostic collection its own finite stopping condition.

Existing packet, decision, task, policy and telemetry schemas retain version 1 unchanged. The new sidecar is independently versioned as `workflow` version 1 in the packaged schema registry. Old API calls, CLI commands and routing without a sidecar retain their behavior. No migration or telemetry conversion is required. Adopt the opt-in sidecar at relevant checkpoints; do not send it to telemetry `summary` or the experimental pilot ledger helper. That helper remains a separate unpublished change.

## Supplied facts the code checks

- **Journey:** one nonempty owner; an accepted transfer selects the new owner, otherwise the old owner remains. Accepted journeys require all declared decisive evidence plus a passed outcome labeled application-level. Passing transport/component checks cannot substitute when labeled accurately.
- **Priority:** a declared before/after inventory, explicit decision and positive chosen WIP limit. Every previous task remains represented; paused/displaced tasks retain checkpoint and continuation; completed tasks name an outcome checkpoint. Active tasks cannot exceed that declared limit. The incoming task must be represented. This inventory stays with the orchestrator.
- **Retry:** sanitized evidence locator or capture blocker, nonempty hypothesis, completed implementation-attempt count, purpose and stall class. Requested/effective tiers describe the previous attempted settings, with unavailable values `null`. Supplied legacy counts/effective tiers cannot contradict them. Capture retries do not trigger the failure increment; ownership/access avoid it, context expands context, and implementation/reasoning failures retain escalation. Risk floors and attempt exhaustion still apply.
- **Integration:** every declared earlier critical behavior has exactly one final-candidate check. Passed/failed checks need evidence and the final revision; accepted candidates cannot contain failed/unchecked behavior. Exclusions require reason, impact and their separate acceptance. `accepted_with_exclusions` is distinct from full acceptance and requires resolved exclusion acceptance. Pending/failed work can be handed off honestly for further validation or repair.

## Host responsibilities and limits

An explained application failure can complete a diagnostic task while its user journey remains failed. Keep that diagnosis separate from claiming the journey itself succeeded; a capture retry does not require first repairing the application.

The code checks declarations, not application truth. It cannot detect an earlier fix omitted from the input inventory, an unlisted active worker, a mislabeled HTTP artifact, a fabricated acknowledgment, an invalid hypothesis, stale dirty contents under the same revision string or a dead evidence locator. The host must inspect current source/dirty edits, retain sanitized evidence, run final-candidate acceptance, confirm transfers/pauses and apply user authority. An accepted outcome field is not release authorization.

Guidance for those judgments belongs in the conditional skill references. The manual adapter still cannot select models, change reasoning, execute workers or meter usage. Classified routing is a heuristic refinement, not measured efficiency evidence. Do not infer missing settings from requested tiers or account counters.

The regression families distinguish deterministic checks and executable synthetic behavior from independent skill simulations. See [their evaluation record](../evals/workflow_reliability/README.md).
