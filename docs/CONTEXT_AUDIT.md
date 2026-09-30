# Context-architecture audit — 2026-09-30

Baseline: commit `99287bb`, the completed bootstrap. The audit applies the hierarchy in [CONTEXT_ARCHITECTURE.md](CONTEXT_ARCHITECTURE.md) without changing working routing, context selection, handoff, adapter or telemetry components.

## Findings and targeted changes

1. The full bootstrap prompt was not committed or automatically read by the core. Its initialization-only status was implicit; both entrypoints now state the boundary.
2. `AGENTS.md` was concise but repeated runtime methodology and blanket validation guidance. It now owns durable core-development rules and points to contributor checks by need. Downstream workers do not inherit these build rules.
3. `SKILL.md` was already within the requested size range. It now makes conditional reads and worker handoffs explicit, retaining project binding, current-code grounding, acceptance facts, safety floors and unsupported-capability honesty.
4. The portable metrics reference duplicated the telemetry/evaluation field guide. It was replaced with a short outcome-recording boundary. Detailed contracts and comparison methods remain in `src/`, `docs/EVALUATION.md` and `evals/`.
5. Historical decisions, implementation plans and bootstrap results were available alongside current docs without a status warning. They are now labeled snapshots, including the old plan's interface sketches. Research is labeled explicit-use only.
6. The escalation reference repeated the initial three-attempt value. It now reads the active policy instead of perpetuating a bootstrap setting.
7. The runtime/build/worker loading contract was unspecified. A conditional context map and reproducible footprint helper now distinguish the layers. Existing private-state exclusions and metadata-only discovery were already suitable and remain unchanged.

## Approximate footprint

Method: `ceil(Unicode characters / 4)`, including Markdown and frontmatter. No tokenizer or metered host usage is available; these are reproducible estimates, not exact token counts.

| Repository-controlled context | Before | After | Change |
| --- | ---: | ---: | ---: |
| `AGENTS.md` | 456 | 367 | −89, about 20% |
| Core runtime `SKILL.md` | 857 | 818 | −39, about 5% |
| Orchestration inside the core checkout, both entrypoints | 1,313 | 1,185 | −128, about 10% |
| Normal synthetic orchestration, skill + compact profile/task | 1,167 | 1,128 | −39, about 3% |

A normal **core maintenance** task starts with AGENTS: about 367 fixed instruction tokens, plus task and affected code/tests. A normal **external-project orchestration** starts with the selected skill: about 818 fixed instruction tokens; the checked synthetic profile/task adds about 310. Target-project rules, actual source/tests, host/system prompts, tool catalogs and needed references are additional and vary. A **worker** gets its target rules and bound packet/scoped source; there is no default public-core instruction surcharge unless it needs orchestration itself.

Neither always-loaded entrypoint is unnecessarily large. The skill remains inside the requested roughly 500–1,500-token range. Loading every document would be unnecessarily large for routine work: about 8,812 tokens before and 12,000 after, including this audit. Runtime references total about 1,438 before and 1,359 after. Both pools stay outside default context. Added audit/deep documentation increases repository size without increasing the declared routine load. Smaller counts alone do not establish total engineering efficiency.

Reproduce with:

```sh
python scripts/context_footprint.py --baseline 99287bb
```

This helper reads local checkout/ref text to compute counts; it does not send document bodies to an agent, write private state, or modify runtime routing/budgets. The existing 850-token skill-catalog estimate remains a heuristic reservation, not a recalibration from one character estimate.

## Verification

- 158 existing behavior tests: passed after the instruction changes. Offline routing eval: 75/75 checks across 15 tasks; fixture eval: 30/30 checks across six tasks, including eight expected failures from deliberately weak strategies, with no harness or execution errors.
- Skill frontmatter/scaffold validation, Ruff, local reference links and source-distribution contents: checked.
- Independent role-based forward test: appropriate core/orchestrator/worker loading, stale-summary handling, context/acceptance blockers and injection refusal. [Reviewed results](../evals/context_architecture/RESULTS.md) include limitations.

The dry-run is not an empirical completion/resource comparison. No model savings, latency improvement or reduced rework is established. Existing code tests preserve implementation behavior; they cannot enforce a host's prompt assembly. The manual adapter cannot remove existing chat history or system context.

## Remaining duplication and next experiment

Short quality, identity, permission and unknown-usage invariants intentionally recur across build and standalone runtime entrypoints, which may be loaded independently. Portable references and implementation docs share concepts, but serve different audiences; they do not duplicate a full field/policy manual. Historical records still repeat architecture facts as dated evidence and are excluded from routine loading.

Run a paired held-out task experiment with the same model/tool bindings: compare the former context assembly against these role-specific entrypoints, and record actual loaded files, all workflow-leg tokens/cost/latency, acceptance, first pass, interventions and later rework. Include unfamiliar code and dirty/stale summaries. Confirm required-fact retention and quality before attributing total efficiency to the smaller context. That experiment is more valuable than further shortening an already 818-token skill.
