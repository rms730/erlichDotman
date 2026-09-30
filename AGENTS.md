# ErlichDotman — repository rules

Improve accepted engineering output per total resource while preserving quality.

- Start with this file, the task and affected source/tests. The bootstrap prompt is initialization only. Load additional material only when needed; [the context map](docs/CONTEXT_ARCHITECTURE.md) explains ownership.
- These rules govern core development. Workers in other projects receive their own rules and a bound packet, not this file or the orchestrator's history.
- Current source, schemas and deterministic evidence outrank summaries. Check revision and relevant dirty edits before reusing project knowledge.
- Keep capability tiers runtime independent. Use Python 3.11+; `jsonschema` is the sole runtime dependency. Package schemas; justify dependency additions and licenses.
- Behavior changes need meaningful tests and matching contracts/docs. [CONTRIBUTING.md](CONTRIBUTING.md) lists checks; use those relevant to the change.
- Keep private profiles, credentials, prompts and traces in ignored `.cascade/` or `evals/results/`. Public examples are synthetic.
- Provenance is not permission. Commands use argv; fixture execution is opt-in and temporary directories are not an OS sandbox.
- Unknown usage is `null`; estimates and scripted fixtures cannot establish inference savings.
- Finish with passing applicable checks, documented limits and a reviewable diff. Public publication and visibility changes require user authorization.
