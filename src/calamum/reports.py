from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

from .layout import ensure_generated_output_layout, infer_project_root_from_runtime_root
from .projects import ResolvedProject, public_path_reference, relative_or_absolute_path
from .render import render_aggregate_markdown
from .signing import sign_json_artifact, verify_json_artifact, verify_signature, write_checksum_sidecar

AGGREGATE_SCHEMA_VERSION = "calamum-aggregate-report-v1"
REQUEST_SCHEMA_VERSION = "calamum-privileged-request-v1"
RECEIPT_SCHEMA_VERSION = "calamum-privileged-receipt-v1"


class ReportError(RuntimeError):
    """Raised when aggregate report generation cannot proceed."""


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(value: str) -> str:
    compact = []
    for char in str(value or "").strip().lower():
        if char.isalnum():
            compact.append(char)
        else:
            compact.append("-")
    token = "".join(compact)
    while "--" in token:
        token = token.replace("--", "-")
    return token.strip("-") or "aggregate"


def default_reports_root(project_context: Optional[ResolvedProject], runs_root: Path) -> Path:
    if project_context is not None:
        return project_context.reports_root
    return runs_root.parent / "reports"


def report_index_path(reports_root: Path) -> Path:
    return Path(reports_root) / "generated" / "report_index.jsonl"


def list_reports(reports_root: Path) -> List[Dict[str, Any]]:
    index_path = report_index_path(reports_root)
    if not index_path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with index_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = str(raw_line or "").strip()
            if not line:
                continue
            payload = json.loads(line)
            if isinstance(payload, dict):
                rows.append(payload)
    return rows


def get_report(report_ref: str, reports_root: Path) -> Optional[Dict[str, Any]]:
    text = str(report_ref or "").strip()
    if not text:
        return None
    candidate = Path(text)
    if candidate.exists() and candidate.is_file():
        payload = json.loads(candidate.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else None

    if ":" not in text:
        return None
    scope, target = text.split(":", 1)
    report_path = Path(reports_root) / "generated" / slugify(scope) / slugify(target) / "report.json"
    if not report_path.exists():
        return None
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else None


def load_run_reports(runs_root: Path) -> List[Dict[str, Any]]:
    index_path = Path(runs_root) / "run_index.jsonl"
    if not index_path.exists():
        return []

    reports: List[Dict[str, Any]] = []
    with index_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = str(raw_line or "").strip()
            if not line:
                continue
            entry = json.loads(line)
            if not isinstance(entry, dict):
                continue
            report_path = str(entry.get("report_json", "") or "").strip()
            if not report_path:
                continue
            candidate = Path(report_path)
            if not candidate.is_absolute():
                candidate = (Path(runs_root).parent / candidate).resolve()
            if not candidate.exists():
                continue
            payload = json.loads(candidate.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                reports.append(payload)
    return reports


def _parse_timestamp(value: str) -> datetime:
    text = str(value or "").strip()
    if not text:
        return datetime.fromtimestamp(0, tz=timezone.utc)
    normalized = text.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except Exception:
        return datetime.fromtimestamp(0, tz=timezone.utc)


def _require_request_target(scope: str, *, project_id: str, domain: str, job_id: str) -> str:
    normalized_scope = str(scope or "").strip().lower()
    if normalized_scope == "project":
        if not project_id:
            raise ReportError("Project aggregates require a project id.")
        return project_id
    if normalized_scope == "domain":
        if not domain:
            raise ReportError("Domain aggregates require a domain value.")
        return domain
    if normalized_scope == "job":
        if not job_id:
            raise ReportError("Job aggregates require a job id.")
        return job_id
    raise ReportError("Unsupported aggregate scope: {0}".format(scope))


def _filter_reports(
    reports: List[Dict[str, Any]],
    *,
    scope: str,
    project_id: str,
    domain: str,
    job_id: str,
) -> List[Dict[str, Any]]:
    normalized_scope = str(scope or "").strip().lower()
    selected: List[Dict[str, Any]] = []
    for report in reports:
        project_payload = report.get("project", {}) if isinstance(report.get("project", {}), dict) else {}
        report_project_id = str(report.get("project_id", "") or project_payload.get("project_id", "") or "").strip()
        report_domain = str(report.get("domain", "") or project_payload.get("domain", "") or "").strip()
        report_job_id = str(report.get("job_id", "") or "").strip()
        if normalized_scope == "project" and report_project_id == project_id:
            selected.append(report)
        elif normalized_scope == "domain" and report_domain == domain:
            selected.append(report)
        elif normalized_scope == "job" and report_job_id == job_id:
            selected.append(report)
    return selected


def _lane_totals(reports: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    totals: Dict[str, Dict[str, int]] = {}
    for report in reports:
        for lane in list(report.get("lanes", [])):
            if not isinstance(lane, dict):
                continue
            lane_name = str(lane.get("lane", "") or "unknown").strip() or "unknown"
            result = str(lane.get("result", "unknown") or "unknown").strip() or "unknown"
            bucket = totals.setdefault(lane_name, {})
            bucket[result] = int(bucket.get(result, 0)) + 1
    return totals


def _result_totals(reports: List[Dict[str, Any]]) -> Dict[str, int]:
    totals: Dict[str, int] = {}
    for report in reports:
        result = str(report.get("result", "unknown") or "unknown").strip() or "unknown"
        totals[result] = int(totals.get(result, 0)) + 1
    return totals


def _definition_totals(reports: List[Dict[str, Any]]) -> Dict[str, int]:
    totals: Dict[str, int] = {}
    for report in reports:
        definition_id = str(report.get("definition_id", "") or "unknown").strip() or "unknown"
        totals[definition_id] = int(totals.get(definition_id, 0)) + 1
    return totals


def _verify_request(
    request_payload: Dict[str, Any],
    request_signature: str,
    *,
    trusted_requesters: List[str],
    public_key_path: Optional[str] = None,
) -> Dict[str, Any]:
    requester_id = str(request_payload.get("requester_id", "") or "").strip()
    if not requester_id:
        raise ReportError("Privileged requests require requester_id.")
    if trusted_requesters and requester_id not in trusted_requesters:
        raise ReportError("Requester is not allowlisted: {0}".format(requester_id))
    expires_at = str(request_payload.get("expires_at", "") or "").strip()
    if expires_at and _parse_timestamp(expires_at) < datetime.now(timezone.utc):
        raise ReportError("Privileged request has expired.")
    if not verify_signature(request_payload, request_signature, public_key_path=public_key_path):
        raise ReportError("Privileged request signature verification failed.")
    return {
        "request_id": str(request_payload.get("request_id", "") or "").strip(),
        "requester_id": requester_id,
        "verified": True,
        "expires_at": expires_at,
    }


def _write_receipt(
    receipt_path: Path,
    payload: Dict[str, Any],
    *,
    sign: bool,
    allow_fallback_signature: bool,
    signing_key_path: Optional[str] = None,
) -> Dict[str, str]:
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_checksum_sidecar(receipt_path)
    artifacts = {"receipt_json": str(receipt_path)}
    if sign:
        signed = sign_json_artifact(
            receipt_path,
            key_path=signing_key_path,
            allow_fallback=allow_fallback_signature,
        )
        if not verify_json_artifact(receipt_path):
            raise ReportError("Receipt signature verification failed after write.")
        artifacts.update(
            {
                "receipt_signature": signed["signature_path"],
                "receipt_checksum": signed["checksum_path"],
            }
        )
    return artifacts


def generate_report(
    *,
    scope: str,
    runs_root: Path,
    reports_root: Path,
    project_context: Optional[ResolvedProject] = None,
    project_id: str = "",
    domain: str = "",
    job_id: str = "",
    sign: bool = False,
    request_payload: Optional[Dict[str, Any]] = None,
    request_signature: str = "",
    public_key_path: Optional[str] = None,
    signing_key_path: Optional[str] = None,
    allow_fallback_signature: bool = True,
) -> Dict[str, Any]:
    normalized_scope = str(scope or "").strip().lower()
    effective_project_id = str(project_id or (project_context.project_id if project_context is not None else "")).strip()
    effective_domain = str(domain or (project_context.domain if project_context is not None else "")).strip()
    effective_job_id = str(job_id or "").strip()
    target = _require_request_target(
        normalized_scope,
        project_id=effective_project_id,
        domain=effective_domain,
        job_id=effective_job_id,
    )

    trusted_requesters = list(project_context.trusted_requesters) if project_context is not None else []
    request_details = {}
    if request_payload is not None:
        if not request_signature:
            raise ReportError("A detached request signature is required for privileged report generation.")
        request_details = _verify_request(
            request_payload,
            request_signature,
            trusted_requesters=trusted_requesters,
            public_key_path=public_key_path,
        )

    runs_root = Path(runs_root).resolve()
    reports_root = Path(reports_root).resolve()
    report_rows = load_run_reports(runs_root)
    selected = _filter_reports(
        report_rows,
        scope=normalized_scope,
        project_id=effective_project_id,
        domain=effective_domain,
        job_id=effective_job_id,
    )
    if not selected:
        raise ReportError("No retained runs matched the requested aggregate scope.")

    selected.sort(key=lambda item: _parse_timestamp(str(item.get("recorded_at", ""))), reverse=True)
    generated_at = utc_now()
    target_slug = slugify(target)
    aggregate_root = reports_root / "generated" / normalized_scope / target_slug
    history_root = aggregate_root / "history" / generated_at.replace(":", "").replace("-", "")
    aggregate_root.mkdir(parents=True, exist_ok=True)
    history_root.mkdir(parents=True, exist_ok=True)

    report_json_path = aggregate_root / "report.json"
    report_md_path = aggregate_root / "report.md"
    manifest_json_path = aggregate_root / "manifest.json"
    receipt_json_path = aggregate_root / "receipt.json"

    if project_context is not None:
        project_root = project_context.project_root
    else:
        project_root = infer_project_root_from_runtime_root(reports_root, Path.cwd())

    ensure_generated_output_layout(project_root, runs_root, reports_root)

    report_ref = "{0}:{1}".format(normalized_scope, target_slug)
    report_payload = {
        "schema_version": AGGREGATE_SCHEMA_VERSION,
        "kind": "aggregate_report",
        "scope": normalized_scope,
        "target": target,
        "report_ref": report_ref,
        "generated_at": generated_at,
        "project_id": effective_project_id,
        "domain": effective_domain,
        "job_id": effective_job_id,
        "project": project_context.to_payload() if project_context is not None else {},
        "source_runs_root": relative_or_absolute_path(runs_root, project_root),
        "report_root": relative_or_absolute_path(aggregate_root, project_root),
        "request": request_details,
        "run_count": len(selected),
        "result_totals": _result_totals(selected),
        "definition_totals": _definition_totals(selected),
        "lane_totals": _lane_totals(selected),
        "latest_run": {
            "run_id": selected[0].get("run_id", ""),
            "definition_id": selected[0].get("definition_id", ""),
            "result": selected[0].get("result", ""),
            "recorded_at": selected[0].get("recorded_at", ""),
        },
        "runs": [
            {
                "run_id": item.get("run_id", ""),
                "definition_id": item.get("definition_id", ""),
                "result": item.get("result", ""),
                "recorded_at": item.get("recorded_at", ""),
                "job_id": item.get("job_id", ""),
                "project_id": item.get("project_id", ""),
                "domain": item.get("domain", ""),
                "report_json": public_path_reference(Path(str(item.get("artifacts", {}).get("report_json", "") or "")), project_root)
                if str(item.get("artifacts", {}).get("report_json", "") or "").strip()
                else "",
                "report_md": public_path_reference(Path(str(item.get("artifacts", {}).get("report_md", "") or "")), project_root)
                if str(item.get("artifacts", {}).get("report_md", "") or "").strip()
                else "",
            }
            for item in selected
        ],
    }

    manifest_payload = {
        "schema_version": AGGREGATE_SCHEMA_VERSION,
        "kind": "aggregate_manifest",
        "scope": normalized_scope,
        "target": target,
        "report_ref": report_ref,
        "generated_at": generated_at,
        "report_paths": {
            "report_json": relative_or_absolute_path(report_json_path, project_root),
            "report_md": relative_or_absolute_path(report_md_path, project_root),
            "manifest_json": relative_or_absolute_path(manifest_json_path, project_root),
            "receipt_json": relative_or_absolute_path(receipt_json_path, project_root),
        },
        "source_run_count": len(selected),
        "source_runs_root": relative_or_absolute_path(runs_root, project_root),
        "request": request_details,
        "signing_requested": bool(sign),
        "filters": {
            "project_id": effective_project_id,
            "domain": effective_domain,
            "job_id": effective_job_id,
        },
    }

    report_json_path.write_text(json.dumps(report_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_md_path.write_text(render_aggregate_markdown(report_payload), encoding="utf-8")
    manifest_json_path.write_text(json.dumps(manifest_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    checksum_paths = {
        "report_json_checksum": str(write_checksum_sidecar(report_json_path)),
        "report_md_checksum": str(write_checksum_sidecar(report_md_path)),
        "manifest_json_checksum": str(write_checksum_sidecar(manifest_json_path)),
    }

    signature_paths = {}
    if sign:
        report_signed = sign_json_artifact(
            report_json_path,
            key_path=signing_key_path,
            allow_fallback=allow_fallback_signature,
        )
        manifest_signed = sign_json_artifact(
            manifest_json_path,
            key_path=signing_key_path,
            allow_fallback=allow_fallback_signature,
        )
        if not verify_json_artifact(report_json_path, public_key_path=public_key_path):
            raise ReportError("Aggregate report signature verification failed after write.")
        if not verify_json_artifact(manifest_json_path, public_key_path=public_key_path):
            raise ReportError("Aggregate manifest signature verification failed after write.")
        signature_paths = {
            "report_signature": report_signed["signature_path"],
            "manifest_signature": manifest_signed["signature_path"],
        }

    receipt_payload = {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "kind": "privileged_receipt",
        "report_ref": report_ref,
        "scope": normalized_scope,
        "target": target,
        "generated_at": generated_at,
        "decision": "go",
        "request": request_details,
        "artifacts": {
            "report_json": relative_or_absolute_path(report_json_path, project_root),
            "report_md": relative_or_absolute_path(report_md_path, project_root),
            "manifest_json": relative_or_absolute_path(manifest_json_path, project_root),
        },
    }
    receipt_artifacts = _write_receipt(
        receipt_json_path,
        receipt_payload,
        sign=bool(sign or request_payload is not None),
        allow_fallback_signature=allow_fallback_signature,
        signing_key_path=signing_key_path,
    )

    for source_path in (report_json_path, report_md_path, manifest_json_path, receipt_json_path):
        shutil.copy2(str(source_path), str(history_root / source_path.name))
        checksum_file = source_path.with_suffix(source_path.suffix + ".sha256")
        if checksum_file.exists():
            shutil.copy2(str(checksum_file), str(history_root / checksum_file.name))
        signature_file = source_path.with_suffix(source_path.suffix + ".sig")
        if signature_file.exists():
            shutil.copy2(str(signature_file), str(history_root / signature_file.name))

    index_entry = {
        "report_ref": report_ref,
        "scope": normalized_scope,
        "target": target,
        "generated_at": generated_at,
        "report_json": str(report_json_path),
        "report_md": str(report_md_path),
        "manifest_json": str(manifest_json_path),
        "receipt_json": str(receipt_json_path),
        "run_count": len(selected),
    }
    index_path = report_index_path(reports_root)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with index_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(index_entry, sort_keys=True) + "\n")

    return {
        "decision": "go",
        "action": "reports-generate",
        "scope": normalized_scope,
        "target": target,
        "report_ref": report_ref,
        "run_count": len(selected),
        "report": report_payload,
        "artifacts": {
            "report_json": str(report_json_path),
            "report_md": str(report_md_path),
            "manifest_json": str(manifest_json_path),
            "receipt_json": receipt_artifacts.get("receipt_json", str(receipt_json_path)),
            "history_root": str(history_root),
            "report_index": str(index_path),
            **checksum_paths,
            **signature_paths,
            **{key: value for key, value in receipt_artifacts.items() if key != "receipt_json"},
        },
        "request": request_details,
    }
