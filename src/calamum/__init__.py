"""Calamum Test package."""

from .api import (
	generate_report,
	get_definition,
	get_project_validation,
	get_registered_projects,
	get_report,
	get_run,
	list_definitions,
	list_reports,
	list_runs,
	register_project_context,
	require_project_context,
	resolve_project_context,
	run_test_definition,
	set_current_project,
)

__all__ = [
	"__version__",
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

__version__ = "0.3.0"
