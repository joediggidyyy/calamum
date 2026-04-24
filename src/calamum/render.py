import json
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .layout import (
    append_human_section,
    render_human_kv_rows,
    render_human_path_tail,
    style_choice_label,
    style_decision_value,
    style_heading,
)


def _packet_timestamp(payload: Dict[str, Any]) -> str:
    for key in ("generated_at_utc", "generated_at", "recorded_at", "timestamp_utc"):
        value = str(payload.get(key, "")).strip()
        if value:
            return value
    return ""


def _packet_decision(payload: Dict[str, Any]) -> str:
    decision = str(payload.get("decision", "")).strip()
    if decision:
        return decision
    result = str(payload.get("result", "")).strip().lower()
    if result in ("go", "ok", "pass", "success"):
        return "go"
    if result in ("fail", "failed", "error", "err", "no-go"):
        return "no-go"
    if result in ("planned", "dry-run"):
        return "advisory"
    return ""


def _render_header(title: str, payload: Optional[Dict[str, Any]] = None, summary: str = "") -> List[str]:
    packet = payload or {}
    lines = [style_heading(title)]
    timestamp = _packet_timestamp(packet)
    if timestamp:
        lines.append("generated_at_utc: {0}".format(timestamp))
    decision = _packet_decision(packet)
    summary_text = str(summary or packet.get("summary", "") or "").strip()
    if decision and summary_text:
        lines.append("decision: {0} - {1}".format(style_decision_value(decision), summary_text))
    elif decision:
        lines.append("decision: {0}".format(style_decision_value(decision)))
    elif summary_text:
        lines.append(summary_text)
    return lines


def _comma_list(values: Any) -> str:
    if isinstance(values, (list, tuple, set)):
        rendered = ", ".join(str(item).strip() for item in values if str(item).strip())
        return rendered or "none"
    text = str(values or "").strip()
    return text or "none"


def _bool_path_summary(item: Dict[str, Any]) -> str:
    return "exists={0} | within_project_root={1} | {2}".format(
        "yes" if bool(item.get("exists", False)) else "no",
        "yes" if bool(item.get("within_project_root", False)) else "no",
        render_human_path_tail(item.get("path", "")) or str(item.get("path", "")).strip(),
    )


def _artifact_rows(artifacts: Dict[str, Any], order: Sequence[str]) -> List[Tuple[str, str]]:
    rows: List[Tuple[str, str]] = []
    for key in order:
        value = artifacts.get(key)
        if value:
            rows.append((key.replace("_", " "), str(value)))
    return rows


def _append_labeled_blocks(lines: List[str], title: str, blocks: Sequence[Tuple[str, List[Tuple[str, Any]]]]) -> None:
    body: List[str] = []
    for index, (label, rows) in enumerate(blocks, start=1):
        if body:
            body.append("")
        body.append("  {0}".format(style_choice_label("{0}. ".format(index), label)))
        body.extend(render_human_kv_rows(rows, indent="    "))
    append_human_section(lines, title, body)
    if lines:
        lines.append("")


def render_markdown_report(report: Dict[str, Any]) -> str:
    project_payload = report.get("project", {}) if isinstance(report.get("project", {}), dict) else {}
    lines = [
        "# Calamum Test Run {0}".format(report.get("run_id", "")),
        "",
        "## Summary",
        "",
        "- Definition: `{0}`".format(report.get("definition_id", "")),
        "- Result: `{0}`".format(report.get("result", "unknown")),
        "- Recorded at (UTC): `{0}`".format(report.get("recorded_at", "")),
        "- Selected lanes: `{0}`".format(", ".join(report.get("selected_lanes", [])) or "none"),
    ]
    if project_payload:
        lines.extend(
            [
                "- Project: `{0}`".format(project_payload.get("project_id", "")),
                "- Domain: `{0}`".format(report.get("domain", "")),
            ]
        )
    if str(report.get("job_id", "")).strip():
        lines.append("- Job: `{0}`".format(report.get("job_id", "")))
    lines.extend(["", "## Lane results", "", "| Lane | Result | Step count |", "| --- | --- | ---: |"])

    for lane in report.get("lanes", []):
        lines.append(
            "| {0} | {1} | {2} |".format(
                lane.get("lane", ""),
                lane.get("result", "unknown"),
                len(lane.get("steps", [])),
            )
        )

    lines.extend(["", "## Step details", ""])
    for lane in report.get("lanes", []):
        steps = lane.get("steps", [])
        lines.append("### {0}".format(lane.get("lane", "")))
        lines.append("")
        if not steps:
            lines.append("- No steps declared for this lane.")
            lines.append("")
            continue
        for step in steps:
            lines.extend(
                [
                    "- Step: `{0}`".format(step.get("id", "")),
                    "- Title: {0}".format(step.get("title", "")),
                    "- Result: `{0}`".format(step.get("result", "unknown")),
                    "- Command: `{0}`".format(step.get("command_display", "")),
                    "- Working directory: `{0}`".format(step.get("cwd", "")),
                    "- Return code: `{0}`".format(step.get("returncode", "planned")),
                    "- Evidence requirements: `{0}`".format(", ".join(step.get("evidence_requirements", [])) or "none"),
                    "- Stdout: `{0}`".format(step.get("stdout_path", "")),
                    "- Stderr: `{0}`".format(step.get("stderr_path", "")),
                    "",
                ]
            )

    artifacts = report.get("artifacts", {})
    if isinstance(artifacts, dict) and artifacts:
        lines.extend(["## Artifacts", ""])
        for key, value in artifacts.items():
            if isinstance(value, list):
                lines.append("- {0}:".format(key))
                for item in value:
                    lines.append("  - `{0}`".format(item))
                continue
            lines.append("- {0}: `{1}`".format(key, value))
        lines.append("")

    next_review_command = str(report.get("next_review_command", "")).strip()
    if next_review_command:
        lines.extend(["## Next review", "", "- `{0}`".format(next_review_command), ""])

    return "\n".join(lines).strip() + "\n"


def render_definition_lines(definition: Dict[str, Any]) -> List[str]:
    lines = _render_header(
        "Calamum test definition",
        {"decision": "go"},
        summary=str(definition.get("summary", "")).strip(),
    )
    append_human_section(
        lines,
        "Summary",
        render_human_kv_rows(
            [
                ("Definition", definition.get("id", "")),
                ("Title", definition.get("title", "")),
                ("Status", definition.get("status", "")),
                ("Category", definition.get("category", "")),
                ("Selector policy", definition.get("selector_policy", "")),
            ]
        ),
    )
    append_human_section(
        lines,
        "Coverage",
        render_human_kv_rows(
            [
                ("Profiles", _comma_list(definition.get("profiles", []))),
                ("Tags", _comma_list(definition.get("tags", []))),
                ("Policy flags", _comma_list(definition.get("policy_flags", []))),
                ("Evidence", _comma_list(definition.get("evidence_requirements", []))),
                ("Default lanes", _comma_list(definition.get("default_lanes", []))),
            ]
        ),
    )
    lanes = definition.get("lanes", {}) if isinstance(definition.get("lanes", {}), dict) else {}
    append_human_section(
        lines,
        "Lanes",
        render_human_kv_rows(
            [
                (lane_name, "{0} step(s)".format(len(lanes.get(lane_name, []) or [])))
                for lane_name in ("pytest", "sandbox_test", "empirical_test")
            ],
            indent="  ",
        ),
    )
    return lines


def render_definition_list(payload: Any) -> List[str]:
    if isinstance(payload, dict):
        rows = list(payload.get("definitions", []) or [])
        packet = payload
    else:
        rows = list(payload or [])
        packet = {"definitions": rows, "decision": "go"}
    project_value = packet.get("project", "")
    if isinstance(project_value, dict):
        project_value = project_value.get("project_id", "") or project_value.get("name", "")
    lines = _render_header(
        "Calamum test definitions",
        packet,
        summary="{0} definition(s) available in the active catalog.".format(len(rows)),
    )
    append_human_section(
        lines,
        "Summary",
        render_human_kv_rows(
            [
                ("Definitions", len(rows)),
                ("Catalog root", render_human_path_tail(packet.get("catalog_root", ""))),
                ("Project", project_value),
            ]
        ),
    )
    blocks: List[Tuple[str, List[Tuple[str, Any]]]] = []
    for item in rows:
        blocks.append(
            (
                str(item.get("id", "") or "definition"),
                [
                    ("Status", item.get("status", "")),
                    ("Category", item.get("category", "")),
                    ("Profiles", _comma_list(item.get("profiles", []))),
                    ("Summary", item.get("summary", "")),
                ],
            )
        )
    _append_labeled_blocks(lines, "Definitions", blocks)
    return lines


def render_project_lines(project: Dict[str, Any]) -> List[str]:
    lines = _render_header(
        "Calamum project context",
        {"decision": "go"},
        summary="Resolved project context for human review.",
    )
    append_human_section(
        lines,
        "Summary",
        render_human_kv_rows(
            [
                ("Project", project.get("project_id", "")),
                ("Name", project.get("name", "")),
                ("Domain", project.get("domain", "")),
                ("Application", project.get("application", "")),
            ]
        ),
    )
    append_human_section(
        lines,
        "Paths",
        render_human_kv_rows(
            [
                ("Project root", project.get("project_root", project.get("root", ""))),
                ("Catalog root", render_human_path_tail(project.get("catalog_root", ""))),
                ("Runs root", render_human_path_tail(project.get("runs_root", ""))),
                ("Reports root", render_human_path_tail(project.get("reports_root", ""))),
                ("Working dir", render_human_path_tail(project.get("working_dir", ""))),
            ]
        ),
    )
    append_human_section(
        lines,
        "Runtime contract",
        render_human_kv_rows(
            [
                ("Aliases", _comma_list(project.get("aliases", []))),
                ("Default lanes", _comma_list(project.get("default_lanes", []))),
                ("Trusted requesters", _comma_list(project.get("trusted_requesters", []))),
            ]
        ),
    )
    path_aliases = project.get("path_aliases", {}) if isinstance(project.get("path_aliases", {}), dict) else {}
    if path_aliases:
        append_human_section(
            lines,
            "Path aliases",
            render_human_kv_rows(sorted(path_aliases.items()), indent="  "),
        )
    return lines


def render_project_list(entries: Iterable[Dict[str, Any]]) -> List[str]:
    rows = list(entries)
    lines = _render_header(
        "Calamum projects",
        {"decision": "go"},
        summary="{0} registered project context(s).".format(len(rows)),
    )
    append_human_section(lines, "Summary", render_human_kv_rows([("Projects", len(rows))]))
    blocks: List[Tuple[str, List[Tuple[str, Any]]]] = []
    for item in rows:
        blocks.append(
            (
                str(item.get("project_id", "") or "project"),
                [
                    ("Name", item.get("name", "")),
                    ("Status", "active" if bool(item.get("active", False)) else "inactive"),
                    ("Root", item.get("root", item.get("project_root", ""))),
                    ("Domain", item.get("domain", "")),
                ],
            )
        )
    _append_labeled_blocks(lines, "Projects", blocks)
    return lines


def render_project_validation(validation: Dict[str, Any]) -> List[str]:
    decision = str(validation.get("decision", "unknown") or "unknown")
    lines = _render_header(
        "Calamum project validation",
        validation,
        summary="Project roots and retained-output paths were checked against the current descriptor.",
    )
    append_human_section(
        lines,
        "Summary",
        render_human_kv_rows(
            [
                ("Decision", style_decision_value(decision)),
                ("Missing markers", _comma_list(validation.get("missing_markers", []))),
                ("Missing paths", _comma_list(validation.get("missing_paths", []))),
            ]
        ),
    )
    append_human_section(
        lines,
        "Resolved paths",
        render_human_kv_rows(
            [
                (str(item.get("name", "") or "path"), _bool_path_summary(item))
                for item in validation.get("resolved_path_checks", [])
                if isinstance(item, dict)
            ],
            indent="  ",
        ),
    )
    return lines


def render_run_summary(report: Dict[str, Any]) -> List[str]:
    lines = _render_header(
        "Calamum retained run",
        report,
        summary="Retained evidence packet for the selected test run.",
    )
    append_human_section(
        lines,
        "Summary",
        render_human_kv_rows(
            [
                ("Run id", report.get("run_id", "")),
                ("Definition", report.get("definition_id", "")),
                ("Result", report.get("result", "unknown")),
                ("Recorded at", report.get("recorded_at", "")),
                ("Project", report.get("project_id", "")),
                ("Job", report.get("job_id", "")),
                ("Selected lanes", _comma_list(report.get("selected_lanes", []))),
            ]
        ),
    )
    lanes = report.get("lanes", []) if isinstance(report.get("lanes", []), list) else []
    if lanes:
        _append_labeled_blocks(
            lines,
            "Lane results",
            [
                (
                    str(lane.get("lane", "") or "lane"),
                    [
                        ("Result", lane.get("result", "unknown")),
                        ("Steps", "{0}".format(len(lane.get("steps", []) or []))),
                    ],
                )
                for lane in lanes
                if isinstance(lane, dict)
            ],
        )
    artifacts = report.get("artifacts", {}) if isinstance(report.get("artifacts", {}), dict) else {}
    append_human_section(
        lines,
        "Artifacts",
        render_human_kv_rows(
            _artifact_rows(
                artifacts,
                ("report_json", "report_md", "manifest_json", "checksums_json", "run_index"),
            )
        ),
    )
    next_review_command = str(report.get("next_review_command", "")).strip()
    if next_review_command:
        append_human_section(lines, "Next review", ["  {0}".format(next_review_command)])
    return lines


def render_runs_list(packet: Dict[str, Any]) -> List[str]:
    runs = list(packet.get("runs", []) or [])
    lines = _render_header(
        "Calamum retained runs",
        packet,
        summary="{0} retained run(s) matched the current query.".format(len(runs)),
    )
    append_human_section(
        lines,
        "Summary",
        render_human_kv_rows(
            [
                ("Runs", len(runs)),
                ("Runs root", render_human_path_tail(packet.get("runs_root", ""))),
            ]
        ),
    )
    _append_labeled_blocks(
        lines,
        "Runs",
        [
            (
                str(item.get("run_id", "") or "run"),
                [
                    ("Result", item.get("result", "unknown")),
                    ("Definition", item.get("definition_id", "")),
                    ("Project", item.get("project_id", "")),
                    ("Job", item.get("job_id", "")),
                    ("Recorded at", item.get("recorded_at", "")),
                ],
            )
            for item in runs
            if isinstance(item, dict)
        ],
    )
    return lines


def render_report_summary(report: Dict[str, Any]) -> List[str]:
    lines = _render_header(
        "Calamum aggregate report",
        report,
        summary="Retained aggregate report for the selected scope.",
    )
    append_human_section(
        lines,
        "Summary",
        render_human_kv_rows(
            [
                ("Report ref", report.get("report_ref", "")),
                ("Scope", report.get("scope", "")),
                ("Target", report.get("target", "")),
                ("Run count", report.get("run_count", 0)),
                ("Generated at", report.get("generated_at", "")),
            ]
        ),
    )
    result_totals = report.get("result_totals", {}) if isinstance(report.get("result_totals", {}), dict) else {}
    if result_totals:
        append_human_section(lines, "Results", render_human_kv_rows(sorted(result_totals.items()), indent="  "))
    runs = report.get("runs", []) if isinstance(report.get("runs", []), list) else []
    if runs:
        _append_labeled_blocks(
            lines,
            "Retained runs",
            [
                (
                    str(item.get("run_id", "") or "run"),
                    [
                        ("Definition", item.get("definition_id", "")),
                        ("Result", item.get("result", "")),
                        ("Recorded at", item.get("recorded_at", "")),
                    ],
                )
                for item in runs[:10]
                if isinstance(item, dict)
            ],
        )
    return lines


def render_reports_list(packet: Dict[str, Any]) -> List[str]:
    reports = list(packet.get("reports", []) or [])
    lines = _render_header(
        "Calamum aggregate reports",
        packet,
        summary="{0} retained aggregate report(s) are available.".format(len(reports)),
    )
    append_human_section(
        lines,
        "Summary",
        render_human_kv_rows(
            [
                ("Reports", len(reports)),
                ("Reports root", render_human_path_tail(packet.get("reports_root", ""))),
            ]
        ),
    )
    _append_labeled_blocks(
        lines,
        "Reports",
        [
            (
                str(item.get("report_ref", "") or "report"),
                [
                    ("Scope", item.get("scope", "")),
                    ("Target", item.get("target", "")),
                    ("Run count", item.get("run_count", 0)),
                    ("Generated at", item.get("generated_at", "")),
                ],
            )
            for item in reports
            if isinstance(item, dict)
        ],
    )
    return lines


def render_no_go_packet(packet: Dict[str, Any]) -> List[str]:
    action = str(packet.get("action", "")).strip()
    title_map = {
        "test-list": "Calamum test definitions",
        "test-show": "Calamum test definition",
        "test-run": "Calamum test run",
        "test-runs-show": "Calamum retained run",
        "test-runs-list": "Calamum retained runs",
        "project-current": "Calamum project context",
        "project-show": "Calamum project context",
        "project-set": "Calamum project context",
        "project-register": "Calamum project context",
        "project-list": "Calamum projects",
        "project-validate": "Calamum project validation",
        "reports-generate": "Calamum aggregate report",
        "reports-show": "Calamum aggregate report",
        "reports-list": "Calamum aggregate reports",
        "cli-error": "Calamum CLI",
    }
    lines = _render_header(
        title_map.get(action, "Calamum CLI"),
        packet,
        summary=str(packet.get("reason", "") or packet.get("summary", "") or "Command blocked.").strip(),
    )
    append_human_section(
        lines,
        "Context",
        render_human_kv_rows(
            [
                ("Action", action),
                ("Definition", packet.get("definition_id", "")),
                ("Run id", packet.get("run_id", "")),
                ("Report ref", packet.get("report_ref", "")),
                ("Project", packet.get("project", packet.get("project_id", ""))),
            ]
        ),
    )
    reasons = packet.get("reasons", []) if isinstance(packet.get("reasons", []), list) else []
    if reasons:
        append_human_section(lines, "Reasons", ["  - {0}".format(str(reason)) for reason in reasons])
    return lines


def render_aggregate_markdown(report: Dict[str, Any]) -> str:
    lines = [
        "# Calamum Aggregate Report {0}".format(report.get("report_ref", "")),
        "",
        "## Summary",
        "",
        "- Scope: `{0}`".format(report.get("scope", "")),
        "- Target: `{0}`".format(report.get("target", "")),
        "- Generated at (UTC): `{0}`".format(report.get("generated_at", "")),
        "- Run count: `{0}`".format(report.get("run_count", 0)),
        "",
        "## Results",
        "",
    ]
    for key, value in sorted((report.get("result_totals", {}) or {}).items()):
        lines.append("- {0}: `{1}`".format(key, value))
    lines.extend(["", "## Lane totals", ""])
    for lane, payload in sorted((report.get("lane_totals", {}) or {}).items()):
        lines.append("### {0}".format(lane))
        lines.append("")
        for key, value in sorted((payload or {}).items()):
            lines.append("- {0}: `{1}`".format(key, value))
        lines.append("")

    lines.extend(["## Retained runs", "", "| Run ID | Definition | Result | Recorded at |", "| --- | --- | --- | --- |"])
    for item in report.get("runs", []):
        lines.append(
            "| {0} | {1} | {2} | {3} |".format(
                item.get("run_id", ""),
                item.get("definition_id", ""),
                item.get("result", ""),
                item.get("recorded_at", ""),
            )
        )
    return "\n".join(lines).strip() + "\n"


def to_json_text(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)
