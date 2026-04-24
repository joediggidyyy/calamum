from pathlib import Path

import pytest

from calamum.reports import ReportError, generate_report, utc_now
from calamum.projects import register_project, resolve_project
from calamum.runner import run_definition
from calamum.signing import sign_payload, verify_json_artifact


@pytest.fixture()
def registered_project(tmp_path, monkeypatch):
    project_root = tmp_path / "aggregate-project"
    config_root = tmp_path / "config"
    project_root.mkdir(parents=True, exist_ok=True)
    (project_root / "src").mkdir()
    (project_root / "tests").mkdir()
    (project_root / "catalog").mkdir()
    (project_root / "pyproject.toml").write_text("[project]\nname = 'aggregate-project'\nversion = '0.0.0'\n", encoding="utf-8")
    monkeypatch.setenv("CALAMUM_CONFIG_ROOT", str(config_root))
    register_project(
        project_id="aggregate-project",
        root=project_root,
        name="Aggregate Project",
        aliases=["aggregate"],
        shape_kind="python",
        required_markers=["pyproject.toml"],
        required_paths=["src", "tests", "catalog"],
        trusted_requesters=["codesentinel"],
        write_local_override=True,
        set_current=True,
    )
    resolved = resolve_project(project="aggregate", cwd=project_root, config_root=config_root)
    assert resolved is not None
    return resolved


def build_definition():
    return {
        "id": "aggregate-smoke",
        "title": "Aggregate smoke",
        "summary": "Create retained evidence for aggregate regeneration.",
        "status": "active",
        "category": "regression",
        "selector_policy": "exact-name-only",
        "profiles": ["default"],
        "tags": ["aggregate"],
        "policy_flags": ["json-first"],
        "evidence_requirements": ["report_json", "report_md"],
        "default_lanes": ["pytest", "sandbox_test", "empirical_test"],
        "lanes": {
            "pytest": [{"id": "pytest-step", "title": "Pytest", "command": ["{python}", "-c", "print('pytest ok')"]}],
            "sandbox_test": [{"id": "sandbox-step", "title": "Sandbox", "command": ["{python}", "-c", "print('sandbox ok')"]}],
            "empirical_test": [{"id": "empirical-step", "title": "Empirical", "command": ["{python}", "-c", "print('empirical ok')"]}],
        },
    }


def test_generate_signed_project_aggregate(registered_project, monkeypatch):
    monkeypatch.setenv("CALAMUM_POLICY_SIGNING_KEY", "aggregate-secret")
    definition = build_definition()

    run_packet = run_definition(
        definition=definition,
        runs_root=registered_project.runs_root,
        project_context=registered_project,
        job_id="job-123",
    )
    assert run_packet["decision"] == "go"

    aggregate = generate_report(
        scope="project",
        runs_root=registered_project.runs_root,
        reports_root=registered_project.reports_root,
        project_context=registered_project,
        sign=True,
    )

    assert aggregate["decision"] == "go"
    assert aggregate["run_count"] == 1
    assert Path(aggregate["artifacts"]["report_json"]).exists()
    assert Path(aggregate["artifacts"]["manifest_json"]).exists()
    assert Path(aggregate["artifacts"]["receipt_json"]).exists()
    assert verify_json_artifact(Path(aggregate["artifacts"]["report_json"]))
    assert verify_json_artifact(Path(aggregate["artifacts"]["manifest_json"]))


def test_generate_report_fails_for_untrusted_requester(registered_project, monkeypatch):
    monkeypatch.setenv("CALAMUM_POLICY_SIGNING_KEY", "aggregate-secret")
    definition = build_definition()
    run_definition(
        definition=definition,
        runs_root=registered_project.runs_root,
        project_context=registered_project,
        job_id="job-123",
    )

    request_payload = {
        "schema_version": "calamum-privileged-request-v1",
        "request_id": "req-1",
        "requester_id": "intruder",
        "scope": "project",
        "target": registered_project.project_id,
        "issued_at": utc_now(),
        "expires_at": "2099-01-01T00:00:00Z",
    }
    signature_hex, algorithm = sign_payload(request_payload)

    with pytest.raises(ReportError):
        generate_report(
            scope="project",
            runs_root=registered_project.runs_root,
            reports_root=registered_project.reports_root,
            project_context=registered_project,
            sign=True,
            request_payload=request_payload,
            request_signature="{0}:{1}".format(algorithm, signature_hex),
        )


def test_default_local_outputs_use_calamum_generated_layout(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CALAMUM_POLICY_SIGNING_KEY", "local-secret")

    run_packet = run_definition(
        definition=build_definition(),
        job_id="local-job",
    )
    runs_root = Path(run_packet["artifacts"]["run_index"]).parent
    reports_root = tmp_path / ".calamum" / "generated" / "reports"

    aggregate = generate_report(
        scope="job",
        job_id="local-job",
        runs_root=runs_root,
        reports_root=reports_root,
        sign=True,
    )

    assert runs_root == tmp_path / ".calamum" / "generated" / "runs"
    assert Path(aggregate["artifacts"]["report_index"]).parent.parent == reports_root
    assert (tmp_path / ".calamum" / "generated" / ".gitignore").exists()
    assert Path(aggregate["report"]["source_runs_root"]).as_posix() == ".calamum/generated/runs"
