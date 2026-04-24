from pathlib import Path

from calamum.api import (
    generate_report,
    list_reports,
    register_project_context,
    resolve_project_context,
    run_test_definition,
)


def test_api_facade_round_trip(tmp_path, monkeypatch):
    project_root = tmp_path / "api-project"
    config_root = tmp_path / "config"
    project_root.mkdir(parents=True, exist_ok=True)
    (project_root / "src").mkdir()
    (project_root / "tests").mkdir()
    (project_root / "catalog").mkdir()
    (project_root / "pyproject.toml").write_text("[project]\nname='api-project'\nversion='0.0.0'\n", encoding="utf-8")
    monkeypatch.setenv("CALAMUM_CONFIG_ROOT", str(config_root))

    packet = register_project_context(
        project_id="api-project",
        root=project_root,
        name="API Project",
        aliases=["api"],
        required_markers=["pyproject.toml"],
        required_paths=["src", "tests", "catalog"],
        write_local_override=True,
        set_current=True,
    )
    assert packet["decision"] == "go"

    resolved = resolve_project_context(project="api", cwd=project_root)
    assert resolved is not None

    definition = {
        "id": "api-smoke",
        "title": "API smoke",
        "summary": "Exercise the public Python facade.",
        "status": "active",
        "category": "integration",
        "selector_policy": "exact-name-only",
        "profiles": ["default"],
        "tags": ["api"],
        "policy_flags": [],
        "evidence_requirements": [],
        "default_lanes": ["pytest"],
        "lanes": {
            "pytest": [{"id": "pytest", "title": "Pytest", "command": ["{python}", "-c", "print('api ok')"]}],
            "sandbox_test": [],
            "empirical_test": [],
        },
    }
    run_packet = run_test_definition(definition, runs_root=resolved.runs_root, project_context=resolved)
    assert run_packet["decision"] == "go"

    report_packet = generate_report(
        scope="project",
        runs_root=resolved.runs_root,
        reports_root=resolved.reports_root,
        project_context=resolved,
    )
    assert report_packet["decision"] == "go"

    rows = list_reports(Path(report_packet["artifacts"]["report_index"]).parent.parent)
    assert rows
