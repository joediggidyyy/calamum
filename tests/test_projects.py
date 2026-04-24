from pathlib import Path

from calamum.projects import register_project, resolve_project, validate_project


def create_project_tree(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "src").mkdir()
    (root / "tests").mkdir()
    (root / "pyproject.toml").write_text("[project]\nname = 'demo'\nversion = '0.0.0'\n", encoding="utf-8")


def test_register_and_resolve_project_round_trip(tmp_path, monkeypatch):
    project_root = tmp_path / "demo-project"
    config_root = tmp_path / "config"
    create_project_tree(project_root)
    monkeypatch.setenv("CALAMUM_CONFIG_ROOT", str(config_root))

    packet = register_project(
        project_id="demo-project",
        root=project_root,
        name="Demo Project",
        aliases=["demo"],
        shape_kind="python",
        catalog_root="catalog",
        runs_root=".calamum/generated/runs",
        reports_root=".calamum/generated/reports",
        working_dir=".",
        required_markers=["pyproject.toml"],
        required_paths=["src", "tests", "catalog"],
        path_aliases={"source_root": "src", "tests_root": "tests"},
        write_local_override=True,
        set_current=True,
    )

    assert packet["decision"] == "go"

    resolved = resolve_project(project="demo", cwd=project_root, config_root=config_root)
    assert resolved is not None
    assert resolved.project_id == "demo-project"
    assert resolved.catalog_root == project_root / "catalog"
    assert resolved.runs_root == project_root / ".calamum" / "generated" / "runs"
    assert resolved.reports_root == project_root / ".calamum" / "generated" / "reports"
    assert resolved.token_map()["tests_root"] == str(project_root / "tests")
    assert (project_root / "catalog" / "test_definitions.json").exists()
    assert (project_root / ".calamum" / "generated" / ".gitignore").exists()

    current = resolve_project(cwd=project_root, config_root=config_root)
    assert current is not None
    assert current.project_id == "demo-project"

    validation = validate_project(resolved)
    assert validation["decision"] == "go"
    assert validation["missing_markers"] == []
    assert validation["missing_paths"] == []
