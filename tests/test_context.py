"""Project-scoped context must remain complete, fresh, and isolated."""

import json

import pytest

from engineering_cascade.context import load_project, read_project_file, select_context


def item(item_id="facts", *, project="demo", revision="r1", tokens=3, required=True):
    return {
        "id": item_id,
        "project_id": project,
        "revision": revision,
        "content": "Required engineering facts.",
        "estimated_tokens": tokens,
        "required": required,
        "trust": "repository-local",
    }


def profile(repository):
    return {
        "schema_version": 1,
        "project_id": "demo",
        "repository": str(repository),
        "branch": "main",
        "revision": "r1",
        "stack": ["Python"],
        "architecture": "A small library.",
        "conventions": [],
        "objectives": [],
        "constraints": [],
        "decisions": [],
        "validation_commands": [["python", "-m", "pytest"]],
        "skill_roots": [],
        "instructions": [],
    }


def test_required_context_precedes_optional_and_selection_is_deterministic():
    inputs = [item("z", tokens=6, required=False), item("b", tokens=2),
              item("a", tokens=2, required=False), item("c", tokens=2, required=False)]
    selected = select_context(inputs, "demo", "r1", 6)
    assert [entry["id"] for entry in selected["items"]] == ["b", "a", "c"]
    assert selected["estimated_tokens"] == 6
    assert selected["omitted"] == ["z"]
    assert select_context(list(reversed(inputs)), "demo", "r1", 6) == selected
    selected["items"][0]["content"] = "changed"
    assert inputs[1]["content"] == "Required engineering facts."


@pytest.mark.parametrize("inputs", [
    [item(), item("other", project="foreign", required=False)],
    [item(), item("old", revision="r0", required=False)],
    [item(), item()],
])
def test_rejects_mixed_stale_or_duplicate_context_even_if_optional(inputs):
    with pytest.raises(ValueError):
        select_context(inputs, "demo", "r1", 0)


@pytest.mark.parametrize("budget", [-1, True, 1.5, "5", None])
def test_invalid_budget_is_rejected(budget):
    with pytest.raises(ValueError):
        select_context([], "demo", "r1", budget)


def test_required_context_cannot_be_truncated():
    with pytest.raises(ValueError, match="required"):
        select_context([item(tokens=4)], "demo", "r1", 3)
    assert select_context([], "demo", "r1", 0)["estimated_tokens"] == 0


def test_load_project_checks_canonical_repository_and_revision(tmp_path):
    repository = tmp_path / "repo"
    repository.mkdir()
    path = repository / "project.json"
    path.write_text(json.dumps(profile(repository)))
    alias = tmp_path / "alias"
    alias.symlink_to(repository, target_is_directory=True)
    assert load_project("project.json", alias, "r1")["project_id"] == "demo"
    with pytest.raises(ValueError, match="revision"):
        load_project(path, repository, "r2")
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    path.write_text(json.dumps(profile(foreign)))
    with pytest.raises(ValueError, match="repository"):
        load_project(path, repository, "r1")


def test_project_profile_and_file_reads_reject_escape_and_symlinks(tmp_path):
    repository = tmp_path / "repo"
    repository.mkdir()
    foreign = tmp_path / "foreign.json"
    foreign.write_text(json.dumps(profile(repository)))
    link = repository / "profile.json"
    link.symlink_to(foreign)
    for path in (foreign, "../foreign.json", link):
        with pytest.raises(ValueError, match="outside"):
            load_project(path, repository, "r1")
    with pytest.raises(ValueError, match="outside"):
        read_project_file(repository, "../foreign.json")
    local = repository / "facts.txt"
    local.write_text("facts")
    assert read_project_file(repository, "facts.txt") == "facts"


def test_context_rejects_invalid_identity_and_schema():
    with pytest.raises(ValueError):
        select_context([], "", "r1", 0)
    with pytest.raises(ValueError):
        select_context([], "demo", "", 0)
    invalid = item()
    invalid["unexpected"] = "data"
    with pytest.raises(ValueError):
        select_context([invalid], "demo", "r1", 5)


def test_schema_integer_estimates_are_normalized_without_mutating_input():
    inputs = [item(tokens=2.0)]
    result = select_context(inputs, "demo", "r1", 2)
    assert type(result["estimated_tokens"]) is int
    assert type(result["items"][0]["estimated_tokens"]) is int
    assert type(inputs[0]["estimated_tokens"]) is float
