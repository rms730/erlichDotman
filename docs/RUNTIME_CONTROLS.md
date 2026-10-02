# Optional runtime control contract

The manual adapter prepares work; it has no model launcher. This optional path checks explicit private model bindings, supplied launch state and host acknowledgments. It grants no permissions, changes no running jobs and makes no billing estimate. Existing version-1 routing/packet/telemetry formats and legacy dispatch remain compatible; legacy dispatch does not establish policy enforcement.

## Profiles and limits

`runtime_policy` maps `routine`, `engineering` and `escalation` to explicit model/reasoning settings. [The example](../examples/runtime-policy.json) uses fictional model identifiers; actual bindings belong in ignored private state. `engineering` is the default. `routine` requires a lightweight decision, mechanical work, low risk/complexity/ambiguity, no signals, and implementation/documentation/validation stage. `escalation` requires an explicit escalation stage with `validation_failure`, `unclear_root_cause` or `capability_gap`, or a review with high/critical risk or security/irreversible/production-critical signals. A frontier decision outside these paths stops rather than silently downgrading.

The initial settings are two total implementation attempts and one concurrent worker. They bound speculative retries and coordination while preserving one retry; they are configurable preferences, not a measured optimum. The stricter routing/runtime attempt limit applies. `launch_context` supplies completed attempts, currently active workers, a stop flag and project/task/revision/run binding. Retries require matching classified workflow evidence. The check admits one additional worker only when below the limit.

These counters are declarations. The host owns truthful, atomic worker admission and attempt accounting across its configured scope; the core has no queue, reservation or race protection. Missing facts, contradictory identities, exhausted limits, stop requests and non-ready routing decisions fail closed.

## Request and acknowledgment

Build the packet with the existing worked example, then use the synthetic launch state:

```sh
engineering-cascade dispatch .cascade/packet.json --decision .cascade/decision.json --policy examples/policy.json --task examples/task.json --runtime-policy examples/runtime-policy.json --launch examples/launch.json
```

This returns a validated `runtime_dispatch` with `blocked_host_controls` and exit status 1. Its `execution_request` binds packet/workflow digests, classified task, active policies and launch state into a request ID. A changed input requires a new acknowledgment; observations also reject a changed or omitted packet/workflow. Tier 0 requests no model/reasoning controls but still requires bounded host accounting.

The host supplies a `host_acknowledgment` containing that exact request, `accepted`, and booleans for `model_selection`, `reasoning_selection`, `attempt_limit` and `parallel_limit`. Only a matching acknowledgment accepting every required control permits `awaiting_host_execution`. Add `--host-ack .cascade/host-ack.json` to recheck it. Unsupported controls remain blocked. Do not manufacture a positive acknowledgment for a host lacking these controls.

The manual adapter's own execution and selection capabilities remain false. An accepted acknowledgment describes another host's declared ability to execute the request; it is not an execution receipt, authorization grant or proof. No host integration or provider client is bundled. Calls outside this opt-in path remain outside its checks.

## Observations and accounting

`record-execution` checks a supplied `execution_observation` bound to the exact request ID. Requested and effective model/reasoning remain distinct. Effective settings require a runtime-evidence locator; otherwise keep them `null`. Setting mismatches are retained as `host_control_violation`; incomplete observations return `host_execution_unverified`. Matching supplied settings return `host_controls_observed`, which does not mean task acceptance or independent evidence verification.

```sh
engineering-cascade record-execution .cascade/prepared.json .cascade/observation.json
```

Input, cached-input and output tokens, latency and cost stay `null` when unavailable. Supplied usage measurements require a usage-evidence locator. Cached input is a subset of total input when both are supplied. A supplied cost requires a separate billing-evidence locator and its unit/currency. The checker validates declarations and never fetches receipts, derives cost from token rates or fills unknown values with zero.

For outcome comparisons, retain every setup/parent/implementation/validation/review/retry leg and human effort in private evidence. These per-request observations do not automatically capture the total. Dots conversations and Work/Codex task usage have different accounting boundaries; [OpenAI's dots documentation](https://learn.chatgpt.com/docs/dots) explains them. [Published pricing](https://learn.chatgpt.com/docs/pricing) distinguishes credit rates from included subscription usage. No rate table is hardcoded here, and no savings claim follows from synthetic tests.
