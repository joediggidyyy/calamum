from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

from .layout import DEFAULT_CATALOG_ROOT_TEXT, DEFAULT_REPORTS_ROOT_TEXT, DEFAULT_RUNS_ROOT_TEXT
from .layout import ensure_catalog_bootstrap, ensure_generated_output_layout

DEFAULT_TEST_LANES = ("pytest", "sandbox_test", "empirical_test")
PROJECT_SCHEMA_VERSION = "calamum-project-v1"
OVERLAY_SCHEMA_VERSION = "calamum-project-overlay-v1"
STATE_SCHEMA_VERSION = "calamum-state-v1"


class ProjectError(RuntimeError):
    """Raised when project registration or resolution fails."""


@dataclass
class ResolvedProject:
    project_id: str
    name: str
    project_root: Path
    descriptor_path: Path
    descriptor: Dict[str, Any]
    overlay_path: Optional[Path]
    overlay: Dict[str, Any]
    state_path: Path
    config_root: Path
    aliases: List[str]
    domain: str
    application: str
    shape_kind: str
    catalog_root: Path
    runs_root: Path
    reports_root: Path
    working_dir: Path
    python_executable: str
    shell: str
    env_file: str
    required_markers: List[str]
    required_paths: List[str]
    default_lanes: List[str]
    trusted_requesters: List[str]
    resolved_path_aliases: Dict[str, Path]

    def token_map(self) -> Dict[str, str]:
        tokens = {
            "project_id": self.project_id,
            "project_name": self.name,
            "project_root": str(self.project_root),
            "descriptor_path": str(self.descriptor_path),
            "catalog_root": str(self.catalog_root),
            "runs_root": str(self.runs_root),
            "reports_root": str(self.reports_root),
            "working_dir": str(self.working_dir),
            "python": self.python_executable,
            "shell": self.shell,
            "env_file": self.env_file,
            "domain": self.domain,
            "application": self.application,
        }
        for key, value in self.resolved_path_aliases.items():
            tokens[str(key)] = str(value)
        return tokens

    def to_payload(self) -> Dict[str, Any]:
        return {
            "schema_version": PROJECT_SCHEMA_VERSION,
            "project_id": self.project_id,
            "name": self.name,
            "aliases": list(self.aliases),
            "domain": self.domain,
            "application": self.application,
            "shape_kind": self.shape_kind,
            "project_root": relative_or_absolute_path(self.project_root, self.project_root),
            "descriptor_path": relative_or_absolute_path(self.descriptor_path, self.project_root),
            "overlay_path": relative_or_absolute_path(self.overlay_path, self.project_root) if self.overlay_path else "",
            "catalog_root": relative_or_absolute_path(self.catalog_root, self.project_root),
            "runs_root": relative_or_absolute_path(self.runs_root, self.project_root),
            "reports_root": relative_or_absolute_path(self.reports_root, self.project_root),
            "working_dir": relative_or_absolute_path(self.working_dir, self.project_root),
            "python": self.python_executable,
            "shell": self.shell,
            "env_file": relative_or_absolute_path(Path(self.env_file), self.project_root) if self.env_file else "",
            "required_markers": list(self.required_markers),
            "required_paths": list(self.required_paths),
            "default_lanes": list(self.default_lanes),
            "trusted_requesters": list(self.trusted_requesters),
            "path_aliases": {
                key: relative_or_absolute_path(value, self.project_root)
                for key, value in sorted(self.resolved_path_aliases.items())
            },
            "config_root": str(self.config_root),
            "state_path": str(self.state_path),
        }


def normalize_project_token(value: Any) -> str:
    raw = str(value or "").strip().lower()
    if not raw:
        return ""
    for ch in ("_", "/", "\\", "."):
        raw = raw.replace(ch, "-")
    while "--" in raw:
        raw = raw.replace("--", "-")
    return raw.strip("-")


def user_config_root(config_root: Optional[Path] = None) -> Path:
    if config_root is not None:
        return Path(config_root).resolve()
    override = str(os.environ.get("CALAMUM_CONFIG_ROOT", "")).strip()
    if override:
        return Path(override).expanduser().resolve()
    appdata = str(os.environ.get("APPDATA", "")).strip()
    if appdata:
        return (Path(appdata) / "Calamum").resolve()
    xdg_config = str(os.environ.get("XDG_CONFIG_HOME", "")).strip()
    if xdg_config:
        return (Path(xdg_config) / "calamum").resolve()
    return (Path.home() / ".config" / "calamum").resolve()


def overlays_root(config_root: Optional[Path] = None) -> Path:
    return user_config_root(config_root) / "projects"


def state_path(config_root: Optional[Path] = None) -> Path:
    return user_config_root(config_root) / "state.json"


def overlay_path(project_id: str, config_root: Optional[Path] = None) -> Path:
    token = normalize_project_token(project_id)
    if not token:
        raise ProjectError("Project id is required for overlay lookup.")
    return overlays_root(config_root) / "{0}.local.json".format(token)


def descriptor_path_for_root(project_root: Path) -> Path:
    return Path(project_root).resolve() / ".calamum" / "project.json"


def relative_or_absolute_path(path: Optional[Path], project_root: Path) -> str:
    if path is None:
        return ""
    candidate = Path(path)
    try:
        resolved = candidate.resolve()
        root = Path(project_root).resolve()
        relative = resolved.relative_to(root)
        text = str(relative).replace("\\", "/")
        return text or "."
    except Exception:
        return str(candidate)


def public_path_reference(path: Optional[Path], project_root: Path) -> str:
    if path is None:
        return ""
    candidate = Path(path)
    try:
        resolved = candidate.resolve()
        root = Path(project_root).resolve()
        relative = resolved.relative_to(root)
        text = str(relative).replace("\\", "/")
        return text or "."
    except Exception:
        return candidate.name


def load_json(path: Path, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if not path.exists():
        return dict(default or {})
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ProjectError("Failed to read JSON file: {0} ({1})".format(path, exc))
    if not isinstance(payload, dict):
        raise ProjectError("JSON payload must be an object: {0}".format(path))
    return payload


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def merge_unique(existing: Any, extra: Any) -> List[str]:
    values: List[str] = []
    for group in (existing, extra):
        if isinstance(group, list):
            for item in group:
                text = str(item or "").strip()
                if text and text not in values:
                    values.append(text)
    return values


def parse_path_aliases(pairs: Optional[List[str]]) -> Dict[str, str]:
    aliases: Dict[str, str] = {}
    for raw_item in list(pairs or []):
        text = str(raw_item or "").strip()
        if not text:
            continue
        if "=" not in text:
            raise ProjectError("Path alias entries must use key=value form: {0}".format(text))
        key, value = text.split("=", 1)
        normalized_key = str(key or "").strip()
        normalized_value = str(value or "").strip()
        if not normalized_key or not normalized_value:
            raise ProjectError("Path alias entries must use key=value form: {0}".format(text))
        aliases[normalized_key] = normalized_value
    return aliases


def load_state(config_root: Optional[Path] = None) -> Dict[str, Any]:
    path = state_path(config_root)
    payload = load_json(path, {}) if path.exists() else {}
    return {
        "schema_version": str(payload.get("schema_version", STATE_SCHEMA_VERSION) or STATE_SCHEMA_VERSION),
        "active_project": str(payload.get("active_project", "") or "").strip(),
        "last_project": str(payload.get("last_project", "") or "").strip(),
        "recent_projects": [str(item).strip() for item in list(payload.get("recent_projects", [])) if str(item).strip()],
    }


def save_state(payload: Dict[str, Any], config_root: Optional[Path] = None) -> Path:
    path = state_path(config_root)
    write_json(path, payload)
    return path


def set_active_project(project_id: str, config_root: Optional[Path] = None) -> Path:
    token = str(project_id or "").strip()
    if not token:
        raise ProjectError("Project id is required to set active state.")
    state = load_state(config_root)
    state["schema_version"] = STATE_SCHEMA_VERSION
    state["last_project"] = state.get("active_project", "")
    state["active_project"] = token
    recent = [token]
    for item in list(state.get("recent_projects", [])):
        text = str(item or "").strip()
        if text and text != token and text not in recent:
            recent.append(text)
    state["recent_projects"] = recent[:20]
    return save_state(state, config_root)


def load_overlay(project_id: str, config_root: Optional[Path] = None) -> Tuple[Optional[Path], Dict[str, Any]]:
    path = overlay_path(project_id, config_root)
    if not path.exists():
        return None, {}
    return path, load_json(path, {})


def save_overlay(project_id: str, payload: Dict[str, Any], config_root: Optional[Path] = None) -> Path:
    path = overlay_path(project_id, config_root)
    write_json(path, payload)
    return path


def find_nearest_descriptor(start: Optional[Path] = None) -> Optional[Path]:
    current = Path(start or Path.cwd()).resolve()
    for candidate in [current] + list(current.parents):
        descriptor = descriptor_path_for_root(candidate)
        if descriptor.exists():
            return descriptor
    return None


def list_registered_projects(config_root: Optional[Path] = None) -> List[Dict[str, Any]]:
    overlays_dir = overlays_root(config_root)
    active = str(load_state(config_root).get("active_project", "") or "").strip()
    entries: List[Dict[str, Any]] = []
    if overlays_dir.exists():
        for path in sorted(overlays_dir.glob("*.local.json")):
            payload = load_json(path, {})
            project_id = str(payload.get("project_id", "") or "").strip()
            project_root = str(payload.get("project_root", "") or "").strip()
            if not project_id:
                continue
            descriptor_path = ""
            name = str(payload.get("name", "") or project_id).strip() or project_id
            aliases = [str(item).strip() for item in list(payload.get("aliases", [])) if str(item).strip()]
            domain = str(payload.get("domain", "") or "").strip()
            application = str(payload.get("application", "") or "").strip()
            if project_root:
                descriptor_candidate = descriptor_path_for_root(Path(project_root))
                if descriptor_candidate.exists():
                    descriptor_path = str(descriptor_candidate)
                    descriptor_payload = load_json(descriptor_candidate, {})
                    name = str(descriptor_payload.get("name", "") or name).strip() or name
                    aliases = merge_unique(aliases, descriptor_payload.get("aliases", []))
                    domain = str(descriptor_payload.get("domain", "") or domain).strip()
                    application = str(descriptor_payload.get("application", "") or application).strip()
            entries.append(
                {
                    "project_id": project_id,
                    "name": name,
                    "root": project_root,
                    "aliases": aliases,
                    "domain": domain,
                    "application": application,
                    "overlay_path": str(path),
                    "descriptor_path": descriptor_path,
                    "active": project_id == active,
                }
            )

    deduped: List[Dict[str, Any]] = []
    seen = set()
    for item in entries:
        key = normalize_project_token(item.get("project_id"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def resolve_project_match(entries: List[Dict[str, Any]], alias: str) -> List[Dict[str, Any]]:
    query = normalize_project_token(alias)
    if not query:
        return []

    scored: List[Tuple[int, Dict[str, Any]]] = []
    for project in entries:
        pid = normalize_project_token(project.get("project_id"))
        name = normalize_project_token(project.get("name"))
        root = normalize_project_token(project.get("root"))
        aliases = [normalize_project_token(item) for item in list(project.get("aliases", [])) if normalize_project_token(item)]
        score = -1
        if query and (query == pid or query == name or query == root or query in aliases):
            score = 300
        elif pid.startswith(query) or name.startswith(query) or any(item.startswith(query) for item in aliases):
            score = 200
        elif query in pid or query in name or query in root or any(query in item for item in aliases):
            score = 100
        if score >= 0:
            if bool(project.get("active", False)):
                score += 10
            scored.append((score, project))

    if not scored:
        return []
    scored.sort(key=lambda item: item[0], reverse=True)
    best = scored[0][0]
    return [payload for score, payload in scored if score == best]


def resolve_descriptor_candidate(value: str, cwd: Optional[Path] = None) -> Optional[Path]:
    text = str(value or "").strip()
    if not text:
        return None
    candidate = Path(text)
    if not candidate.is_absolute():
        candidate = (Path(cwd or Path.cwd()).resolve() / candidate).resolve()
    if candidate.is_file() and candidate.name.lower() == "project.json":
        return candidate
    if candidate.is_dir():
        descriptor = descriptor_path_for_root(candidate)
        if descriptor.exists():
            return descriptor
    return None


def _resolve_setting_path(raw_value: Any, project_root: Path, default_value: str) -> Path:
    text = str(raw_value or default_value or "").strip() or default_value
    candidate = Path(text)
    if candidate.is_absolute():
        return candidate.resolve()
    return (project_root / candidate).resolve()


def _load_runtime_env(overlay: Mapping[str, Any]) -> Dict[str, Any]:
    overrides = overlay.get("overrides", {}) if isinstance(overlay.get("overrides", {}), dict) else {}
    runtime = {}
    for key in ("python", "shell", "env_file", "catalog_root", "runs_root", "reports_root", "working_dir"):
        if key in overrides:
            runtime[key] = overrides.get(key)
    return runtime


def _build_resolved_project(descriptor_path: Path, config_root: Optional[Path] = None) -> ResolvedProject:
    descriptor = load_json(descriptor_path, {})
    project_id = str(descriptor.get("project_id", "") or "").strip()
    if not project_id:
        raise ProjectError("Project descriptor is missing project_id: {0}".format(descriptor_path))

    project_root = descriptor_path.parent.parent.resolve()
    root_value = str(descriptor.get("root", ".") or ".").strip() or "."
    root_candidate = Path(root_value)
    if root_candidate.is_absolute():
        project_root = root_candidate.resolve()
    else:
        project_root = (project_root / root_candidate).resolve()

    overlay_file, overlay = load_overlay(project_id, config_root)
    overlay_runtime = _load_runtime_env(overlay)
    calamum = descriptor.get("calamum", {}) if isinstance(descriptor.get("calamum", {}), dict) else {}
    shape = descriptor.get("shape", {}) if isinstance(descriptor.get("shape", {}), dict) else {}
    runtime = calamum.get("runtime", {}) if isinstance(calamum.get("runtime", {}), dict) else {}

    catalog_root = _resolve_setting_path(
        overlay_runtime.get("catalog_root") or calamum.get("catalog_root"),
        project_root,
        DEFAULT_CATALOG_ROOT_TEXT,
    )
    runs_root = _resolve_setting_path(
        overlay_runtime.get("runs_root") or calamum.get("runs_root"),
        project_root,
        DEFAULT_RUNS_ROOT_TEXT,
    )
    reports_root = _resolve_setting_path(
        overlay_runtime.get("reports_root") or calamum.get("reports_root"),
        project_root,
        DEFAULT_REPORTS_ROOT_TEXT,
    )
    working_dir = _resolve_setting_path(overlay_runtime.get("working_dir") or calamum.get("working_dir"), project_root, ".")

    path_aliases = dict(calamum.get("path_aliases", {}) if isinstance(calamum.get("path_aliases", {}), dict) else {})
    overlay_aliases = overlay.get("path_aliases", {}) if isinstance(overlay.get("path_aliases", {}), dict) else {}
    path_aliases.update(overlay_aliases)
    resolved_aliases: Dict[str, Path] = {}
    for key, value in path_aliases.items():
        text = str(value or "").strip()
        if not text:
            continue
        resolved_aliases[str(key)] = _resolve_setting_path(text, project_root, text)

    if "source_root" not in resolved_aliases:
        resolved_aliases["source_root"] = (project_root / "src").resolve()
    if "tests_root" not in resolved_aliases:
        resolved_aliases["tests_root"] = (project_root / "tests").resolve()
    if "artifacts_root" not in resolved_aliases:
        resolved_aliases["artifacts_root"] = (project_root / "dist").resolve()

    python_executable = str(
        overlay_runtime.get("python")
        or runtime.get("python")
        or os.environ.get("CALAMUM_PYTHON", "")
        or sys.executable
    ).strip()
    shell = str(overlay_runtime.get("shell") or runtime.get("shell") or "").strip()
    env_file_value = str(overlay_runtime.get("env_file") or runtime.get("env_file") or "").strip()
    env_file = str(_resolve_setting_path(env_file_value, project_root, env_file_value)) if env_file_value else ""

    required_markers = [str(item).strip() for item in list(calamum.get("required_markers", [])) if str(item).strip()]
    required_paths = [str(item).strip() for item in list(calamum.get("required_paths", [])) if str(item).strip()]
    default_lanes = [str(item).strip() for item in list(calamum.get("default_lanes", DEFAULT_TEST_LANES)) if str(item).strip()]
    if not default_lanes:
        default_lanes = list(DEFAULT_TEST_LANES)

    trusted_requesters = merge_unique(calamum.get("trusted_requesters", []), overlay.get("trusted_requesters", []))
    aliases = merge_unique([project_id], descriptor.get("aliases", []))
    aliases = merge_unique(aliases, overlay.get("aliases", []))

    return ResolvedProject(
        project_id=project_id,
        name=str(descriptor.get("name", "") or project_id).strip() or project_id,
        project_root=project_root,
        descriptor_path=descriptor_path,
        descriptor=descriptor,
        overlay_path=overlay_file,
        overlay=overlay,
        state_path=state_path(config_root),
        config_root=user_config_root(config_root),
        aliases=aliases,
        domain=str(descriptor.get("domain", "") or overlay.get("domain", "") or "general").strip() or "general",
        application=str(descriptor.get("application", "") or overlay.get("application", "") or "").strip(),
        shape_kind=str(shape.get("kind", "generic") or "generic").strip() or "generic",
        catalog_root=catalog_root,
        runs_root=runs_root,
        reports_root=reports_root,
        working_dir=working_dir,
        python_executable=python_executable,
        shell=shell,
        env_file=env_file,
        required_markers=required_markers,
        required_paths=required_paths,
        default_lanes=default_lanes,
        trusted_requesters=trusted_requesters,
        resolved_path_aliases=resolved_aliases,
    )


def resolve_project(project: Optional[str] = None, cwd: Optional[Path] = None, config_root: Optional[Path] = None) -> Optional[ResolvedProject]:
    search_root = Path(cwd or Path.cwd()).resolve()

    if project:
        direct = resolve_descriptor_candidate(project, search_root)
        if direct is not None:
            return _build_resolved_project(direct, config_root)
        matches = resolve_project_match(list_registered_projects(config_root), project)
        if not matches:
            nearest = find_nearest_descriptor(search_root)
            if nearest is not None:
                candidate = _build_resolved_project(nearest, config_root)
                tokens = [normalize_project_token(candidate.project_id), normalize_project_token(candidate.name)]
                tokens.extend([normalize_project_token(item) for item in candidate.aliases])
                if normalize_project_token(project) in [token for token in tokens if token]:
                    return candidate
            raise ProjectError("Unknown project: {0}".format(project))
        descriptor_path = str(matches[0].get("descriptor_path", "") or "").strip()
        root = str(matches[0].get("root", "") or "").strip()
        if descriptor_path:
            return _build_resolved_project(Path(descriptor_path), config_root)
        if root:
            descriptor = descriptor_path_for_root(Path(root))
            if descriptor.exists():
                return _build_resolved_project(descriptor, config_root)
        raise ProjectError("Registered project is missing a readable descriptor: {0}".format(project))

    nearest = find_nearest_descriptor(search_root)
    if nearest is not None:
        return _build_resolved_project(nearest, config_root)

    env_project = str(os.environ.get("CALAMUM_PROJECT", "") or "").strip()
    if env_project:
        return resolve_project(env_project, search_root, config_root)

    state = load_state(config_root)
    active_project = str(state.get("active_project", "") or "").strip()
    if active_project:
        return resolve_project(active_project, search_root, config_root)
    return None


def require_project(project: Optional[str] = None, cwd: Optional[Path] = None, config_root: Optional[Path] = None) -> ResolvedProject:
    resolved = resolve_project(project=project, cwd=cwd, config_root=config_root)
    if resolved is None:
        raise ProjectError("No Calamum project context could be resolved.")
    return resolved


def resolve_active_project(config_root: Optional[Path] = None) -> Optional[ResolvedProject]:
    state = load_state(config_root)
    active_project = str(state.get("active_project", "") or "").strip()
    if not active_project:
        return None
    return resolve_project(project=active_project, config_root=config_root)


def require_active_project(config_root: Optional[Path] = None) -> ResolvedProject:
    resolved = resolve_active_project(config_root=config_root)
    if resolved is None:
        raise ProjectError("No active Calamum project is set.")
    return resolved


def validate_project(resolved: ResolvedProject) -> Dict[str, Any]:
    marker_checks = []
    for marker in resolved.required_markers:
        path = (resolved.project_root / marker).resolve()
        marker_checks.append(
            {
                "marker": marker,
                "exists": path.exists(),
                "path": relative_or_absolute_path(path, resolved.project_root),
            }
        )

    path_checks = []
    for item in resolved.required_paths:
        path = (resolved.project_root / item).resolve()
        path_checks.append(
            {
                "required_path": item,
                "exists": path.exists(),
                "path": relative_or_absolute_path(path, resolved.project_root),
            }
        )

    resolved_path_checks = []
    for name, path in {
        "catalog_root": resolved.catalog_root,
        "runs_root": resolved.runs_root,
        "reports_root": resolved.reports_root,
        "working_dir": resolved.working_dir,
    }.items():
        resolved_path_checks.append(
            {
                "name": name,
                "path": relative_or_absolute_path(path, resolved.project_root),
                "exists": path.exists(),
                "within_project_root": is_within_root(path, resolved.project_root),
            }
        )

    missing_markers = [item["marker"] for item in marker_checks if not item["exists"]]
    missing_paths = [item["required_path"] for item in path_checks if not item["exists"]]
    issues = []
    if missing_markers:
        issues.append("missing_required_markers")
    if missing_paths:
        issues.append("missing_required_paths")

    return {
        "decision": "go" if not issues else "no-go",
        "project": resolved.to_payload(),
        "missing_markers": missing_markers,
        "missing_paths": missing_paths,
        "marker_checks": marker_checks,
        "path_checks": path_checks,
        "resolved_path_checks": resolved_path_checks,
        "issues": issues,
    }


def is_within_root(path: Path, root: Path) -> bool:
    try:
        Path(path).resolve().relative_to(Path(root).resolve())
        return True
    except Exception:
        return False


def register_project(
    *,
    project_id: str,
    root: Path,
    name: str = "",
    aliases: Optional[List[str]] = None,
    shape_kind: str = "generic",
    catalog_root: str = DEFAULT_CATALOG_ROOT_TEXT,
    runs_root: str = DEFAULT_RUNS_ROOT_TEXT,
    reports_root: str = DEFAULT_REPORTS_ROOT_TEXT,
    working_dir: str = ".",
    required_markers: Optional[List[str]] = None,
    required_paths: Optional[List[str]] = None,
    path_aliases: Optional[Dict[str, str]] = None,
    python_executable: str = "",
    shell: str = "",
    env_file: str = "",
    trusted_requesters: Optional[List[str]] = None,
    default_lanes: Optional[List[str]] = None,
    application: str = "",
    domain: str = "general",
    set_current: bool = False,
    write_local_override: bool = False,
    force: bool = False,
    config_root: Optional[Path] = None,
) -> Dict[str, Any]:
    normalized_id = str(project_id or "").strip()
    if not normalized_id:
        raise ProjectError("project_id is required.")
    project_root = Path(root).resolve()
    descriptor_path = descriptor_path_for_root(project_root)
    if descriptor_path.exists() and not force:
        raise ProjectError("Project descriptor already exists: {0}".format(descriptor_path))

    normalized_aliases = merge_unique([normalized_id], aliases or [])
    normalized_markers = [str(item).strip() for item in list(required_markers or []) if str(item).strip()]
    normalized_required_paths = [str(item).strip() for item in list(required_paths or []) if str(item).strip()]
    normalized_default_lanes = [str(item).strip() for item in list(default_lanes or DEFAULT_TEST_LANES) if str(item).strip()]
    if not normalized_default_lanes:
        normalized_default_lanes = list(DEFAULT_TEST_LANES)

    normalized_path_aliases = dict(path_aliases or {})
    descriptor_payload = {
        "schema_version": PROJECT_SCHEMA_VERSION,
        "project_id": normalized_id,
        "name": str(name or normalized_id).strip() or normalized_id,
        "root": ".",
        "aliases": normalized_aliases,
        "domain": str(domain or "general").strip() or "general",
        "application": str(application or "").strip(),
        "shape": {"kind": str(shape_kind or "generic").strip() or "generic"},
        "calamum": {
            "catalog_root": str(catalog_root or DEFAULT_CATALOG_ROOT_TEXT).strip() or DEFAULT_CATALOG_ROOT_TEXT,
            "runs_root": str(runs_root or DEFAULT_RUNS_ROOT_TEXT).strip() or DEFAULT_RUNS_ROOT_TEXT,
            "reports_root": str(reports_root or DEFAULT_REPORTS_ROOT_TEXT).strip() or DEFAULT_REPORTS_ROOT_TEXT,
            "working_dir": str(working_dir or ".").strip() or ".",
            "required_markers": normalized_markers,
            "required_paths": normalized_required_paths,
            "path_aliases": normalized_path_aliases,
            "default_lanes": normalized_default_lanes,
            "trusted_requesters": [
                str(item).strip() for item in list(trusted_requesters or []) if str(item).strip()
            ],
            "runtime": {},
        },
    }
    write_json(descriptor_path, descriptor_payload)

    overlay_payload = {
        "schema_version": OVERLAY_SCHEMA_VERSION,
        "project_id": normalized_id,
        "name": str(name or normalized_id).strip() or normalized_id,
        "project_root": str(project_root),
        "aliases": normalized_aliases,
        "domain": str(domain or "general").strip() or "general",
        "application": str(application or "").strip(),
        "trusted_requesters": [
            str(item).strip() for item in list(trusted_requesters or []) if str(item).strip()
        ],
        "path_aliases": {},
        "overrides": {},
    }
    if python_executable:
        overlay_payload["overrides"]["python"] = str(python_executable).strip()
    if shell:
        overlay_payload["overrides"]["shell"] = str(shell).strip()
    if env_file:
        overlay_payload["overrides"]["env_file"] = str(env_file).strip()
    overlay_file = None
    if write_local_override or overlay_payload["overrides"]:
        overlay_file = save_overlay(normalized_id, overlay_payload, config_root)
    if set_current:
        set_active_project(normalized_id, config_root)

    resolved = _build_resolved_project(descriptor_path, config_root)
    catalog_file = ensure_catalog_bootstrap(project_root, resolved.catalog_root)
    generated_layout = ensure_generated_output_layout(project_root, resolved.runs_root, resolved.reports_root)
    return {
        "decision": "go",
        "action": "project-register",
        "project": resolved.to_payload(),
        "descriptor_path": relative_or_absolute_path(descriptor_path, project_root),
        "overlay_path": str(overlay_file) if overlay_file else "",
        "bootstrap": {
            "catalog_path": relative_or_absolute_path(catalog_file, project_root),
            "generated_root": relative_or_absolute_path(generated_layout["generated_root"], project_root),
            "generated_gitignore": relative_or_absolute_path(generated_layout["gitignore_path"], project_root),
        },
        "set_current": bool(set_current),
    }


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
