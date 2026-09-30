# Initial milestone implementation plan

Historical, completed bootstrap plan. Its execution assignments and interface sketches are not instructions for future tasks. Read current source/schemas and the relevant tests for current behavior.

Goal: deliver the small core and thin skill defined in [DECISIONS.md](DECISIONS.md).

Execution: native coordination with independent, bounded agents for research, context/skill selection, and telemetry/evaluation. The user requested autonomous reversible decisions and appropriate delegation. This overrides repeated design/plan approval gates in the local Superpowers workflow; public publication remains gated.

## Tasks

- [x] Establish versioned contracts and explicit policy. Test malformed input, unknown fields, risk floors, deterministic routing, downgrade, escalation, retry exhaustion, and non-mutating decisions before implementation.
- [x] Build context and handoff functions. Test project/revision isolation, path escape and symlinks, required-item budget exhaustion, freshness, and packet rendering. Select compatible skills within a metadata budget; discovery does not load bodies or install packages.
- [x] Build telemetry and offline evaluation. Test partial usage, denominator correctness, failed-task costs, finite retries, validator timeouts, fixture failure exit codes, and measured-only feedback recommendations. Compare five strategies without manufacturing model usage.
- [x] Integrate CLI, manual adapter, packaged contracts, synthetic examples, and thin skill. Exercise commands end to end; forward-test the skill with a realistic project-mixing request.
- [x] Review architecture/security, run all checks, build and smoke-test a wheel, record honest results, and commit logical units. Audit the exact tracked payload before any private push. Request approval before making it public.

## Interfaces

All public core functions consume and return JSON-compatible dictionaries, validated at entry. Schema definitions are named `task`, `project`, `policy`, `context_item`, `packet`, `skill`, `decision`, and `telemetry`.

- `contracts.validate(document, kind) -> None`; raises `ValueError` for contract violations.
- `routing.route(task, policy, evidence=None) -> dict`: decision with project/task identity, tier, budget, reason codes, validation commands, escalation conditions, and status.
- `context.select_context(items, project_id, revision, budget_tokens) -> dict`: selected items, estimated tokens, omitted IDs; reject mixed/stale items and incomplete required context.
- `context.load_project(path, repository, revision) -> dict`: validate profile binding and freshness.
- `handoff.build_packet(task, project, decision, context, **details) -> dict`; `render_packet(packet) -> str`.
- `skills.discover_skills(roots) -> list[dict]`: JSON sidecar metadata only. `select_skills(required_capabilities, catalog, budget_tokens, allowed_trust) -> dict`.
- `telemetry.summarize(records) -> dict`; `recommend(records, minimum_samples=20, success_threshold=0.95) -> list[dict]`.
- `evaluation.run_suite(root, mode='routing', execute=False) -> dict`: uses project fixtures in subprocesses only when explicitly opted in.

Root coordination owns contracts, policy, routing, CLI and documentation. Delegates own disjoint modules and their tests. No delegate commits or touches Git configuration.

## Review focus

Unknown usage must remain unknown; a cheap failure still contributes to resource totals. Stale or mixed-project context must not pass through. High-risk mechanical work must preserve risk floors. Third-party skill metadata cannot authorize code execution. Validators time out and failed fixture checks make the CLI fail.
