# Architecture

The core makes decisions and validates boundaries; the host agent does the engineering. This keeps policy testable without provider credentials and avoids hiding unsupported runtime features.

| Component | Responsibility | Boundary |
| --- | --- | --- |
| `contracts.py` and packaged schemas | Strict version 1 input validation | No network schema loading; private values excluded from validation errors |
| `routing.py` | Capability and context recommendation | No permission grant, provider choice, or model execution |
| `context.py` | Required-first context selection and profile freshness | One project/revision; bounded estimates; repository-local paths |
| `handoff.py` | Bind facts, constraints and validation into a packet | Missing required facts stop construction |
| `workflow.py` | Check optional bound ownership, priority, retry and integration facts | Declared facts only; no scheduler, evidence verification or permission grant |
| `skills.py` | Read metadata and select compatible capabilities | No body loading, execution, or installation |
| `adapters.py` | Prepare host dispatch | Explicit unsupported controls and unknown usage |
| `validation.py` | Run authorized argv validators | Finite timeout, bounded output; caller owns sandbox/permission |
| `telemetry.py` | Aggregate outcomes and recommend policy review | All attempts counted; unavailable measurements stay unknown |
| `evaluation.py` | Check routing and scripted implementation loops | Isolated bundled fixtures; no inference savings claim |

All functions exchange JSON-compatible dictionaries. The canonical definitions live in `src/engineering_cascade/schemas/contracts.schema.json`, which ships in the wheel. Reject unknown fields to expose accidental interface drift early. A future incompatible change gets a new schema version.

Project state is explicit input, not process-global memory. A host can route many projects concurrently by passing independent profiles, context and task identities; no hosted scheduling or durable queue is implemented. Telemetry groups task outcomes by run, project, task and strategy, never by task name alone.

Runtime-specific model IDs and reasoning settings are adapter configuration. The manual adapter reports requested tier separately from effective tier; it never pretends the host changed models. A future adapter must publish controls, usage units, permission needs and validator behavior before execution.

No database, event bus, vector store, model-training pipeline, or distributed agent platform is needed to test the initial hypothesis. Add one only when measured trials reveal a requirement the current contracts cannot satisfy. [DECISIONS.md](DECISIONS.md) records alternatives and trade-offs.
