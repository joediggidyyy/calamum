from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from .catalog import get_definition as _get_definition
from .catalog import list_definitions as _list_definitions
from .projects import (
    ResolvedProject,
    list_registered_projects,
    register_project,
    require_project,
    resolve_project,
    set_active_project,
    validate_project,
)
from .reports import generate_report, get_report, list_reports
from .runner import get_run, list_runs, run_definition


def resolve_project_context(project: Optional[str] = None, cwd: Optional[Path] = None) -> Optional[ResolvedProject]:
    return resolve_project(project=project, cwd=cwd)


def require_project_context(project: Optional[str] = None, cwd: Optional[Path] = None) -> ResolvedProject:
    return require_project(project=project, cwd=cwd)


def register_project_context(**kwargs: Any) -> Dict[str, Any]:
    return register_project(**kwargs)


def set_current_project(project: str) -> Path:
    return set_active_project(project)


def get_project_validation(project: Optional[str] = None, cwd: Optional[Path] = None) -> Dict[str, Any]:
    resolved = require_project(project=project, cwd=cwd)
    return validate_project(resolved)


def get_registered_projects() -> List[Dict[str, Any]]:
    return list_registered_projects()


def list_definitions(catalog_root: Optional[Path] = None) -> List[Dict[str, Any]]:
    return _list_definitions(catalog_root)


def get_definition(definition_id: str, catalog_root: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    return _get_definition(definition_id, catalog_root)


def run_test_definition(
    definition: Dict[str, Any],
    *,
    runs_root: Optional[Path] = None,
    requested_lanes: Optional[Sequence[str]] = None,
    dry_run: bool = False,
    project_context: Optional[ResolvedProject] = None,
    job_id: str = "",
) -> Dict[str, Any]:
    return run_definition(
        definition=definition,
        runs_root=runs_root,
        requested_lanes=requested_lanes,
        dry_run=dry_run,
        project_context=project_context,
        job_id=job_id,
    )


__all__ = [
    "generate_report",
    "get_definition",
    "get_project_validation",
    "get_registered_projects",
    "get_report",
    "get_run",
    "list_definitions",
    "list_reports",
    "list_runs",
    "register_project_context",
    "require_project_context",
    "resolve_project_context",
    "run_test_definition",
    "set_current_project",
]
