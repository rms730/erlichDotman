"""Metadata selection respects operator provenance and compatibility."""

import json

import pytest

from engineering_cascade.skills import discover_skills, select_skills


def skill(name, capabilities, *, tokens=2, trust="repository-local", requires=(), conflicts=()):
    return {
        "name": name, "capabilities": list(capabilities), "estimated_tokens": tokens,
        "trust": trust, "requires": list(requires), "conflicts": list(conflicts),
    }


def write_skill(root, metadata):
    folder = root / metadata["name"]
    folder.mkdir(parents=True)
    (folder / "skill.json").write_text(json.dumps(metadata))
    (folder / "SKILL.md").write_text("NEVER LOAD THIS BODY")
    return folder


def test_discovery_is_sorted_reads_only_sidecars_and_overrides_self_claimed_trust(tmp_path):
    write_skill(tmp_path, skill("z", ["testing"], trust="trusted"))
    write_skill(tmp_path, skill("a", ["coding"]))
    (tmp_path / "a" / "SKILL.md").unlink()
    (tmp_path / "a" / "SKILL.md").mkdir()
    catalog = discover_skills([tmp_path])
    assert [entry["name"] for entry in catalog] == ["a", "z"]
    assert all(entry["trust"] == "repository-local" for entry in catalog)
    assert all(entry["source"].endswith("skill.json") for entry in catalog)
    third_party = discover_skills([{"path": tmp_path, "trust": "third-party"}])
    assert all(entry["trust"] == "third-party" for entry in third_party)


def test_discovery_rejects_escape_duplicate_and_bad_sidecars(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    folder = write_skill(outside, skill("foreign", ["coding"]))
    (root / "foreign").symlink_to(folder, target_is_directory=True)
    with pytest.raises(ValueError, match="outside"):
        discover_skills([root])
    (root / "foreign").unlink()
    local = write_skill(root, skill("local", ["coding"]))
    (local / "skill.json").unlink()
    (local / "skill.json").symlink_to(folder / "skill.json")
    with pytest.raises(ValueError, match="outside"):
        discover_skills([root])
    (local / "skill.json").unlink()
    (local / "skill.json").write_text("{}")
    with pytest.raises(ValueError):
        discover_skills([root])
    (local / "skill.json").write_text(json.dumps(skill("local", ["coding"])))
    with pytest.raises(ValueError, match="duplicate"):
        discover_skills([root, root])


def test_discovery_rejects_duplicate_names_across_roots_and_invalid_root_trust(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    write_skill(first, skill("same", ["coding"]))
    write_skill(second, skill("same", ["testing"]))
    with pytest.raises(ValueError, match="duplicate"):
        discover_skills([first, second])
    with pytest.raises(ValueError, match="trust"):
        discover_skills([{"path": first, "trust": "self-authorized"}])


def test_selection_finds_cheapest_complete_set_instead_of_greedy_dead_end():
    catalog = [skill("a", ["code"], tokens=1, conflicts=["test"]),
               skill("b", ["code"], tokens=2), skill("test", ["test"], tokens=2)]
    result = select_skills(["code", "test"], catalog, 4, ["repository-local"])
    assert [entry["name"] for entry in result["selected"]] == ["b", "test"]
    assert result["missing_capabilities"] == []
    assert result["estimated_tokens"] == 4
    assert select_skills(["test", "code"], list(reversed(catalog)), 4, ["repository-local"]) == result


def test_selection_includes_dependencies_and_honors_one_sided_conflicts():
    catalog = [skill("code", ["code"], requires=["base"]), skill("base", ["base"], tokens=1),
               skill("test", ["test"], tokens=4, conflicts=["base"])]
    result = select_skills(["code", "test"], catalog, 5, ["repository-local"])
    assert [entry["name"] for entry in result["selected"]] == ["base", "code"]
    assert result["missing_capabilities"] == ["test"]
    assert result["rejected"]["test"] == "conflicts with selected skill"


def test_selection_rejects_disallowed_trust_and_broken_dependencies_without_permissions():
    catalog = [skill("unsafe", ["code"], trust="third-party"),
               skill("broken", ["code"], requires=["missing"]),
               skill("dependent", ["test"], requires=["unsafe"])]
    result = select_skills(["code", "test"], catalog, 20, ["repository-local"])
    assert result["selected"] == []
    assert result["missing_capabilities"] == ["code", "test"]
    assert "trust" in result["rejected"]["unsafe"]
    assert "dependency" in result["rejected"]["broken"]
    assert "dependency" in result["rejected"]["dependent"]
    assert "permission" not in result


def test_selection_respects_budget_and_does_not_add_irrelevant_skills():
    catalog = [skill("both", ["code", "test"], tokens=3),
               skill("code", ["code"], tokens=1), skill("test", ["test"], tokens=1),
               skill("irrelevant", ["other"], tokens=1)]
    result = select_skills(["code", "test"], catalog, 2, ["repository-local"])
    assert [entry["name"] for entry in result["selected"]] == ["code", "test"]
    assert result["estimated_tokens"] == 2
    assert select_skills([], catalog, 0, ["repository-local"])["selected"] == []
    assert select_skills(["code"], catalog, 0, ["repository-local"])["missing_capabilities"] == ["code"]


@pytest.mark.parametrize("budget", [-1, True, 1.2, None])
def test_selection_rejects_invalid_budget(budget):
    with pytest.raises(ValueError):
        select_skills([], [], budget, [])


def test_selection_rejects_duplicate_catalog_names_and_invalid_inputs():
    with pytest.raises(ValueError, match="duplicate"):
        select_skills(["code"], [skill("same", ["code"])] * 2, 5, ["repository-local"])
    with pytest.raises(ValueError):
        select_skills([""], [], 5, [])
    with pytest.raises(ValueError):
        select_skills([], [], 5, ["self-authorized"])


def test_dependency_cycles_terminate_and_conflicting_dependency_closures_fail():
    catalog = [skill("code", ["code"], requires=["base"]),
               skill("base", ["base"], requires=["code"])]
    result = select_skills(["code"], catalog, 4, ["repository-local"])
    assert [entry["name"] for entry in result["selected"]] == ["base", "code"]
    catalog[1]["conflicts"] = ["code"]
    result = select_skills(["code"], catalog, 4, ["repository-local"])
    assert result["selected"] == []
    assert "conflicting" in result["rejected"]["code"]


def test_large_irrelevant_catalog_is_allowed_but_relevant_search_is_bounded():
    catalog = [skill(f"unrelated-{number}", ["unrelated"]) for number in range(25)]
    catalog.append(skill("code", ["code"]))
    assert len(select_skills(["code"], catalog, 2, ["repository-local"])["selected"]) == 1
    with pytest.raises(ValueError, match="20 relevant"):
        select_skills(["unrelated"], catalog, 100, ["repository-local"])


def test_discovered_provenance_cannot_be_replaced_by_sidecar_source(tmp_path):
    metadata = skill("code", ["code"], trust="trusted")
    metadata["source"] = "operator-approved"
    folder = write_skill(tmp_path, metadata)
    result = discover_skills([{"path": tmp_path, "trust": "third-party"}])
    assert result[0]["source"] == str((folder / "skill.json").resolve())
    assert result[0]["trust"] == "third-party"
    (folder / "skill.json").write_text('{"name":"one","name":"two"}')
    with pytest.raises(ValueError):
        discover_skills([tmp_path])


def test_schema_integer_skill_estimates_are_normalized(tmp_path):
    metadata = skill("code", ["code"], tokens=2.0)
    write_skill(tmp_path, metadata)
    discovered = discover_skills([tmp_path])
    assert type(discovered[0]["estimated_tokens"]) is int
    result = select_skills(["code"], [metadata], 2, ["repository-local"])
    assert type(result["estimated_tokens"]) is int
    assert type(result["selected"][0]["estimated_tokens"]) is int
    assert type(metadata["estimated_tokens"]) is float
