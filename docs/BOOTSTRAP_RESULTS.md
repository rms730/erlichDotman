# Bootstrap verification — 2026-09-30

Historical bootstrap evidence, not a runtime instruction or a claim about the latest checkout. New changes require fresh verification.

## Delivered

A Python 3.11+ reference core, a standalone thin Agent Skills entrypoint, strict packaged JSON contracts, explicit tier/risk/context policy, revision-bound project context, required-fact handoffs, metadata-only skill composition, manual host dispatch, truthful telemetry and reviewable feedback. MIT license, contribution/security guidance, primary-source attribution, private-state exclusions, CI and build metadata accompany the code.

No hosted daemon, model-training stack, vector store, provider framework or paid model calls were needed. The only declared runtime dependency is `jsonschema` (with its upstream transitive dependencies). The wheel contains the library and canonical schemas; the source distribution also contains skills, docs, examples and offline eval inputs.

## Checked evidence

| Check | Result |
| --- | --- |
| Behavior tests | 158 passed in the clean Python 3.11 virtual environment |
| Ruff | Passed |
| Installed dependency consistency | Passed |
| Routing evaluation | 15 task classes × 5 strategies: 75 checks passed |
| Scripted fixture evaluation | 6 fixtures × 5 strategies: 30 replay expectations passed; no contract/harness/execution errors |
| Skill frontmatter/scaffold validator | Passed |
| Independent skill forward-test | Correctly stopped stale/mixed context, missing acceptance facts, budget overflow and unauthorized installation; retained unknown controls/usage |
| Independent code review | Addressed validator path-alias bypass, protected-floor grading, per-project feedback scope, terminal ordering, integral JSON numbers, unbounded attempt allocation and subprocess output/descendant cleanup |
| Packaging | Source distribution and wheel build; wheel schema/CLI smoke test outside the checkout |
| CI | Configured for Python 3.11 and 3.13, least-privilege read permissions and pinned official actions |

The first remote run passed Python 3.11 and exposed a parser-depth assumption on Python 3.13. An explicit 64-level JSON nesting budget replaced reliance on interpreter recursion behavior, with acceptance/rejection and quoted-bracket regression checks.

Fixtures exercise a boundary bug, refactor, nested API/multi-file behavior, executable documentation, key-validation security behavior and operation-count performance acceptance. Nine other classes currently have routing-contract coverage rather than executable implementations.

Eight deliberately scripted baseline quality failures are expected by the replay tests. The intelligent/progressive scripts finish all six fixtures with two retries; these scripts were authored to exercise control flow. Those outcomes are **not real-model quality evidence**. The architecture-high/implementation-low strategy checks stage routing and replay behavior; no actual model architecture leg was executed. Do not tune live policy from these outcomes.

## Efficiency limits

No real inference token, price, reasoning or end-to-end model-latency measurements were available for the offline suites. Token and cost totals remain `null`. Executed validator latency is real but does not measure inference latency. Context estimates are heuristics. There is no supported claim of token savings, cost savings or optimal packet format yet.

Fresh subprocess validators and project-bound manifests are useful controls, not a general security sandbox. Windows behavior is not verified by this CI; POSIX process-group cleanup is tested locally. Dirty-tree freshness requires caller-provided evidence; automatic fingerprints are on the roadmap.

## Publication boundary

The public payload contains synthetic examples and no private project inventory, credentials, provider bindings, raw eval traces or local caches. Git commits use a GitHub no-reply identity. Generated build artifacts and private local state are ignored. Public visibility, package-index publication and release tags require separate operator authorization.

The next three experiments are a measured runtime adapter and held-out baseline trials, comparative handoff compression trials, and reviewable policy calibration from those measurements. See [ROADMAP.md](ROADMAP.md).
