import json
import sys
from pathlib import Path

import pytest

from calamum.cli import EXIT_OK, main


def test_list_uses_seed_catalog(capsys):
    project_root = Path(__file__).resolve().parents[1]
    catalog_root = project_root / "catalog"

    exit_code = main(["test", "list", "--catalog-root", str(catalog_root), "--json"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    ids = {item["id"] for item in payload["definitions"]}

    assert exit_code == EXIT_OK
    assert payload["decision"] == "go"
    assert payload["count"] >= 2
    assert "seed-cli-smoke" in ids
    assert "seed-adversarial-smoke" in ids


def test_root_help_is_grouped(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["-h"])

    captured = capsys.readouterr()

    assert exc_info.value.code == 0
    assert "[Commands]" in captured.out
    assert "[Examples]" in captured.out
    assert "calamum project current" in captured.out
    assert "monitor" in captured.out
    assert "project" in captured.out
    assert "--version" in captured.out


def test_version_flag_reports_version(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])

    captured = capsys.readouterr()

    assert exc_info.value.code == 0
    assert captured.out.strip() == "calamum 0.3.0"


@pytest.mark.parametrize(
    ("argv", "expected_heading"),
    [
        (["test", "-h"], "[Definitions]"),
        (["test", "runs", "-h"], "[Inspection]"),
        (["test", "project", "-h"], "[Registration]"),
        (["test", "reports", "-h"], "[Generation]"),
        (["project", "-h"], "[Registration]"),
        (["monitor", "-h"], "[Inspection]"),
        (["monitor", "capability", "-h"], "[Inspection]"),
    ],
)
def test_parent_help_pages_are_grouped(argv, expected_heading, capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(argv)

    captured = capsys.readouterr()

    assert exc_info.value.code == 0
    assert expected_heading in captured.out
    assert "[Options]" in captured.out


def test_human_definition_list_is_sectioned(capsys):
    project_root = Path(__file__).resolve().parents[1]
    catalog_root = project_root / "catalog"

    exit_code = main(["test", "list", "--catalog-root", str(catalog_root)])
    captured = capsys.readouterr()

    assert exit_code == EXIT_OK
    assert "Calamum test definitions" in captured.out
    assert "Summary" in captured.out
    assert "Definitions" in captured.out
    assert "definitions:" not in captured.out
    assert "\n\n  2. " in captured.out
    assert captured.out.endswith("\n\n")


def test_run_and_review_round_trip(tmp_path, capsys):
    catalog_root = tmp_path / "catalog"
    runs_root = tmp_path / "runs"
    reports_root = tmp_path / "reports"
    catalog_root.mkdir()

    catalog_path = catalog_root / "test_definitions.json"
    catalog_payload = {
        "schema_version": "calamum-test-catalog-v2",
        "definitions": [
            {
                "id": "temp-smoke",
                "title": "Temporary smoke definition",
                "summary": "Exercise all canonical lanes through the CLI.",
                "status": "active",
                "category": "regression",
                "selector_policy": "exact-name-only",
                "profiles": ["default"],
                "tags": ["cli"],
                "policy_flags": ["json-first"],
                "evidence_requirements": ["report_json", "report_md"],
                "default_lanes": ["pytest", "sandbox_test", "empirical_test"],
                "lanes": {
                    "pytest": [
                        {
                            "id": "pytest-step",
                            "title": "Pytest step",
                            "command": [sys.executable, "-c", "print('pytest lane ok')"],
                        }
                    ],
                    "sandbox_test": [
                        {
                            "id": "sandbox-step",
                            "title": "Sandbox step",
                            "command": [sys.executable, "-c", "print('sandbox lane ok')"],
                        }
                    ],
                    "empirical_test": [
                        {
                            "id": "empirical-step",
                            "title": "Empirical step",
                            "command": [sys.executable, "-c", "print('empirical lane ok')"],
                        }
                    ],
                },
            }
        ],
    }
    catalog_path.write_text(json.dumps(catalog_payload, indent=2) + "\n", encoding="utf-8")

    exit_code = main(
        [
            "test",
            "run",
            "temp-smoke",
            "--job",
            "job-1",
            "--catalog-root",
            str(catalog_root),
            "--runs-root",
            str(runs_root),
            "--json",
        ]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == EXIT_OK
    assert payload["decision"] == "go"
    assert payload["result"] == "pass"
    assert payload["run_id"]

    run_id = payload["run_id"]
    report_json_path = Path(payload["artifacts"]["report_json"])
    report_md_path = Path(payload["artifacts"]["report_md"])
    manifest_json_path = Path(payload["artifacts"]["manifest_json"])
    checksums_json_path = Path(payload["artifacts"]["checksums_json"])
    run_index_path = Path(payload["artifacts"]["run_index"])

    assert report_json_path.exists()
    assert report_md_path.exists()
    assert manifest_json_path.exists()
    assert checksums_json_path.exists()
    assert run_index_path.exists()

    exit_code = main(["test", "runs", "show", run_id, "--runs-root", str(runs_root), "--json"])
    captured = capsys.readouterr()
    show_payload = json.loads(captured.out)

    assert exit_code == EXIT_OK
    assert show_payload["decision"] == "go"
    assert show_payload["definition_id"] == "temp-smoke"
    assert show_payload["result"] == "pass"

    exit_code = main(["test", "runs", "show", run_id, "--runs-root", str(runs_root)])
    captured = capsys.readouterr()

    assert exit_code == EXIT_OK
    assert "Calamum retained run" in captured.out
    assert "Artifacts" in captured.out
    assert "Next review" in captured.out

    aggregate_exit = main(
        [
            "test",
            "reports",
            "generate",
            "--scope",
            "job",
            "--job",
            "job-1",
            "--runs-root",
            str(runs_root),
            "--reports-root",
            str(reports_root),
            "--json",
        ]
    )
    captured = capsys.readouterr()
    aggregate_payload = json.loads(captured.out)

    assert aggregate_exit == EXIT_OK
    assert aggregate_payload["decision"] == "go"
    assert Path(aggregate_payload["artifacts"]["report_json"]).exists()


@pytest.mark.parametrize("subcommand", ["show", "run"])
def test_definition_argument_help_is_explicit(subcommand, capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["test", subcommand, "-h"])

    captured = capsys.readouterr()

    assert exc_info.value.code == 0
    assert "definition_id" in captured.out
    assert "Exact test definition id from the catalog" in captured.out
    assert "Example:" in captured.out
    assert "calamum test list" in captured.out


def test_project_register_and_current_via_cli(tmp_path, monkeypatch, capsys):
    config_root = tmp_path / "config"
    project_root = tmp_path / "cli-project"
    project_root.mkdir(parents=True)
    (project_root / "src").mkdir()
    (project_root / "tests").mkdir()
    (project_root / "catalog").mkdir()
    (project_root / "pyproject.toml").write_text("[project]\nname='cli-project'\nversion='0.0.0'\n", encoding="utf-8")
    monkeypatch.setenv("CALAMUM_CONFIG_ROOT", str(config_root))

    exit_code = main(
        [
            "project",
            "register",
            "--id",
            "cli-project",
            "--root",
            str(project_root),
            "--name",
            "CLI Project",
            "--alias",
            "cli",
            "--require-marker",
            "pyproject.toml",
            "--require-path",
            "src",
            "--require-path",
            "tests",
            "--require-path",
            "catalog",
            "--write-local-override",
            "--set-current",
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert exit_code == EXIT_OK
    assert payload["decision"] == "go"
    assert payload["project"]["runs_root"] == ".calamum/generated/runs"
    assert payload["project"]["reports_root"] == ".calamum/generated/reports"

    exit_code = main(["project", "current", "--config-root", str(config_root), "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert exit_code == EXIT_OK
    assert payload["project"]["project_id"] == "cli-project"

    exit_code = main(["project", "current", "--config-root", str(config_root)])
    captured = capsys.readouterr()
    assert exit_code == EXIT_OK
    assert "Calamum project context" in captured.out
    assert "Paths" in captured.out
    assert "Runtime contract" in captured.out

    exit_code = main(["test", "project", "current", "--config-root", str(config_root), "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert exit_code == EXIT_OK
    assert payload["project"]["project_id"] == "cli-project"


def test_project_register_interactive(tmp_path, monkeypatch, capsys):
    config_root = tmp_path / "config"
    project_root = tmp_path / "interactive-project"
    project_root.mkdir(parents=True)
    (project_root / "src").mkdir()
    (project_root / "tests").mkdir()
    (project_root / "catalog").mkdir()
    (project_root / "pyproject.toml").write_text("[project]\nname='interactive-project'\nversion='0.0.0'\n", encoding="utf-8")
    monkeypatch.setenv("CALAMUM_CONFIG_ROOT", str(config_root))

    answers = iter(["interactive-project", str(project_root), "Interactive Project"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    exit_code = main(
        [
            "project",
            "register",
            "--interactive",
            "--write-local-override",
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == EXIT_OK
    assert payload["decision"] == "go"
    assert payload["project"]["project_id"] == "interactive-project"


def test_monitor_capability_list_human_and_json(capsys):
    exit_code = main(["monitor", "capability", "list", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == EXIT_OK
    assert payload["decision"] == "go"
    assert payload["monitor_surface_status"] == "scaffolded"
    assert payload["json_noninteractive"] is True
    assert "monitor" in payload["canonical_root_commands"]

    exit_code = main(["monitor", "capability", "list"])
    captured = capsys.readouterr()
    assert exit_code == EXIT_OK
    assert "Calamum monitor capability" in captured.out
    assert "Adapters" in captured.out
    assert "Runtime signals" in captured.out


def test_human_no_go_output_is_sectioned(capsys):
    project_root = Path(__file__).resolve().parents[1]
    catalog_root = project_root / "catalog"

    exit_code = main(["test", "show", "missing-definition", "--catalog-root", str(catalog_root)])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Calamum test definition" in captured.out
    assert "decision: no-go" in captured.out
    assert "unknown_test_definition" in captured.out
