# Security model

Efficiency cannot justify expanding authority. The core distinguishes trusted operator inputs, repository-local content, third-party resources and untrusted outputs. These are provenance labels, not execution privileges.

| Threat | Boundary or procedure | Remaining limitation |
| --- | --- | --- |
| Project mixing or stale assumptions | Project/revision binding; required context cannot be dropped | Caller must supply a fresh snapshot including dirty edits |
| Skill injection or supply-chain code | Metadata-only discovery; operator provenance; no auto-install | Host must review selected bodies and dependencies |
| Repository/tool prompt injection | Carry provenance; treat content as data | No automatic semantic injection detector |
| Shell interpretation | Validators use argv, never `shell=True` | Python/tests themselves can execute arbitrary code |
| Hanging or noisy validators | Timeout, bounded output and failure status | External OS sandbox needed for hostile code |
| Credentials in public artifacts | Ignored private state; synthetic fixtures; payload review | `.gitignore` is not a secret scanner or authorization system |
| Destructive migrations/publication | Decision prepares work but does not grant permission | Host must enforce its approval and privilege model |
| Dependency compromise | One mature runtime dependency; explicit dev dependencies; license review | Installation still requires trusted package sources |

Bundled fixture execution is opt-in and uses fresh temporary directories. It does not run arbitrary task shell strings. The generic validator API is available to explicitly authorized callers; it is not a security sandbox. Do not use it to execute untrusted repository code on a privileged host.

Keep credentials in the runtime's secret store, never in task packets or telemetry. Raw traces may contain private code and paths; default local storage is ignored. Audit tracked paths and content before pushing, including all commit history. CI must not receive production credentials.

JSON loads reject duplicate keys, non-finite numbers, oversized files and nesting beyond 64 levels; contracts reject unknown fields. The explicit nesting limit is independent of Python's parser recursion behavior. Remote schema resolution and skill installation are absent. Adapters must declare controls and permissions and preserve requested/effective model distinctions. Unknown controls cannot be simulated as successful execution.
