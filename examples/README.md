# Worked synthetic handoff

These files describe a fictional calculator. `project.json` uses the current directory as a path-confinement root so the packet builder can be tried in a checkout. The named calculator files are illustrative; this example does not execute them. Use the fixture suite for executable examples.

```sh
mkdir -p .cascade
engineering-cascade route examples/task.json --policy examples/policy.json > .cascade/decision.json
engineering-cascade context examples/context.json --project examples/project.json --budget 2000 > .cascade/context.json
engineering-cascade packet examples/task.json examples/project.json .cascade/decision.json --context .cascade/context.json --details examples/packet-details.json > .cascade/packet.json
engineering-cascade packet examples/task.json examples/project.json .cascade/decision.json --context .cascade/context.json --details examples/packet-details.json --markdown
engineering-cascade dispatch .cascade/packet.json --decision .cascade/decision.json
engineering-cascade skills discover skills
```

The last dispatch prepares a request with `effective_tier: null` and no usage. A host agent or human decides how to execute within existing permissions. The CLI does not launch a model or run the example validator. Replace the synthetic profile and revision with repository-grounded local state before real use.
