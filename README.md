# ErlichDotman

Route AI-assisted engineering work through the least expensive credible capability, preserve compact project context, and escalate from validation evidence.

This is an alpha reference core and a portable orchestration skill. It prepares work for a host coding agent; it does not launch models. Capability tiers are deterministic (0), lightweight (1), standard (2), advanced (3), and frontier (4). Provider names, reasoning settings, prices, and credentials belong in private runtime configuration.

## Try it

Python 3.11 or newer is required. From a checkout:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
engineering-cascade route examples/task.json --policy examples/policy.json
engineering-cascade eval --root . --mode routing
engineering-cascade eval --root . --mode fixtures --execute
python -m pytest
```

On Windows, activate `.venv\Scripts\Activate.ps1`. Source-only use is also available with `PYTHONPATH=src python -m engineering_cascade` once `jsonschema` is installed.

The fixture command explicitly authorizes bundled Python validators in temporary directories. It performs real edits and tests using **scripted patches**, with no model calls. Temporary directories are not an OS sandbox; run unfamiliar code in an external sandbox.

## Use the skill

The skill is named `erlichdotman`, displayed as **ErlichDotman**. Point a host agent at [skills/erlichdotman/SKILL.md](skills/erlichdotman/SKILL.md), or copy that whole skill directory into the host's supported skill location. Nothing is installed automatically. The skill works without the CLI; the CLI makes contracts, selection, and measurement deterministic. Host permissions and user intent remain authoritative.

The repository is [rms730/erlichDotman](https://github.com/rms730/erlichDotman). The existing Python package and CLI remain named `engineering-cascade`.

For core maintenance, start with `AGENTS.md` and affected source/tests. For orchestration, load only the selected skill and target-project context; its links are conditional, not a preload list. Workers receive their own project rules and bound packet. The bootstrap prompt and research are outside default context. [Context ownership](docs/CONTEXT_ARCHITECTURE.md) documents the load paths.

The control plane follows:

```text
classify → deterministic evidence → route → select context/skills
         → compact packet → host execution → validate → record → escalate
```

A precise plan can use advanced reasoning, then hand a mechanical implementation to a lighter tier. High-risk work keeps its quality floor. See [the worked handoff](examples/README.md).

## What works now

- Explicit category, risk, ambiguity, complexity, and failure-based routing with bounded attempts.
- Project/revision-bound context and handoffs; required context cannot be silently dropped.
- Metadata-only skill discovery, compatible selection, dependency/conflict handling, and capability-gap reporting.
- Strict versioned JSON contracts, telemetry aggregation, and reviewable feedback recommendations.
- Fifteen routing task classes and isolated fixture evaluations comparing five strategies.
- A manual adapter that reports unavailable model controls and usage honestly.
- Optional workflow checks for declared diagnostic ownership, priority transitions, evidence-driven retries and retained candidate behavior; [scope and limits](docs/WORKFLOW_BOUNDARIES.md).

The initial policy is a heuristic. There is no learned cost optimizer, paid provider adapter, scheduler, or automatic policy rewrite. Fixture results demonstrate harness behavior, not real-model quality or cost savings. Missing token counts and costs remain `null`.

## Documentation by task

[Architecture](docs/ARCHITECTURE.md) explains the boundaries. [Decisions](docs/DECISIONS.md) is historical rationale for architectural review. [Evaluation](docs/EVALUATION.md) defines quality and resource accounting. [Research](docs/RESEARCH.md) supplies attribution for explicit research/license review. [Security](docs/SECURITY_MODEL.md) covers trust and execution limits. [Roadmap](docs/ROADMAP.md) identifies the next experiments.

Private project profiles, provider bindings, and telemetry belong in ignored `.cascade/`. Keep raw eval output in ignored `evals/results/`; share only reviewed aggregates. The public examples describe fictional projects.

MIT licensed. See [CONTRIBUTING.md](CONTRIBUTING.md) for checks and contribution scope.
