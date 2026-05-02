import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .catalog import CANONICAL_TEST_LANES, CommandType, default_runs_root
from .layout import default_catalog_root as layout_default_catalog_root
from .layout import ensure_generated_output_layout, infer_project_root_from_runtime_root
from .projects import ResolvedProject, public_path_reference, relative_or_absolute_path
from .render import render_markdown_report
from .signing import write_checksum_sidecar


HEARTBEAT_INTERVAL_SEC = 20


class RunError(RuntimeError):
    """Raised when a run cannot be completed."""


def _emit_heartbeat(msg: str) -> None:
    """Write a single heartbeat line to stderr; monkeypatchable for tests."""
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()


def _drain_pipe(pipe: Any, chunks: List[str], dest_path: Path) -> None:
    """Drain a text pipe line-by-line, accumulating into *chunks* and writing to *dest_path*."""
    try:
        with dest_path.open("w", encoding="utf-8", errors="replace") as fh:
            for line in pipe:
                chunks.append(line)
                fh.write(line)
    except Exception:  # pragma: no cover - I/O failure during drain
        pass


def _supervise_step(
    command: Any,
    cwd: Path,
    env: Dict[str, str],
    stdout_path: Path,
    stderr_path: Path,
    shell: bool,
    run_id: str,
    lane: str,
    step_id: str,
    cwd_ref: str = "",
    heartbeat_interval: int = HEARTBEAT_INTERVAL_SEC,
) -> Tuple[int, str, str]:
    """Spawn *command* with Popen, drain stdout/stderr to files and in-memory, emit heartbeats."""
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=shell,
        cwd=str(cwd),
        env=env,
    )
    stdout_chunks: List[str] = []
    stderr_chunks: List[str] = []
    stdout_thread = threading.Thread(
        target=_drain_pipe, args=(proc.stdout, stdout_chunks, stdout_path), daemon=True
    )
    stderr_thread = threading.Thread(
        target=_drain_pipe, args=(proc.stderr, stderr_chunks, stderr_path), daemon=True
    )
    stdout_thread.start()
    stderr_thread.start()
    start_time = time.monotonic()
    last_heartbeat_time = start_time
    try:
        while proc.poll() is None:
            now = time.monotonic()
            if now - last_heartbeat_time >= heartbeat_interval:
                elapsed = now - start_time
                safe_cwd = cwd_ref or Path(str(cwd)).name
                _emit_heartbeat(
                    "[calamum heartbeat] run={0} lane={1} step={2}"
                    " elapsed={3:.0f}s interval={4}s cwd={5}".format(
                        run_id, lane, step_id, elapsed, heartbeat_interval, safe_cwd
                    )
                )
                last_heartbeat_time = now
            time.sleep(0.5)
    finally:
        stdout_thread.join()
        stderr_thread.join()
    returncode = proc.returncode if proc.returncode is not None else proc.wait()
    return returncode, "".join(stdout_chunks), "".join(stderr_chunks)


def run_definition(
    definition: Dict[str, Any],
    runs_root: Optional[Path] = None,
    requested_lanes: Optional[Sequence[str]] = None,
    dry_run: bool = False,
    project_context: Optional[ResolvedProject] = None,
    job_id: str = "",
) -> Dict[str, Any]:
    root = Path(runs_root) if runs_root is not None else (project_context.runs_root if project_context is not None else default_runs_root())
    project_root = project_context.project_root if project_context is not None else infer_project_root_from_runtime_root(root, Path.cwd())
    default_reports_root = project_context.reports_root if project_context is not None else (root.parent / "reports")
    ensure_generated_output_layout(project_root, root, default_reports_root)
    runtime_tokens = build_runtime_tokens(project_context, project_root, root, default_reports_root)
    selected_lanes = select_lanes(definition, requested_lanes)
    root.mkdir(parents=True, exist_ok=True)

    run_id = build_run_id(str(definition.get("id", "definition")))
    run_dir = root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    lane_reports = []
    overall_result = "planned" if dry_run else "pass"
    for lane_name in selected_lanes:
        lane_report = run_lane(
            lane_name=lane_name,
            steps=list(definition.get("lanes", {}).get(lane_name, [])),
            lane_dir=run_dir / lane_name,
            dry_run=dry_run,
            project_context=project_context,
            runtime_tokens=runtime_tokens,
            _run_id=run_id,
        )
        lane_reports.append(lane_report)
        lane_result = str(lane_report.get("result", "unknown"))
        if lane_result == "failed":
            overall_result = "failed"
        elif overall_result == "pass" and lane_result not in ("pass", "not_applicable"):
            overall_result = lane_result

    recorded_at = utc_now()
    report = {
        "decision": "go" if overall_result in ("pass", "planned", "not_applicable") else "no-go",
        "definition_id": str(definition.get("id", "")),
        "definition_title": str(definition.get("title", "")),
        "definition_summary": str(definition.get("summary", "")),
        "definition_tags": list(definition.get("tags", [])),
        "definition_profiles": list(definition.get("profiles", [])),
        "definition_policy_flags": list(definition.get("policy_flags", [])),
        "definition_evidence_requirements": list(definition.get("evidence_requirements", [])),
        "result": overall_result,
        "recorded_at": recorded_at,
        "run_id": run_id,
        "run_dir": str(run_dir),
        "selected_lanes": list(selected_lanes),
        "lanes": lane_reports,
        "dry_run": bool(dry_run),
        "job_id": str(job_id or "").strip(),
        "project_id": project_context.project_id if project_context is not None else "",
        "domain": project_context.domain if project_context is not None else "",
        "project": project_context.to_payload() if project_context is not None else {},
        "next_review_command": "calamum test runs show {0}".format(run_id),
        "artifacts": {},
    }

    report_json_path = run_dir / "report.json"
    report_md_path = run_dir / "report.md"
    checksums_json_path = run_dir / "checksums.json"
    manifest_json_path = run_dir / "manifest.json"
    report["artifacts"] = {
        "report_json": str(report_json_path),
        "report_md": str(report_md_path),
        "checksums_json": str(checksums_json_path),
        "manifest_json": str(manifest_json_path),
        "run_index": str(root / "run_index.jsonl"),
        "checksum_sidecars": [
            str(report_json_path.with_suffix(report_json_path.suffix + ".sha256")),
            str(report_md_path.with_suffix(report_md_path.suffix + ".sha256")),
            str(checksums_json_path.with_suffix(checksums_json_path.suffix + ".sha256")),
            str(manifest_json_path.with_suffix(manifest_json_path.suffix + ".sha256")),
        ],
    }

    write_json(report_json_path, report)
    report_md_path.write_text(render_markdown_report(report), encoding="utf-8")
    checksum_payload = build_checksum_payload(run_dir, report, project_context, project_root=project_root)
    write_json(checksums_json_path, checksum_payload)
    manifest_payload = build_manifest_payload(run_dir, report, checksum_payload, project_context, project_root=project_root)
    write_json(manifest_json_path, manifest_payload)
    checksum_sidecars = [
        str(write_checksum_sidecar(report_json_path)),
        str(write_checksum_sidecar(report_md_path)),
        str(write_checksum_sidecar(checksums_json_path)),
        str(write_checksum_sidecar(manifest_json_path)),
    ]
    report["artifacts"]["checksum_sidecars"] = checksum_sidecars
    append_run_index(root / "run_index.jsonl", report)
    return report


def list_runs(runs_root: Optional[Path] = None) -> List[Dict[str, Any]]:
    root = Path(runs_root) if runs_root is not None else default_runs_root()
    index_path = root / "run_index.jsonl"
    if not index_path.exists():
        return []

    rows = []
    with index_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = str(raw_line).strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def get_run(run_id: str, runs_root: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    root = Path(runs_root) if runs_root is not None else default_runs_root()
    report_path = root / str(run_id) / "report.json"
    if not report_path.exists():
        return None
    with report_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def append_run_index(index_path: Path, report: Dict[str, Any]) -> None:
    index_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "run_id": report.get("run_id", ""),
        "definition_id": report.get("definition_id", ""),
        "result": report.get("result", "unknown"),
        "recorded_at": report.get("recorded_at", ""),
        "project_id": report.get("project_id", ""),
        "domain": report.get("domain", ""),
        "job_id": report.get("job_id", ""),
        "report_json": report.get("artifacts", {}).get("report_json", ""),
        "report_md": report.get("artifacts", {}).get("report_md", ""),
        "manifest_json": report.get("artifacts", {}).get("manifest_json", ""),
        "selected_lanes": report.get("selected_lanes", []),
    }
    with index_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")


def run_lane(
    lane_name: str,
    steps: Iterable[Dict[str, Any]],
    lane_dir: Path,
    dry_run: bool,
    project_context: Optional[ResolvedProject] = None,
    runtime_tokens: Optional[Dict[str, str]] = None,
    _run_id: str = "",
) -> Dict[str, Any]:
    lane_dir.mkdir(parents=True, exist_ok=True)
    normalized_steps = list(steps)
    if len(normalized_steps) == 0:
        return {"lane": lane_name, "result": "not_applicable", "steps": []}

    results = []
    lane_result = "planned" if dry_run else "pass"
    for step in normalized_steps:
        result = run_step(
            step,
            lane_dir,
            dry_run=dry_run,
            project_context=project_context,
            runtime_tokens=runtime_tokens,
            _run_id=_run_id,
            _lane=lane_name,
        )
        results.append(result)
        if result.get("result") == "failed":
            lane_result = "failed"
        elif lane_result == "pass" and result.get("result") != "pass":
            lane_result = str(result.get("result"))

    return {"lane": lane_name, "result": lane_result, "steps": results}


def run_step(
    step: Dict[str, Any],
    lane_dir: Path,
    dry_run: bool,
    project_context: Optional[ResolvedProject] = None,
    runtime_tokens: Optional[Dict[str, str]] = None,
    _run_id: str = "",
    _lane: str = "",
) -> Dict[str, Any]:
    step_id = str(step.get("id", "step")).strip() or "step"
    title = str(step.get("title", step_id)).strip() or step_id
    command = resolve_step_command(step.get("command", []), project_context, runtime_tokens=runtime_tokens)
    command_display = display_command(command)
    stdout_path = lane_dir / "{0}.stdout.txt".format(step_id)
    stderr_path = lane_dir / "{0}.stderr.txt".format(step_id)
    cwd_path = resolve_step_cwd(step, project_context, runtime_tokens=runtime_tokens)
    env_payload = resolve_step_env(step, project_context, runtime_tokens=runtime_tokens)
    env_keys = sorted([key for key in env_payload.keys() if key.startswith("CALAMUM_")])

    if dry_run:
        return {
            "id": step_id,
            "title": title,
            "command_display": command_display,
            "result": "planned",
            "returncode": None,
            "cwd": str(cwd_path),
            "env_keys": env_keys,
            "expected_artifacts": list(step.get("expected_artifacts", [])),
            "evidence_requirements": list(step.get("evidence_requirements", [])),
            "notes": str(step.get("notes", "") or "").strip(),
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
        }

    returncode, stdout_text, stderr_text = _supervise_step(
        command=command,
        cwd=cwd_path,
        env=env_payload,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        shell=bool(step.get("shell", False)) or isinstance(command, str),
        run_id=str(_run_id or ""),
        lane=str(_lane or ""),
        step_id=step_id,
        cwd_ref=Path(str(cwd_path)).name,
    )

    allow_failure = bool(step.get("allow_failure", False))
    result = "pass"
    if returncode != 0:
        result = "allowed_failure" if allow_failure else "failed"

    return {
        "id": step_id,
        "title": title,
        "command_display": command_display,
        "result": result,
        "returncode": int(returncode),
        "cwd": str(cwd_path),
        "env_keys": env_keys,
        "expected_artifacts": list(step.get("expected_artifacts", [])),
        "evidence_requirements": list(step.get("evidence_requirements", [])),
        "notes": str(step.get("notes", "") or "").strip(),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
    }


def select_lanes(definition: Dict[str, Any], requested_lanes: Optional[Sequence[str]]) -> List[str]:
    if not requested_lanes:
        defaults = list(definition.get("default_lanes", []))
        return defaults or list(CANONICAL_TEST_LANES)

    allowed = set(CANONICAL_TEST_LANES)
    selected = []
    for lane in requested_lanes:
        normalized = str(lane or "").strip()
        if normalized not in allowed:
            raise RunError("Unknown test lane: {0}".format(normalized))
        if normalized not in selected:
            selected.append(normalized)

    if len(selected) == 0:
        return list(CANONICAL_TEST_LANES)
    return selected


def build_run_id(definition_id: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    compact = []
    for char in str(definition_id or "definition").lower():
        if char.isalnum():
            compact.append(char)
        else:
            compact.append("-")
    slug = "".join(compact).strip("-") or "definition"
    return "{0}-{1}".format(stamp, slug)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def display_command(command: CommandType) -> str:
    if isinstance(command, str):
        return command
    return subprocess.list2cmdline(list(command))


def build_runtime_tokens(
    project_context: Optional[ResolvedProject],
    project_root: Path,
    runs_root: Path,
    reports_root: Path,
) -> Dict[str, str]:
    if project_context is not None:
        return project_context.token_map()

    return {
        "project_id": "",
        "project_name": project_root.name,
        "project_root": str(project_root),
        "descriptor_path": str(project_root / ".calamum" / "project.json"),
        "catalog_root": str(layout_default_catalog_root(project_root)),
        "runs_root": str(runs_root),
        "reports_root": str(reports_root),
        "working_dir": str(project_root),
        "python": sys.executable,
        "shell": str(os.environ.get("COMSPEC", "") or "").strip(),
        "env_file": "",
        "domain": "",
        "application": "",
        "source_root": str((project_root / "src").resolve()),
        "tests_root": str((project_root / "tests").resolve()),
        "artifacts_root": str((project_root / "dist").resolve()),
    }


def substitute_tokens(
    raw_value: str,
    project_context: Optional[ResolvedProject],
    runtime_tokens: Optional[Dict[str, str]] = None,
) -> str:
    text = str(raw_value or "")
    if project_context is None and not runtime_tokens:
        return text
    tokens = project_context.token_map() if project_context is not None else {}
    tokens.update(dict(runtime_tokens or {}))
    result = text
    start = 0
    while True:
        open_index = result.find("{", start)
        if open_index < 0:
            break
        close_index = result.find("}", open_index + 1)
        if close_index < 0:
            break
        token_name = result[open_index + 1 : close_index]
        if token_name in tokens:
            result = result[:open_index] + str(tokens[token_name]) + result[close_index + 1 :]
            start = open_index + len(str(tokens[token_name]))
            continue
        raise RunError("Unresolved Calamum token: {0}".format(token_name))
    return result


def resolve_step_command(
    command: CommandType,
    project_context: Optional[ResolvedProject],
    runtime_tokens: Optional[Dict[str, str]] = None,
) -> CommandType:
    if isinstance(command, str):
        return substitute_tokens(command, project_context, runtime_tokens=runtime_tokens)
    return [substitute_tokens(str(part), project_context, runtime_tokens=runtime_tokens) for part in list(command)]


def resolve_step_cwd(
    step: Dict[str, Any],
    project_context: Optional[ResolvedProject],
    runtime_tokens: Optional[Dict[str, str]] = None,
) -> Path:
    raw_cwd = str(step.get("cwd", "") or "").strip()
    if project_context is None:
        base_root = Path(str((runtime_tokens or {}).get("project_root", Path.cwd()))).resolve()
        default_working_dir = Path(str((runtime_tokens or {}).get("working_dir", base_root))).resolve()
        target = (
            Path(substitute_tokens(raw_cwd, project_context, runtime_tokens=runtime_tokens))
            if raw_cwd
            else default_working_dir
        )
        if not target.is_absolute():
            target = (base_root / target).resolve()
        return target
    raw_cwd = str(step.get("cwd", "") or "").strip()
    target = (
        Path(substitute_tokens(raw_cwd, project_context, runtime_tokens=runtime_tokens))
        if raw_cwd
        else project_context.working_dir
    )
    if not target.is_absolute():
        target = (project_context.project_root / target).resolve()
    assert_path_contained(target, project_context)
    return target


def parse_env_file(path: Path) -> Dict[str, str]:
    payload: Dict[str, str] = {}
    if not path.exists():
        return payload
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = str(raw_line or "").strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        normalized_key = str(key or "").strip()
        normalized_value = str(value or "").strip()
        if normalized_key:
            payload[normalized_key] = normalized_value
    return payload


def resolve_step_env(
    step: Dict[str, Any],
    project_context: Optional[ResolvedProject],
    runtime_tokens: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    env_payload = dict(os.environ)
    if project_context is not None and project_context.env_file:
        env_payload.update(parse_env_file(Path(project_context.env_file)))
        env_payload.setdefault("CALAMUM_PROJECT_ID", project_context.project_id)
        env_payload.setdefault("CALAMUM_PROJECT_ROOT", str(project_context.project_root))
        env_payload.setdefault("CALAMUM_REPORTS_ROOT", str(project_context.reports_root))
        env_payload.setdefault("CALAMUM_RUNS_ROOT", str(project_context.runs_root))
    elif runtime_tokens:
        if str(runtime_tokens.get("project_id", "")).strip():
            env_payload.setdefault("CALAMUM_PROJECT_ID", str(runtime_tokens.get("project_id", "")))
        env_payload.setdefault("CALAMUM_PROJECT_ROOT", str(runtime_tokens.get("project_root", "")))
        env_payload.setdefault("CALAMUM_REPORTS_ROOT", str(runtime_tokens.get("reports_root", "")))
        env_payload.setdefault("CALAMUM_RUNS_ROOT", str(runtime_tokens.get("runs_root", "")))
    step_env = step.get("env", {}) if isinstance(step.get("env", {}), dict) else {}
    for key, value in step_env.items():
        env_payload[str(key)] = substitute_tokens(str(value), project_context, runtime_tokens=runtime_tokens)
    return env_payload


def assert_path_contained(path: Path, project_context: ResolvedProject) -> None:
    allowed_roots = [
        project_context.project_root,
        project_context.runs_root,
        project_context.reports_root,
        project_context.working_dir,
    ] + list(project_context.resolved_path_aliases.values())
    for root in allowed_roots:
        try:
            Path(path).resolve().relative_to(Path(root).resolve())
            return
        except Exception:
            continue
    raise RunError("Resolved step path escapes declared Calamum roots: {0}".format(path))


def build_checksum_payload(
    run_dir: Path,
    report: Dict[str, Any],
    project_context: Optional[ResolvedProject],
    project_root: Optional[Path] = None,
) -> Dict[str, Any]:
    resolved_project_root = (
        Path(project_root).resolve()
        if project_root is not None
        else (project_context.project_root if project_context is not None else infer_project_root_from_runtime_root(run_dir.parent, Path.cwd()))
    )
    files = []
    for path in sorted(run_dir.rglob("*")):
        if path.is_dir():
            continue
        if path.name.endswith(".sha256"):
            continue
        files.append(
            {
                "path": public_path_reference(path, resolved_project_root),
                "sha256": sha256_file(path),
            }
        )
    return {
        "schema_version": "calamum-run-checksums-v1",
        "run_id": report.get("run_id", ""),
        "generated_at": utc_now(),
        "files": files,
    }


def build_manifest_payload(
    run_dir: Path,
    report: Dict[str, Any],
    checksum_payload: Dict[str, Any],
    project_context: Optional[ResolvedProject],
    project_root: Optional[Path] = None,
) -> Dict[str, Any]:
    resolved_project_root = (
        Path(project_root).resolve()
        if project_root is not None
        else (project_context.project_root if project_context is not None else infer_project_root_from_runtime_root(run_dir.parent, Path.cwd()))
    )
    return {
        "schema_version": "calamum-run-manifest-v1",
        "kind": "run_manifest",
        "run_id": report.get("run_id", ""),
        "definition_id": report.get("definition_id", ""),
        "result": report.get("result", ""),
        "recorded_at": report.get("recorded_at", ""),
        "project_id": report.get("project_id", ""),
        "domain": report.get("domain", ""),
        "job_id": report.get("job_id", ""),
        "run_dir": public_path_reference(run_dir, resolved_project_root),
        "artifacts": {
            key: public_path_reference(Path(value), resolved_project_root)
            for key, value in report.get("artifacts", {}).items()
            if key != "checksum_sidecars" and str(value).strip()
        },
        "checksum_manifest": public_path_reference(
            Path(str(report.get("artifacts", {}).get("checksums_json", "") or "")),
            resolved_project_root,
        ),
        "files": list(checksum_payload.get("files", [])),
    }


def sha256_file(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()
