"""Select heuristic context budgets and read project-bound files safely.

``estimated_tokens`` are caller-provided planning heuristics, never metered usage.
Path confinement protects against accidental project mixing; it is not an OS sandbox.
"""

import re
from copy import deepcopy
from pathlib import Path

from .contracts import load_json, validate

_IDENTIFIER = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_.-]{0,79}\Z")


def _check_budget(budget_tokens):
    if type(budget_tokens) is not int or budget_tokens < 0:
        raise ValueError("budget_tokens must be a nonnegative integer")


def _repository_file(repository, path):
    """Resolve a file path while retaining one canonical repository boundary."""
    try:
        root = Path(repository).expanduser().resolve(strict=True)
        if not root.is_dir():
            raise ValueError("repository must be a directory")
        candidate = Path(path).expanduser()
        if not candidate.is_absolute():
            candidate = root / candidate
        resolved = candidate.resolve()
        if not resolved.is_relative_to(root):
            raise ValueError("path resolves outside the repository")
        return root, resolved
    except (OSError, RuntimeError, TypeError) as error:
        raise ValueError(f"invalid repository path: {error}") from error


def read_project_file(repository, path):
    """Read UTF-8 text only after resolving containment, including symlinks."""
    _, resolved = _repository_file(repository, path)
    try:
        return resolved.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ValueError(f"cannot read project file: {error}") from error


def load_project(path, repository, revision):
    """Load a profile whose canonical repository and revision match the caller."""
    if not isinstance(revision, str) or not revision:
        raise ValueError("revision must be a nonempty string")
    root, resolved = _repository_file(repository, path)
    project = load_json(resolved)
    validate(project, "project")
    try:
        bound_root = Path(project["repository"]).expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise ValueError(f"invalid profile repository: {error}") from error
    if bound_root != root:
        raise ValueError("profile repository does not match the canonical repository")
    if project["revision"] != revision:
        raise ValueError("profile revision is stale")
    result = deepcopy(project)
    result["repository"] = str(root)
    return result


def select_context(items, project_id, revision, budget_tokens):
    """Keep required facts, then optional facts by ID within a heuristic budget.

    Every input is checked even when it would be omitted. A required item's
    content is never shortened to fit. Returned dictionaries do not alias inputs.
    """
    _check_budget(budget_tokens)
    if not isinstance(project_id, str) or not _IDENTIFIER.fullmatch(project_id):
        raise ValueError("project_id must be a valid project identifier")
    if not isinstance(revision, str) or not revision:
        raise ValueError("revision must be a nonempty string")
    if not isinstance(items, list):
        raise ValueError("context items must be a list")
    seen = set()
    normalized = []
    for item in items:
        validate(item, "context_item")
        if item["project_id"] != project_id:
            raise ValueError("context item belongs to another project")
        if item["revision"] != revision:
            raise ValueError("context item revision is stale")
        if item["id"] in seen:
            raise ValueError(f"duplicate context id: {item['id']}")
        seen.add(item["id"])
        normalized.append({**item, "estimated_tokens": int(item["estimated_tokens"])})
    required = sorted((item for item in normalized if item["required"]), key=lambda item: item["id"])
    optional = sorted((item for item in normalized if not item["required"]), key=lambda item: item["id"])
    estimated = sum(item["estimated_tokens"] for item in required)
    if estimated > budget_tokens:
        raise ValueError("required context exceeds the heuristic token budget")
    selected = required[:]
    omitted = []
    for item in optional:
        if estimated + item["estimated_tokens"] <= budget_tokens:
            selected.append(item)
            estimated += item["estimated_tokens"]
        else:
            omitted.append(item["id"])
    return {"items": deepcopy(selected), "estimated_tokens": estimated, "omitted": omitted}
