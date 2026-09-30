# Skill orchestration

Load catalog metadata before loading skill instructions. This prevents five unused methodologies from consuming the implementation agent's context and allows compatibility checks before composing them.

The generic Agent Skills format describes `SKILL.md`, progressive disclosure and supporting resources. ErlichDotman adds an optional `skill.json` sidecar for deterministic capability/cost/conflict selection. Existing skills without sidecars still work through host-provided catalog metadata; this version does not claim to discover every installed format automatically.

```json
{
  "name": "test-boundaries",
  "capabilities": ["testing"],
  "estimated_tokens": 700,
  "trust": "repository-local",
  "conflicts": [],
  "requires": []
}
```

Discovery accepts operator-provided roots and reads only sidecars. Root provenance overrides a sidecar's self-reported trust. Third-party text cannot label itself trusted. Metadata selection minimizes the useful compatible set under a budget, includes dependencies, rejects conflicts, and reports missing capabilities. Labels describe origin; they do not authorize execution.

Only selected skill bodies are loaded by the host. Estimates must include their expected references; expand only when the task actually needs a reference. Declared conflicts are a first check, not proof instructions are semantically compatible. The host must compare permission requirements, test methods and scope before composing unfamiliar skills.

For missing capabilities: report the gap, inspect an operator-approved source, review origin/license/code and instruction compatibility, recommend a candidate, and obtain installation authorization when needed. Never install a suggested skill as a side effect of discovery. Record its version/provenance and measured outcome after authorized use.
