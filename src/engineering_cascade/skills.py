"""Discover metadata only and choose compatible, budgeted skill sets.

Trust comes from operator-supplied roots, never a manifest's self-description.
This module does not read skill bodies, install packages, or confer permission.
Token estimates are metadata heuristics and cannot measure inference savings.
"""

import os
from copy import deepcopy
from pathlib import Path

from .context import _check_budget
from .contracts import load_json, validate

_TRUST_LABELS = {"trusted", "repository-local", "third-party", "untrusted"}
_MAX_CANDIDATES = 20


def discover_skills(roots):
    """Read only skill.json sidecars beneath operator-asserted trusted roots.

    A root is a path (repository-local provenance) or {path, trust}. Escaping
    directory/file symlinks and duplicate skill names or sidecars fail closed.
    """
    if not isinstance(roots, list):
        raise ValueError("skill roots must be a list")
    catalog = []
    names, sources = set(), set()
    for descriptor in roots:
        if isinstance(descriptor, dict):
            if set(descriptor) != {"path", "trust"}:
                raise ValueError("root descriptor must contain only path and trust")
            path, trust = descriptor["path"], descriptor["trust"]
        else:
            path, trust = descriptor, "repository-local"
        if not isinstance(trust, str) or trust not in _TRUST_LABELS:
            raise ValueError("invalid operator root trust")
        try:
            root = Path(path).expanduser().resolve(strict=True)
            if not root.is_dir():
                raise ValueError("skill root must be a directory")
            for directory, subdirectories, files in os.walk(root, followlinks=False):
                for name in sorted(subdirectories):
                    child = Path(directory) / name
                    if child.is_symlink() and not child.resolve().is_relative_to(root):
                        raise ValueError("skill directory symlink resolves outside root")
                if "skill.json" not in files:
                    continue
                source = (Path(directory) / "skill.json").resolve(strict=True)
                if not source.is_relative_to(root):
                    raise ValueError("skill sidecar resolves outside root")
                if source in sources:
                    raise ValueError("duplicate skill sidecar")
                manifest = load_json(source)
                validate(manifest, "skill")
                if manifest["name"] in names:
                    raise ValueError(f"duplicate skill name: {manifest['name']}")
                result = deepcopy(manifest)
                result["estimated_tokens"] = int(result["estimated_tokens"])
                result["trust"], result["source"] = trust, str(source)
                catalog.append(result)
                names.add(manifest["name"])
                sources.add(source)
        except (OSError, RuntimeError, TypeError) as error:
            raise ValueError(f"cannot discover skill metadata: {error}") from error
    return sorted(catalog, key=lambda entry: (entry["name"], entry["source"]))


def select_skills(required_capabilities, catalog, budget_tokens, allowed_trust):
    """Choose minimum estimated tokens among sets with maximum useful coverage.

    Dependencies count against the same budget; conflicts are bidirectional.
    Exhaustive search over at most 20 relevant skills avoids greedy dead ends.
    This is a metadata recommendation, never authorization to execute a skill.
    """
    _check_budget(budget_tokens)
    if (not isinstance(required_capabilities, list) or
            any(not isinstance(value, str) or not value for value in required_capabilities)):
        raise ValueError("required capabilities must be a list of nonempty strings")
    if (not isinstance(allowed_trust, (list, set, tuple)) or
            any(not isinstance(value, str) or value not in _TRUST_LABELS for value in allowed_trust)):
        raise ValueError("allowed trust must contain recognized provenance labels")
    if not isinstance(catalog, list):
        raise ValueError("skill catalog must be a list")
    by_name = {}
    for entry in catalog:
        validate(entry, "skill")
        if entry["name"] in by_name:
            raise ValueError(f"duplicate skill name: {entry['name']}")
        by_name[entry["name"]] = {**deepcopy(entry), "estimated_tokens": int(entry["estimated_tokens"])}
    required = set(required_capabilities)
    rejected = {}
    allowed = set(allowed_trust)
    closures = {}
    for name in sorted(by_name):
        closure, pending = set(), [name]
        failure = None
        while pending:
            current = pending.pop()
            if current in closure:
                continue
            if current not in by_name:
                failure = f"missing dependency: {current}"
                break
            if by_name[current]["trust"] not in allowed:
                failure = ("trust not allowed" if current == name else
                           f"dependency trust not allowed: {current}")
                break
            closure.add(current)
            pending.extend(sorted(by_name[current]["requires"], reverse=True))
        if failure is None and any(set(by_name[current]["conflicts"]) & closure for current in closure):
            failure = "dependency closure contains conflicting skills"
        if failure is not None:
            rejected[name] = failure
        else:
            closures[name] = closure
    candidates = sorted(name for name in closures if set(by_name[name]["capabilities"]) & required)
    relevant = set().union(*(closures[name] for name in candidates)) if candidates else set()
    if len(relevant) > _MAX_CANDIDATES:
        raise ValueError(f"skill selection supports at most {_MAX_CANDIDATES} relevant skills")
    best_names, best_score = set(), (0, 0, 0, ())
    visited = set()

    def search(index, selected):
        nonlocal best_names, best_score
        state = (index, tuple(sorted(selected)))
        if state in visited:
            return
        visited.add(state)
        tokens = sum(by_name[name]["estimated_tokens"] for name in selected)
        if tokens > budget_tokens:
            return
        covered = set().union(*(set(by_name[name]["capabilities"]) for name in selected)) if selected else set()
        score = (-len(covered & required), tokens, len(selected), tuple(sorted(selected)))
        if score < best_score:
            best_names, best_score = selected, score
        if index == len(candidates):
            return
        search(index + 1, selected)
        expanded = selected | closures[candidates[index]]
        if not any(set(by_name[name]["conflicts"]) & expanded for name in expanded):
            search(index + 1, expanded)

    search(0, set())
    coverage = set().union(*(set(by_name[name]["capabilities"]) for name in best_names)) if best_names else set()
    for name in sorted(by_name):
        if name in best_names or name in rejected:
            continue
        if not set(by_name[name]["capabilities"]) & required:
            rejected[name] = "not needed for required capabilities"
        elif any(set(by_name[selected]["conflicts"]) & (best_names | closures[name])
                 for selected in best_names | closures[name]):
            rejected[name] = "conflicts with selected skill"
        elif sum(by_name[dependency]["estimated_tokens"] for dependency in closures[name]) > budget_tokens:
            rejected[name] = "dependency closure exceeds budget"
        else:
            rejected[name] = "not in the minimum-budget useful set"
    return {
        "selected": [deepcopy(by_name[name]) for name in sorted(best_names)],
        "missing_capabilities": sorted(required - coverage),
        "estimated_tokens": sum(by_name[name]["estimated_tokens"] for name in best_names),
        "rejected": dict(sorted(rejected.items())),
    }
