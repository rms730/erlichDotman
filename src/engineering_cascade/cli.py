"""Read-only JSON control plane, with explicitly opted-in bundled fixture execution."""

import argparse
import json
import sys
from pathlib import Path

from .contracts import load_json, validate
from .routing import route


def _parser():
    parser = argparse.ArgumentParser(prog="engineering-cascade")
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("validate", help="validate a public contract")
    check.add_argument("input")
    check.add_argument("--kind", required=True)
    routing = sub.add_parser("route", help="recommend tier and context, without execution")
    routing.add_argument("task")
    routing.add_argument("--policy", required=True)
    routing.add_argument("--evidence")
    routing.add_argument("--workflow", help="optional bound workflow sidecar")
    workflow = sub.add_parser("workflow-check", help="check supplied workflow facts only")
    workflow.add_argument("input")
    context = sub.add_parser("context", help="select project and revision scoped excerpts")
    context.add_argument("items")
    context.add_argument("--project", required=True)
    context.add_argument("--budget", required=True, type=int)
    packet = sub.add_parser("packet", help="build a bound implementation packet")
    for name in ("task", "project", "decision"):
        packet.add_argument(name)
    packet.add_argument("--context", required=True)
    packet.add_argument("--details", required=True)
    packet.add_argument("--markdown", action="store_true")
    dispatch = sub.add_parser("dispatch", help="prepare a request for a host agent")
    dispatch.add_argument("packet")
    dispatch.add_argument("--decision", required=True)
    dispatch.add_argument("--workflow", help="optional worker-scoped workflow sidecar")
    dispatch.add_argument("--policy", help="active policy; required for a workflow retry")
    skills = sub.add_parser("skills", help="discover metadata or select compatible skills")
    skill_sub = skills.add_subparsers(dest="skill_command", required=True)
    discover = skill_sub.add_parser("discover")
    discover.add_argument("roots", nargs="+")
    discover.add_argument("--trust", default="repository-local",
                          choices=["trusted", "repository-local", "third-party", "untrusted"])
    select = skill_sub.add_parser("select")
    select.add_argument("catalog")
    select.add_argument("--capability", action="append", default=[])
    select.add_argument("--budget", type=int, required=True)
    select.add_argument("--allow-trust", action="append", default=None)
    for name in ("summary", "recommend"):
        telemetry = sub.add_parser(name, help="aggregate JSONL telemetry without policy mutation")
        telemetry.add_argument("records")
        if name == "recommend":
            telemetry.add_argument("--minimum-samples", type=int, default=20)
            telemetry.add_argument("--success-threshold", type=float, default=0.95)
    evaluation = sub.add_parser("eval", help="run repository policy or bundled fixture checks")
    evaluation.add_argument("--root", default=".")
    evaluation.add_argument("--mode", choices=["routing", "fixtures"], default="routing")
    evaluation.add_argument("--execute", action="store_true",
                            help="authorize bundled Python fixture validators in temp directories")
    return parser


def _records(path):
    """Bound telemetry input; reject malformed lines rather than silently dropping them."""
    with Path(path).open("rb") as stream:
        lines = stream.read(16 * 1024 * 1024 + 1)
    if len(lines) > 16 * 1024 * 1024:
        raise ValueError("Telemetry exceeds byte budget")
    # Reuse strict JSON parsing for each line without any external side effects.
    from .contracts import _finite_float, _invalid_number, _unique_object
    records = []
    for number, line in enumerate(lines.decode("utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line, object_pairs_hook=_unique_object,
                                      parse_constant=_invalid_number, parse_float=_finite_float))
        except (ValueError, RecursionError) as exc:
            raise ValueError(f"Invalid telemetry JSON at line {number}") from exc
    return records


def _run(args):
    if args.command == "validate":
        validate(load_json(args.input), args.kind)
        return {"valid": True, "kind": args.kind}, 0
    if args.command == "route":
        return route(load_json(args.task), load_json(args.policy),
                     load_json(args.evidence) if args.evidence else None,
                     load_json(args.workflow) if args.workflow else None), 0
    if args.command == "workflow-check":
        from .workflow import check_workflow
        check_workflow(load_json(args.input))
        return {"valid": True, "scope": "supplied_workflow_facts_only"}, 0
    if args.command == "context":
        from .context import select_context
        project = load_json(args.project)
        validate(project, "project")
        return select_context(load_json(args.items), project["project_id"], project["revision"],
                              args.budget), 0
    if args.command == "packet":
        from .handoff import build_packet, render_packet
        result = build_packet(load_json(args.task), load_json(args.project),
                              load_json(args.decision), load_json(args.context),
                              **load_json(args.details))
        return render_packet(result) if args.markdown else result, 0
    if args.command == "dispatch":
        from .adapters import ManualAdapter
        return ManualAdapter().prepare(load_json(args.packet), load_json(args.decision),
                                       load_json(args.workflow) if args.workflow else None,
                                       load_json(args.policy) if args.policy else None), 0
    if args.command == "skills":
        from .skills import discover_skills, select_skills
        if args.skill_command == "discover":
            return discover_skills([{"path": root, "trust": args.trust}
                                    for root in args.roots]), 0
        return select_skills(args.capability, load_json(args.catalog), args.budget,
                             args.allow_trust or ["trusted", "repository-local"]), 0
    if args.command in {"summary", "recommend"}:
        from .telemetry import recommend, summarize
        records = _records(args.records)
        if args.command == "summary":
            return summarize(records), 0
        return recommend(records, args.minimum_samples, args.success_threshold), 0
    if args.command == "eval":
        from .evaluation import run_suite
        report = run_suite(Path(args.root), mode=args.mode, execute=args.execute)
        failure_fields = ("checks_failed", "contract_failures", "harness_errors",
                          "execution_failures")
        failed = any(report.get(key, 0) for key in failure_fields)
        return report, 1 if failed else 0
    raise ValueError("Unsupported command")


def main(argv=None):
    args = _parser().parse_args(argv)
    try:
        result, status = _run(args)
        if isinstance(result, str):
            print(result)
        else:
            print(json.dumps(result, indent=2, allow_nan=False))
        return status
    except (ValueError, OSError, TypeError, UnicodeError) as exc:
        # Contract errors exclude document values; file errors may expose caller-supplied paths.
        print(f"engineering-cascade: {exc}", file=sys.stderr)
        return 2
