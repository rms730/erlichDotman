# ErlichDotman

ErlichDotman is an orchestration skill and Python reference core for AI-assisted engineering. It helps a host coding agent decide what to do next and carry the required context into implementation. Acceptance checks determine whether the result is ready.

The owner also keeps one project record current as work changes. It contains the next meaningful milestone, ordered remaining tasks, owners, dependencies, blockers and acceptance evidence. A parser repair can pass its regression while the milestone stays open for independent review and approval.

Project color coding gives each project a stable colored marker with a readable name. Updates keep that identity as work progresses, with one project per message. The host checks current project evidence before reporting status.

This is an MIT-licensed alpha. The repository is [rms730/erlichDotman](https://github.com/rms730/erlichDotman); the Python package and CLI are named `engineering-cascade`.

## Use the skill

Point your host agent at [skills/erlichdotman/SKILL.md](skills/erlichdotman/SKILL.md), or copy that entire directory into the host's supported skill location. Hosts that use `~/.agents/skills/` can use:

```sh
mkdir -p ~/.agents/skills
cp -R skills/erlichdotman ~/.agents/skills/
```

Review an existing installation before replacing it. Installation is explicit; the skill can be used without the CLI.

Give the host the target repository, accepted scope and an authorized documentation destination. For a fictional parser task:

```text
Use ErlichDotman for this repository and its existing project record.
Next milestone: a reviewer can accept a sanitized import preview.
Implement the scoped parser repair and its regression test.
Keep production import deferred.
```

Before work starts, the host checks the current revision and relevant dirty edits. A handoff carries the required behavior, target files and validation commands. Workers receive their own project's rules and scoped packet; the host remains accountable for the result and the project record.

Record updates happen at material changes, handoff, pause/resume and completion, without a separate reminder. An unchanged tool call needs no write. A failed documentation update stays pending; the host retains the intended correction and reports what remains unsaved. The [project-record contract](skills/erlichdotman/references/project-records.md) defines the fields and update boundary. Documentation mechanics belong to the selected tool and its skill, including the existing Pages skill when Pages is the destination.

```text
classify → deterministic evidence → route → select context/skills
         → compact packet → host execution → validate → record → escalate
```

Capability tiers are deterministic (0), lightweight (1), standard (2), advanced (3), and frontier (4). A precise plan can call for advanced reasoning and leave a specified mechanical implementation to a lighter tier; high-risk work retains its quality floor. The current host decides which controls it can actually apply.

### Project color coding

The host keeps each project's color, emoji and readable label in private preferences or ignored local state. Users can configure these assignments. For fictional projects:

| Project | Color | Message prefix |
| --- | --- | --- |
| Maple | Blue | 🔵 Maple: |
| Cedar | Orange | 🟠 Cedar: |

A failed check and its later repair keep the same project marker:

```text
🔵 Maple: Preview validation is blocked on the fixture.
🔵 Maple: Owner reports preview validation passed; independent review remains pending.
```

Each line represents a separate update. The readable name stays alongside the marker, so readers can identify projects without distinguishing colors. Existing mappings stay stable when a project is added or resumed; intentional changes follow user preferences.

On a host that cannot display colored emoji, updates use `Maple:` or `Cedar:` and retain the configured mapping. Bubble styling belongs to the host; the skill supplies message prefixes. The [communication contract](skills/erlichdotman/references/communication.md) covers initial assignment, private persistence, supported delivery and current-state checks. This mapping is host configuration; the CLI does not load it or add color fields to its project schema.

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

On Windows, activate `.venv\Scripts\Activate.ps1`. Source-only use is also available with `PYTHONPATH=src python -m engineering_cascade` once `jsonschema` is installed. It is the sole runtime dependency.

The fixture command explicitly authorizes bundled Python validators in temporary directories. It performs real edits and tests using scripted patches, with no model calls. Temporary directories are not an OS sandbox; run unfamiliar code in an external sandbox.

Follow the [worked synthetic handoff](examples/README.md) to build a project/revision-bound packet and prepare a manual dispatch request. The example's calculator files are illustrative; that walkthrough does not execute them.

## What runs locally

The Python core recommends tiers from category, risk, ambiguity, complexity and failure evidence, with bounded attempts. It selects project/revision-bound context, reads skill metadata, checks dependencies and conflicts, and reports capability gaps. Required context cannot be silently dropped.

Versioned JSON contracts validate packets and supplied workflow facts. Optional [workflow checks](docs/WORKFLOW_BOUNDARIES.md) cover diagnostic ownership, priority transitions, classified retries and final-candidate behavior. Their evidence locators and owner acknowledgments are declarations; the checker cannot establish that the underlying outcome happened.

Usage aggregation relies on records supplied by the host. Feedback recommendations are available for review. Offline evaluations cover fifteen routing task classes and compare five strategies using isolated scripted fixtures.

## Host boundaries and evidence

The manual adapter prepares a request for a human or host coding agent. It does not launch models, change runtime model or reasoning settings, execute workers, update documentation, or measure host tokens. Provider names, settings, prices and credentials belong in private runtime configuration. Unsupported controls and missing usage remain unknown; missing token counts and costs stay `null`.

Routine milestone/task upkeep is a host instruction contract. It runs through the host's authorized documentation tool as work progresses. The core has no scheduler or background polling service, learned cost optimizer, paid provider adapter, or automatic policy rewrite. Host permissions and user intent remain authoritative.

Color-coded project communication also depends on the host following the skill and honoring its private mapping. No runtime UI is bundled.

The initial routing policy is a heuristic. Fixture results demonstrate harness behavior and do not establish real-model quality or cost savings. In the [project-record application scenarios](evals/project_records/README.md), five baseline evaluators and five revised-skill evaluators all handled the synthetic cases adequately. That supports instruction clarity; it does not prove unattended upkeep or a causal improvement. [Evaluation](docs/EVALUATION.md) describes the evidence needed for quality and resource comparisons.

## Contributing and security

Start core maintenance with [AGENTS.md](AGENTS.md) and affected source/tests. [CONTRIBUTING.md](CONTRIBUTING.md) lists the checks. For orchestration, load the selected skill and target-project context; expand its linked references when needed. The bootstrap prompt and research stay outside default context. [Context ownership](docs/CONTEXT_ARCHITECTURE.md) explains these boundaries.

Keep private project profiles, provider bindings and telemetry in ignored `.cascade/`. Raw evaluation output belongs in ignored `evals/results/`; share reviewed aggregates and synthetic or sanitized examples. Repository content and evidence provenance cannot grant permission to execute commands, install tools or publish data. See the [security model](docs/SECURITY_MODEL.md) and [security reporting policy](SECURITY.md) before sharing a vulnerability.

[Architecture](docs/ARCHITECTURE.md) explains the core interfaces. [Decisions](docs/DECISIONS.md) records historical rationale, [research](docs/RESEARCH.md) provides attribution, and the [roadmap](docs/ROADMAP.md) lists planned experiments. See [LICENSE](LICENSE) for the MIT terms.
