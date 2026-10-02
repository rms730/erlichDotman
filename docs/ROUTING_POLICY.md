# Routing policy

The bootstrap policy is an explicit, uncalibrated heuristic. It chooses a credible starting capability; it does not estimate a numerical probability of success or prove optimal cost.

| Tier | Role |
| --- | --- |
| 0 deterministic | Tests, compiler, search, schema checks or other operations requiring no inference |
| 1 lightweight | Clear, bounded, mechanical work |
| 2 standard | Ordinary feature, API, UI, review or refactor work |
| 3 advanced | Architecture, unclear debugging, unfamiliar systems or consequential changes |
| 4 frontier | Critical risk or irreversible changes where further reasoning is justified |

`examples/policy.json` maps task categories, risk and evidence signals to floors. Complexity and ambiguity add floors: medium → 2, high → 3. Architecture/planning starts at 3. A low-risk, low-ambiguity mechanical implementation can downgrade to 1 once a precise packet exists. Security and migration categories preserve their category floor even if marked mechanical. Risk/signals prevent a deterministic flag from disguising consequential work.

Safe tasks explicitly resolvable with deterministic operations use tier 0. A failed implementation raises the next attempt above the previously attempted tier, capped at 4. An unclear root cause starts advanced debugging. Insufficient context expands its estimate independently of the model tier, bounded by policy. At the attempt limit, return `needs_human`; do not retry silently.

`evidence.attempts` counts completed implementation attempts, not planning legs. `validation_failed` should describe observed tests/compiler results. `previous_tier` describes the actual attempted capability when known. Reason codes record each applied rule without emitting a long explanation.

A routing decision never means a destructive migration, shell command, third-party installation or publication is authorized. Host authorization is a separate gate. Skills and adapters may also be unavailable; report that gap rather than claiming execution.

The [optional runtime control contract](RUNTIME_CONTROLS.md) binds a current decision to explicit private model/reasoning profiles and bounded launch state. It requires a matching host acknowledgment before reporting dispatch ready, keeps requested/effective observations distinct, and stops unsupported paths. The manual adapter still launches no models; acknowledgments and counters are supplied declarations.

The [optional workflow sidecar](WORKFLOW_BOUNDARIES.md) refines retries using a supplied stall classification and evidence/hypothesis. It separates ownership, tooling/access and context remedies from implementation/reasoning escalation, permits evidence-capture retries and preserves floors/attempt limits. Without it the version-1 heuristic above is unchanged. Classification and opaque evidence content remain host judgments.

For expected-total-cost routing, collect latency, costs of every leg/retry, human attention and rework on held-out tasks. Calibrate project/category-specific decisions after enough observations. Review feedback recommendations before editing policy; never tune on the same fixtures used for the final comparison.
