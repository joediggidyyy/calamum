import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Tuple

from . import __version__
from .catalog import CatalogError, default_catalog_root, default_runs_root, get_definition, list_definitions
from .layout import (
    CalamumArgumentParser,
    DEFAULT_CATALOG_ROOT_TEXT,
    DEFAULT_REPORTS_ROOT_TEXT,
    DEFAULT_RUNS_ROOT_TEXT,
    render_help_overview,
)
from .projects import (
    ProjectError,
    parse_path_aliases,
    register_project,
    require_active_project,
    require_project,
    resolve_project,
    resolve_active_project,
    set_active_project,
    user_config_root,
    validate_project,
    list_registered_projects,
)
from .render import (
    render_definition_lines,
    render_definition_list,
    render_monitor_capability_list,
    render_no_go_packet,
    render_project_lines,
    render_project_list,
    render_project_validation,
    render_reports_list,
    render_report_summary,
    render_run_summary,
    render_runs_list,
    to_json_text,
)
from .reports import ReportError, default_reports_root, generate_report, get_report, list_reports
from .runner import RunError, get_run, list_runs, run_definition

EXIT_OK = 0
EXIT_INPUT_ERROR = 2
EXIT_EXECUTION_FAILED = 3

DEFINITION_RECORD_DESCRIPTION = (
    "A test definition is a named catalog record that explains what Calamum should show or run, "
    "including lanes, steps, and retained evidence requirements."
)
DEFINITION_ID_HELP = (
    "Exact test definition id from the catalog; use 'calamum test list' to discover ids "
    "(example: seed-cli-smoke)"
)
SHOW_DEFINITION_EXAMPLE = "Example: calamum test show seed-cli-smoke"
RUN_DEFINITION_EXAMPLE = "Example: calamum test run seed-cli-smoke --job local-smoke"


def _configure_parser_sections(
    parser: argparse.ArgumentParser,
    arguments_title: str = "Arguments",
    options_title: str = "General options",
) -> argparse.ArgumentParser:
    parser._positionals.title = arguments_title
    parser._optionals.title = options_title
    return parser


def _set_parent_help(
    parser: argparse.ArgumentParser,
    *,
    usage: str,
    summary: str,
    groups: Sequence[Tuple[str, Sequence[Tuple[str, str]]]],
    examples: Optional[Sequence[str]] = None,
    extra_options: Optional[Sequence[Tuple[str, str]]] = None,
) -> None:
    if hasattr(parser, "set_custom_help_renderer"):
        options = [("-h, --help", "show this help message and exit")]
        if extra_options:
            options.extend(list(extra_options))
        parser.set_custom_help_renderer(
            lambda _: render_help_overview(
                usage=usage,
                summary=summary,
                groups=groups,
                options=options,
                examples=examples,
            )
        )


def _add_json_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", help="Emit machine-readable output")


def _version_text() -> str:
    return "calamum {0}".format(__version__)


def _add_project_namespace(
    parser: argparse.ArgumentParser,
    *,
    usage: str,
    summary: str,
    examples: Sequence[str],
) -> None:
    project_sub = parser.add_subparsers(dest="project_cmd", required=True, parser_class=CalamumArgumentParser, metavar="<command>")
    _set_parent_help(
        parser,
        usage=usage,
        summary=summary,
        groups=[
            ("Registration", (("register", "Register or update a project descriptor."), ("set", "Set the active Calamum project."), ("current", "Show the resolved current project."))),
            ("Inspection", (("validate", "Validate a project descriptor."), ("list", "List locally registered projects."), ("show", "Show one registered project."))),
        ],
        examples=list(examples),
    )

    project_register = _configure_parser_sections(
        project_sub.add_parser(
            "register",
            help="Register a project descriptor",
            description="Register a project descriptor and optional machine-local overlay without crowding the terminal with raw JSON.",
        ),
        arguments_title="Registration options",
    )
    register_identity = project_register.add_argument_group("Identity")
    register_identity.add_argument("--id", dest="project_id", default="", help="Stable project id")
    register_identity.add_argument("--name", default="", help="Human-facing project name")
    register_identity.add_argument("--root", default="", help="Project root directory")
    register_identity.add_argument("--alias", action="append", dest="aliases", help="Additional project alias", default=[])
    register_identity.add_argument("--shape", default="generic", help="Project shape kind")
    register_runtime = project_register.add_argument_group("Runtime roots")
    register_runtime.add_argument("--catalog-root", default=DEFAULT_CATALOG_ROOT_TEXT, help="Project-local catalog root (default: {0})".format(DEFAULT_CATALOG_ROOT_TEXT))
    register_runtime.add_argument("--runs-root", default=DEFAULT_RUNS_ROOT_TEXT, help="Project-local retained runs root (default: {0}; local-only by default)".format(DEFAULT_RUNS_ROOT_TEXT))
    register_runtime.add_argument("--reports-root", default=DEFAULT_REPORTS_ROOT_TEXT, help="Project-local aggregate reports root (default: {0}; local-only by default)".format(DEFAULT_REPORTS_ROOT_TEXT))
    register_runtime.add_argument("--working-dir", default=".", help="Default execution working directory")
    register_contract = project_register.add_argument_group("Contract rules")
    register_contract.add_argument("--path", action="append", default=[], help="Additional path alias using key=value")
    register_contract.add_argument("--require-marker", action="append", default=[], help="Required project marker")
    register_contract.add_argument("--require-path", action="append", default=[], help="Required project-relative path")
    register_local = project_register.add_argument_group("Machine-local overrides")
    register_local.add_argument("--python", default="", help="Machine-local Python executable override")
    register_local.add_argument("--shell", default="", help="Machine-local shell override")
    register_local.add_argument("--env-file", default="", help="Machine-local env file override")
    register_local.add_argument("--trusted-requester", action="append", default=[], help="Allowlisted delegated requester id")
    register_local.add_argument("--application", default="", help="Optional application id metadata")
    register_local.add_argument("--domain", default="general", help="Optional project domain")
    register_flow = project_register.add_argument_group("Interaction")
    register_flow.add_argument("--interactive", action="store_true", help="Prompt for missing values")
    register_flow.add_argument("--no-input", action="store_true", help="Fail rather than prompting for missing values")
    register_flow.add_argument("--set-current", action="store_true", help="Set this project as active after registration")
    register_flow.add_argument("--write-local-override", action="store_true", help="Persist a machine-local overlay record")
    register_flow.add_argument("--force", action="store_true", help="Overwrite an existing descriptor")
    add_config_root_argument(project_register.add_argument_group("Context options"))
    _add_json_argument(project_register.add_argument_group("Output options"))

    project_set = _configure_parser_sections(
        project_sub.add_parser("set", help="Set the active project", description="Set the active Calamum project for later commands."),
        arguments_title="Required arguments",
    )
    project_set.add_argument("project", help="Project id, alias, or descriptor-root path")
    add_config_root_argument(project_set.add_argument_group("Context options"))
    _add_json_argument(project_set.add_argument_group("Output options"))

    project_current = _configure_parser_sections(
        project_sub.add_parser("current", help="Show the current project", description="Show the resolved current Calamum project."),
        arguments_title="Context selectors",
    )
    add_config_root_argument(project_current.add_argument_group("Context options"))
    _add_json_argument(project_current.add_argument_group("Output options"))

    project_validate = _configure_parser_sections(
        project_sub.add_parser("validate", help="Validate a project descriptor", description="Validate a project descriptor and its retained-output path contract."),
        arguments_title="Project selector",
    )
    project_validate.add_argument("project", nargs="?", default="", help="Optional project id, alias, or descriptor-root path")
    add_config_root_argument(project_validate.add_argument_group("Context options"))
    _add_json_argument(project_validate.add_argument_group("Output options"))

    project_list = _configure_parser_sections(
        project_sub.add_parser("list", help="List registered projects", description="List locally registered Calamum project descriptors."),
        arguments_title="Context selectors",
    )
    add_config_root_argument(project_list.add_argument_group("Context options"))
    _add_json_argument(project_list.add_argument_group("Output options"))

    project_show = _configure_parser_sections(
        project_sub.add_parser("show", help="Show one registered project", description="Show one registered Calamum project descriptor."),
        arguments_title="Required arguments",
    )
    project_show.add_argument("project", help="Project id, alias, or descriptor-root path")
    add_config_root_argument(project_show.add_argument_group("Context options"))
    _add_json_argument(project_show.add_argument_group("Output options"))


def _monitor_capability_summary(project_context: Optional[Any]) -> Dict[str, Any]:
    return {
        "decision": "go",
        "action": "monitor-capability-list",
        "summary": "Current monitor-shell scaffold and adapter posture.",
        "monitor_surface_status": "scaffolded",
        "project": project_context.to_payload() if project_context is not None else {},
        "project_context_resolved": bool(project_context is not None),
        "json_noninteractive": True,
        "platform": sys.platform,
        "pyshark_installed": bool(importlib.util.find_spec("pyshark") is not None),
        "adapters": {
            "pnp": "planned",
            "pcap": "planned",
            "session": "planned",
        },
        "canonical_root_commands": ["test", "project", "monitor"],
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        packet = dispatch(args)
    except (CatalogError, RunError, ProjectError, ReportError) as exc:
        payload = {"decision": "no-go", "action": "cli-error", "reason": str(exc)}
        emit(payload, as_json=bool(getattr(args, "json", False)))
        return EXIT_INPUT_ERROR

    emit(packet, as_json=bool(getattr(args, "json", False)))
    return exit_code_for_packet(packet)


def build_parser() -> argparse.ArgumentParser:
    parser = _configure_parser_sections(
        CalamumArgumentParser(
            prog="calamum",
            description="Calamum retained-evidence testing CLI.",
        ),
        options_title="Options",
    )
    parser.add_argument("--version", action="version", version=_version_text(), help="show installed version and exit")
    subcommands = parser.add_subparsers(dest="command", required=True, parser_class=CalamumArgumentParser, metavar="<command>")

    _set_parent_help(
        parser,
        usage="calamum [-h] <command> ...",
        summary="Calamum retained-evidence CLI for test execution, project context, and monitor scaffolding.",
        groups=[("Commands", (("test", "Run and inspect Calamum test surfaces."), ("project", "Register and resolve Calamum project contexts."), ("monitor", "Inspect Calamum monitor scaffolding and capability surfaces.")))],
        examples=["calamum test list", "calamum project current", "calamum monitor capability list"],
        extra_options=[("--version", "show installed version and exit")],
    )

    test = _configure_parser_sections(
        subcommands.add_parser(
            "test",
            help="Run and inspect Calamum test surfaces",
            description="Calamum test workspace for catalog definitions, retained runs, project contexts, and aggregate reports.",
        ),
        options_title="Options",
    )
    test_sub = test.add_subparsers(dest="test_cmd", required=True, parser_class=CalamumArgumentParser, metavar="<command>")
    _set_parent_help(
        test,
        usage="calamum test [-h] <command> ...",
        summary="Use the test namespace to review definitions, execute retained runs, and inspect project/report state without crowding the terminal.",
        groups=[
            ("Definitions", (("list", "List available test definitions."), ("show", "Show one named test definition."), ("run", "Run one named test definition."))),
            ("Retained evidence", (("runs", "Inspect retained test runs."), ("reports", "Generate and inspect aggregate reports."))),
            ("Project context", (("project", "Register and resolve project contexts."),)),
        ],
        examples=["calamum test show seed-cli-smoke", "calamum test run seed-cli-smoke --job local-smoke"],
    )

    test_list = _configure_parser_sections(
        test_sub.add_parser(
            "list",
            help="List test definitions",
            description="List available test definitions from the resolved Calamum catalog.",
        ),
        arguments_title="Catalog selectors",
    )
    test_list_context = test_list.add_argument_group("Catalog options")
    add_catalog_root_argument(test_list_context)
    add_project_selector_argument(test_list_context)
    add_config_root_argument(test_list_context)
    _add_json_argument(test_list.add_argument_group("Output options"))

    test_show = _configure_parser_sections(
        test_sub.add_parser(
            "show",
            help="Show one test definition",
            description="Show one test definition from the catalog. " + DEFINITION_RECORD_DESCRIPTION,
            epilog=SHOW_DEFINITION_EXAMPLE,
        ),
        arguments_title="Required arguments",
    )
    add_definition_argument(test_show)
    test_show_context = test_show.add_argument_group("Catalog options")
    add_catalog_root_argument(test_show_context)
    add_project_selector_argument(test_show_context)
    add_config_root_argument(test_show_context)
    _add_json_argument(test_show.add_argument_group("Output options"))

    test_run = _configure_parser_sections(
        test_sub.add_parser(
            "run",
            help="Run one test definition",
            description="Run one test definition from the catalog. " + DEFINITION_RECORD_DESCRIPTION,
            epilog=RUN_DEFINITION_EXAMPLE,
        ),
        arguments_title="Required arguments",
    )
    add_definition_argument(test_run)
    test_run_exec = test_run.add_argument_group("Execution options")
    test_run_exec.add_argument(
        "--lane",
        dest="lanes",
        action="append",
        choices=["pytest", "sandbox_test", "empirical_test"],
        help="Restrict execution to one or more canonical test lanes",
    )
    test_run_exec.add_argument("--dry-run", action="store_true", help="Plan the run without executing commands")
    test_run_context = test_run.add_argument_group("Context options")
    add_catalog_root_argument(test_run_context)
    add_runs_root_argument(test_run_context)
    add_project_selector_argument(test_run_context)
    add_config_root_argument(test_run_context)
    test_run_context.add_argument("--job", default="", help="Optional job id to attach to the retained run")
    _add_json_argument(test_run.add_argument_group("Output options"))

    test_runs = _configure_parser_sections(
        test_sub.add_parser(
            "runs",
            help="Inspect retained runs",
            description="Inspect retained Calamum test runs and review one saved run at a time.",
        ),
        options_title="Options",
    )
    test_runs_sub = test_runs.add_subparsers(dest="test_runs_cmd", required=True, parser_class=CalamumArgumentParser, metavar="<command>")
    _set_parent_help(
        test_runs,
        usage="calamum test runs [-h] <command> ...",
        summary="Inspect the retained run ledger or open one concrete run record for evidence review.",
        groups=[("Inspection", (("list", "List retained test runs."), ("show", "Show one retained test run.")))],
        examples=["calamum test runs list", "calamum test runs show 20260424T013142Z-seed-cli-smoke"],
    )

    test_runs_list = _configure_parser_sections(
        test_runs_sub.add_parser("list", help="List retained runs", description="List retained runs from the resolved Calamum runs root."),
        arguments_title="Run selectors",
    )
    test_runs_list_context = test_runs_list.add_argument_group("Context options")
    add_runs_root_argument(test_runs_list_context)
    add_project_selector_argument(test_runs_list_context)
    add_config_root_argument(test_runs_list_context)
    _add_json_argument(test_runs_list.add_argument_group("Output options"))

    test_runs_show = _configure_parser_sections(
        test_runs_sub.add_parser("show", help="Show one retained run", description="Show one retained run packet and its recorded artifacts."),
        arguments_title="Required arguments",
    )
    test_runs_show.add_argument("run_id", help="Exact retained run id to inspect")
    test_runs_show_context = test_runs_show.add_argument_group("Context options")
    add_runs_root_argument(test_runs_show_context)
    add_config_root_argument(test_runs_show_context)
    _add_json_argument(test_runs_show.add_argument_group("Output options"))

    project = _configure_parser_sections(
        test_sub.add_parser(
            "project",
            help="Compatibility alias for top-level project contexts",
            description="Compatibility alias for top-level Calamum project context commands.",
        ),
        options_title="Options",
    )
    _add_project_namespace(
        project,
        usage="calamum test project [-h] <command> ...",
        summary="Compatibility alias for top-level project context management.",
        examples=["calamum project register --id codesentinel-core --root .", "calamum project current"],
    )

    project_root = _configure_parser_sections(
        subcommands.add_parser(
            "project",
            help="Register and resolve project contexts",
            description="Register, inspect, and validate Calamum project contexts used to resolve catalog, runs, and reports roots.",
        ),
        options_title="Options",
    )
    _add_project_namespace(
        project_root,
        usage="calamum project [-h] <command> ...",
        summary="Manage the project context packet that Calamum uses to resolve local catalog, run, and report roots.",
        examples=["calamum project register --id codesentinel-core --root .", "calamum project current"],
    )

    monitor = _configure_parser_sections(
        subcommands.add_parser(
            "monitor",
            help="Inspect monitor scaffolding and capabilities",
            description="Inspect the current Calamum monitor shell, capability surface, and planned adapter posture.",
        ),
        options_title="Options",
    )
    monitor_sub = monitor.add_subparsers(dest="monitor_cmd", required=True, parser_class=CalamumArgumentParser, metavar="<command>")
    _set_parent_help(
        monitor,
        usage="calamum monitor [-h] <command> ...",
        summary="Use the monitor namespace to review native monitor scaffolding and capability signals without exposing backend tool names as primary operator commands.",
        groups=[("Inspection", (("capability", "Inspect monitor-shell capabilities and adapter posture."),))],
        examples=["calamum monitor capability list", "calamum monitor -h"],
    )

    monitor_capability = _configure_parser_sections(
        monitor_sub.add_parser(
            "capability",
            help="Inspect monitor capabilities",
            description="Inspect the current Calamum monitor-shell capability and adapter posture.",
        ),
        options_title="Options",
    )
    monitor_capability_sub = monitor_capability.add_subparsers(dest="monitor_capability_cmd", required=True, parser_class=CalamumArgumentParser, metavar="<command>")
    _set_parent_help(
        monitor_capability,
        usage="calamum monitor capability [-h] <command> ...",
        summary="Review the current monitor-shell scaffold, adapter posture, and project-context resolution status.",
        groups=[("Inspection", (("list", "List current monitor capability signals."),))],
        examples=["calamum monitor capability list", "calamum monitor capability list --json"],
    )

    monitor_capability_list = _configure_parser_sections(
        monitor_capability_sub.add_parser(
            "list",
            help="List monitor capability signals",
            description="List the current Calamum monitor-shell capability signals and adapter posture.",
        ),
        arguments_title="Context selectors",
    )
    add_project_selector_argument(monitor_capability_list.add_argument_group("Context options"))
    add_config_root_argument(monitor_capability_list.add_argument_group("Context options"))
    _add_json_argument(monitor_capability_list.add_argument_group("Output options"))

    reports = _configure_parser_sections(
        test_sub.add_parser(
            "reports",
            help="Generate and inspect aggregate reports",
            description="Generate and inspect retained aggregate reports across job, project, or domain scope.",
        ),
        options_title="Options",
    )
    reports_sub = reports.add_subparsers(dest="reports_cmd", required=True, parser_class=CalamumArgumentParser, metavar="<command>")
    _set_parent_help(
        reports,
        usage="calamum test reports [-h] <command> ...",
        summary="Inspect retained aggregate reports or generate a fresh report packet for the selected scope.",
        groups=[("Inspection", (("list", "List generated aggregate reports."), ("show", "Show one generated aggregate report."))), ("Generation", (("generate", "Generate a job, project, or domain aggregate report."),))],
        examples=["calamum test reports list", "calamum test reports generate --scope project --project codesentinel-core"],
    )

    reports_list = _configure_parser_sections(
        reports_sub.add_parser("list", help="List aggregate reports", description="List retained aggregate reports from the resolved reports root."),
        arguments_title="Report selectors",
    )
    reports_list_context = reports_list.add_argument_group("Context options")
    add_reports_root_argument(reports_list_context)
    add_project_selector_argument(reports_list_context)
    add_config_root_argument(reports_list_context)
    _add_json_argument(reports_list.add_argument_group("Output options"))

    reports_show = _configure_parser_sections(
        reports_sub.add_parser("show", help="Show one aggregate report", description="Show one retained aggregate report by report reference."),
        arguments_title="Required arguments",
    )
    reports_show.add_argument("report_ref", help="Exact report reference to inspect")
    reports_show_context = reports_show.add_argument_group("Context options")
    add_reports_root_argument(reports_show_context)
    add_project_selector_argument(reports_show_context)
    add_config_root_argument(reports_show_context)
    _add_json_argument(reports_show.add_argument_group("Output options"))

    reports_generate = _configure_parser_sections(
        reports_sub.add_parser("generate", help="Generate an aggregate report", description="Generate a job-, project-, or domain-scoped aggregate report from retained run evidence."),
        arguments_title="Generation options",
    )
    generate_scope = reports_generate.add_argument_group("Scope options")
    generate_scope.add_argument("--scope", choices=["job", "project", "domain"], required=True, help="Aggregate scope to build")
    generate_scope.add_argument("--job", default="", help="Job id for job-scoped aggregates")
    generate_scope.add_argument("--domain", default="", help="Domain name for domain-scoped aggregates")
    generate_context = reports_generate.add_argument_group("Context options")
    add_project_selector_argument(generate_context)
    add_runs_root_argument(generate_context)
    add_reports_root_argument(generate_context)
    add_config_root_argument(generate_context)
    generate_signing = reports_generate.add_argument_group("Signing options")
    generate_signing.add_argument("--sign", action="store_true", help="Sign the generated JSON artifacts")
    generate_signing.add_argument("--request-file", default="", help="Optional privileged request JSON payload")
    generate_signing.add_argument("--request-signature-file", default="", help="Detached signature for the privileged request")
    generate_signing.add_argument("--public-key", default="", help="Optional public key for signature verification")
    generate_signing.add_argument("--signing-key", default="", help="Optional private key for aggregate signing")
    generate_signing.add_argument("--no-fallback-signature", action="store_true", help="Require Ed25519 rather than allowing fallback signatures")
    _add_json_argument(reports_generate.add_argument_group("Output options"))

    return parser


def add_catalog_root_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--catalog-root",
        default=None,
        help=(
            "Path to the Calamum test catalog root "
            "(defaults to the resolved project context or ./{0})".format(DEFAULT_CATALOG_ROOT_TEXT)
        ),
    )


def add_definition_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "definition",
        metavar="definition_id",
        help=DEFINITION_ID_HELP,
    )


def add_runs_root_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--runs-root",
        default=None,
        help=(
            "Path to the retained Calamum test runs root "
            "(defaults to the resolved project context or ./{0})".format(DEFAULT_RUNS_ROOT_TEXT)
        ),
    )


def add_reports_root_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--reports-root",
        default=None,
        help=(
            "Path to the retained Calamum aggregate reports root "
            "(defaults to the resolved project context or ./{0})".format(DEFAULT_REPORTS_ROOT_TEXT)
        ),
    )


def add_project_selector_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--project",
        default="",
        help="Project id, alias, or descriptor-root path to resolve before command execution",
    )


def add_config_root_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--config-root",
        default=None,
        help="Override the machine-local Calamum config root used for overlays and active state",
    )


def dispatch(args: argparse.Namespace) -> Dict[str, Any]:
    config_root = Path(args.config_root).resolve() if getattr(args, "config_root", None) else None

    if args.command == "project" or (args.command == "test" and args.test_cmd == "project"):
        if args.project_cmd == "register":
            payload = collect_registration_inputs(args)
            packet = register_project(config_root=config_root, **payload)
            return packet

        if args.project_cmd == "set":
            resolved = require_project(project=args.project, config_root=config_root)
            state_file = set_active_project(resolved.project_id, config_root=config_root)
            return {
                "decision": "go",
                "action": "project-set",
                "project": resolved.to_payload(),
                "state_path": str(state_file),
            }

        if args.project_cmd == "current":
            resolved = resolve_active_project(config_root=config_root)
            if resolved is None:
                resolved = require_project(cwd=Path.cwd(), config_root=config_root)
            return {
                "decision": "go",
                "action": "project-current",
                "project": resolved.to_payload(),
            }

        if args.project_cmd == "validate":
            resolved = require_project(project=args.project or None, config_root=config_root)
            packet = validate_project(resolved)
            packet["action"] = "project-validate"
            return packet

        if args.project_cmd == "list":
            projects = list_registered_projects(config_root=config_root)
            return {
                "decision": "go",
                "action": "project-list",
                "projects": projects,
                "count": len(projects),
                "config_root": str(user_config_root(config_root)),
            }

        if args.project_cmd == "show":
            resolved = require_project(project=args.project, config_root=config_root)
            return {
                "decision": "go",
                "action": "project-show",
                "project": resolved.to_payload(),
            }

    if args.command == "monitor":
        project_context = resolve_project(project=getattr(args, "project", None) or None, config_root=config_root)
        if args.monitor_cmd == "capability" and args.monitor_capability_cmd == "list":
            return _monitor_capability_summary(project_context)
        raise RunError("Unsupported monitor command: {0}".format(args.monitor_cmd))

    if args.command != "test":
        raise RunError("Unsupported command family: {0}".format(args.command))

    project_context = resolve_project(project=getattr(args, "project", None) or None, config_root=config_root)
    catalog_root = resolve_catalog_root(args, project_context)
    runs_root = resolve_runs_root(args, project_context)
    reports_root = resolve_reports_root(args, project_context, runs_root)

    if args.test_cmd == "list":
        definitions = list_definitions(catalog_root)
        return {
            "decision": "go",
            "action": "test-list",
            "catalog_root": str(catalog_root),
            "project": project_context.to_payload() if project_context is not None else {},
            "definitions": definitions,
            "count": len(definitions),
        }

    if args.test_cmd == "show":
        definition = get_definition(args.definition, catalog_root)
        if definition is None:
            return {
                "decision": "no-go",
                "action": "test-show",
                "definition_id": str(args.definition),
                "reason": "unknown_test_definition",
            }
        return {
            "decision": "go",
            "action": "test-show",
            "project": project_context.to_payload() if project_context is not None else {},
            "definition": definition,
        }

    if args.test_cmd == "run":
        definition = get_definition(args.definition, catalog_root)
        if definition is None:
            return {
                "decision": "no-go",
                "action": "test-run",
                "definition_id": str(args.definition),
                "reason": "unknown_test_definition",
            }
        report = run_definition(
            definition=definition,
            runs_root=runs_root,
            requested_lanes=args.lanes,
            dry_run=bool(args.dry_run),
            project_context=project_context,
            job_id=str(args.job or "").strip(),
        )
        report["action"] = "test-run"
        return report

    if args.test_cmd == "runs":
        if args.test_runs_cmd == "list":
            runs = list_runs(runs_root)
            return {
                "decision": "go",
                "action": "test-runs-list",
                "runs_root": str(runs_root),
                "runs": runs,
                "count": len(runs),
            }
        if args.test_runs_cmd == "show":
            report = get_run(args.run_id, runs_root)
            if report is None:
                return {
                    "decision": "no-go",
                    "action": "test-runs-show",
                    "run_id": str(args.run_id),
                    "reason": "run_not_found",
                }
            report["action"] = "test-runs-show"
            return report

    if args.test_cmd == "reports":
        if args.reports_cmd == "list":
            rows = list_reports(reports_root)
            return {
                "decision": "go",
                "action": "reports-list",
                "reports_root": str(reports_root),
                "reports": rows,
                "count": len(rows),
            }
        if args.reports_cmd == "show":
            payload = get_report(args.report_ref, reports_root)
            if payload is None:
                return {
                    "decision": "no-go",
                    "action": "reports-show",
                    "reason": "report_not_found",
                    "report_ref": str(args.report_ref),
                }
            payload["action"] = "reports-show"
            payload["decision"] = "go"
            return payload
        if args.reports_cmd == "generate":
            request_payload = load_optional_json_file(getattr(args, "request_file", ""))
            request_signature = load_optional_text_file(getattr(args, "request_signature_file", ""))
            packet = generate_report(
                scope=args.scope,
                runs_root=runs_root,
                reports_root=reports_root,
                project_context=project_context,
                project_id=str(args.project or (project_context.project_id if project_context is not None else "")).strip(),
                domain=str(args.domain or (project_context.domain if project_context is not None else "")).strip(),
                job_id=str(args.job or "").strip(),
                sign=bool(args.sign),
                request_payload=request_payload,
                request_signature=request_signature,
                public_key_path=str(args.public_key or "").strip() or None,
                signing_key_path=str(args.signing_key or "").strip() or None,
                allow_fallback_signature=not bool(args.no_fallback_signature),
            )
            return packet

    raise RunError("Unsupported test command: {0}".format(args.test_cmd))


def exit_code_for_packet(packet: Dict[str, Any]) -> int:
    if str(packet.get("decision", "")).lower() != "go":
        return EXIT_INPUT_ERROR
    if str(packet.get("result", "")).lower() == "failed":
        return EXIT_EXECUTION_FAILED
    return EXIT_OK


def emit(packet: Dict[str, Any], as_json: bool) -> None:
    if as_json:
        sys.stdout.write(to_json_text(packet) + "\n")
        return

    action = str(packet.get("action", "")).strip()
    if str(packet.get("decision", "")).lower() != "go":
        lines = render_no_go_packet(packet)
    elif action == "test-list":
        lines = render_definition_list(packet)
    elif action == "test-show":
        lines = render_definition_lines(packet.get("definition", {}))
    elif action == "monitor-capability-list":
        lines = render_monitor_capability_list(packet)
    elif action in ("test-run", "test-runs-show"):
        lines = render_run_summary(packet)
    elif action == "test-runs-list":
        lines = render_runs_list(packet)
    elif action in ("project-show", "project-current", "project-register", "project-set"):
        lines = render_project_lines(packet.get("project", {}))
    elif action == "project-list":
        lines = render_project_list(packet.get("projects", []))
    elif action == "project-validate":
        lines = render_project_validation(packet)
    elif action in ("reports-generate", "reports-show"):
        lines = render_report_summary(packet.get("report", packet))
    elif action == "reports-list":
        lines = render_reports_list(packet)
    else:
        lines = render_no_go_packet(packet)

    sys.stdout.write("\n".join(str(line).rstrip() for line in lines) + "\n")


def resolve_catalog_root(args: argparse.Namespace, project_context: Optional[Any]) -> Path:
    if getattr(args, "catalog_root", None):
        return Path(args.catalog_root).resolve()
    if project_context is not None:
        return project_context.catalog_root
    return default_catalog_root().resolve()


def resolve_runs_root(args: argparse.Namespace, project_context: Optional[Any]) -> Path:
    if getattr(args, "runs_root", None):
        return Path(args.runs_root).resolve()
    if project_context is not None:
        return project_context.runs_root
    return default_runs_root().resolve()


def resolve_reports_root(args: argparse.Namespace, project_context: Optional[Any], runs_root: Path) -> Path:
    if getattr(args, "reports_root", None):
        return Path(args.reports_root).resolve()
    return default_reports_root(project_context, runs_root).resolve()


def load_optional_json_file(raw_path: str) -> Optional[Dict[str, Any]]:
    path_text = str(raw_path or "").strip()
    if not path_text:
        return None
    path = Path(path_text).resolve()
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ReportError("Request payload must be a JSON object.")
    return payload


def load_optional_text_file(raw_path: str) -> str:
    path_text = str(raw_path or "").strip()
    if not path_text:
        return ""
    return Path(path_text).resolve().read_text(encoding="utf-8").strip()


def prompt_value(label: str, current: str = "") -> str:
    prompt = "{0}{1}: ".format(label, " [{0}]".format(current) if current else "")
    value = input(prompt).strip()
    return value or current


def collect_registration_inputs(args: argparse.Namespace) -> Dict[str, Any]:
    interactive = bool(args.interactive) and not bool(args.no_input)
    project_id = str(args.project_id or "").strip()
    root = str(args.root or "").strip()
    name = str(args.name or "").strip()
    if interactive:
        project_id = prompt_value("project_id", project_id)
        root = prompt_value("project_root", root or str(Path.cwd()))
        name = prompt_value("name", name or project_id)
    if not project_id:
        raise ProjectError("project_id is required.")
    if not root:
        raise ProjectError("project root is required.")
    return {
        "project_id": project_id,
        "root": Path(root).resolve(),
        "name": name or project_id,
        "aliases": list(args.aliases or []),
        "shape_kind": str(args.shape or "generic").strip() or "generic",
        "catalog_root": str(args.catalog_root or DEFAULT_CATALOG_ROOT_TEXT).strip() or DEFAULT_CATALOG_ROOT_TEXT,
        "runs_root": str(args.runs_root or DEFAULT_RUNS_ROOT_TEXT).strip() or DEFAULT_RUNS_ROOT_TEXT,
        "reports_root": str(args.reports_root or DEFAULT_REPORTS_ROOT_TEXT).strip() or DEFAULT_REPORTS_ROOT_TEXT,
        "working_dir": str(args.working_dir or ".").strip() or ".",
        "required_markers": list(args.require_marker or []),
        "required_paths": list(args.require_path or []),
        "path_aliases": parse_path_aliases(list(args.path or [])),
        "python_executable": str(args.python or "").strip(),
        "shell": str(args.shell or "").strip(),
        "env_file": str(args.env_file or "").strip(),
        "trusted_requesters": list(args.trusted_requester or []),
        "application": str(args.application or "").strip(),
        "domain": str(args.domain or "general").strip() or "general",
        "set_current": bool(args.set_current),
        "write_local_override": bool(args.write_local_override),
        "force": bool(args.force),
    }
