# Contributing

Keep changes small and evidence-backed. Add a behavior test for a meaningful regression or contract change, and explain its expected effect on correctness and total task cost. Do not add a provider client or background service without a concrete evaluation need.

```sh
python -m pip install -e '.[dev]'
python -m pytest
python -m ruff check .
engineering-cascade eval --root . --mode routing
engineering-cascade eval --root . --mode fixtures --execute
python -m build
```

Update the relevant docs and versioned schema alongside public behavior. Preserve unknown measurements, failed-attempt accounting, project isolation, and permission boundaries. New runtime dependencies need a maintenance/benefit explanation and a license review.

Use synthetic inputs in tests and public examples. Never submit secrets, private project profiles, proprietary prompts, or unreviewed traces. Avoid changing routing defaults based on fixture outcomes; collect held-out measured trials first.

CI verifies the Python core and bundled offline evaluations. Provider adapters will need separate opt-in integration tests. The repository is alpha; contract changes require a schema version change when backward compatibility is broken.
