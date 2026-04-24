import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .layout import CATALOG_SCHEMA_VERSION, default_catalog_root as layout_default_catalog_root
from .layout import default_runs_root as layout_default_runs_root

CANONICAL_TEST_LANES = ("pytest", "sandbox_test", "empirical_test")
CANONICAL_TEST_STATUSES = ("seed", "active", "experimental", "deprecated", "disabled")
CANONICAL_TEST_CATEGORIES = (
    "adversarial",
    "general",
    "bootstrap",
    "regression",
    "security",
    "performance",
    "integration",
    "compliance",
)
CANONICAL_TEST_PROFILES = ("default", "smoke", "fast", "release", "nightly")
CANONICAL_TEST_TAGS = (
    "adversarial",
    "aggregate",
    "api",
    "auth",
    "catalog",
    "cli",
    "filesystem",
    "project",
    "reporting",
    "retained-evidence",
    "sandbox",
    "signing",
    "smoke",
)
CANONICAL_TEST_POLICY_FLAGS = (
    "containment",
    "deterministic-output",
    "json-first",
    "local-only",
    "privileged-operation",
    "project-aware",
    "release-gate",
    "signed-output",
)
CANONICAL_EVIDENCE_REQUIREMENTS = (
    "checksums_json",
    "manifest_json",
    "manifest_signature",
    "receipt_json",
    "report_json",
    "report_md",
    "report_signature",
    "stderr_capture",
    "stdout_capture",
)
CANONICAL_EXPECTED_ARTIFACTS = (
    "checksums_json",
    "manifest_json",
    "receipt_json",
    "report_json",
    "report_md",
    "stderr",
    "stdout",
)
CANONICAL_SELECTOR_POLICIES = ("exact-name-only",)
CommandType = Union[str, List[str]]


class CatalogError(RuntimeError):
    """Raised when the Calamum test catalog cannot be loaded or interpreted."""


def default_catalog_root() -> Path:
    return layout_default_catalog_root()


def default_runs_root() -> Path:
    return layout_default_runs_root()


def catalog_path(catalog_root: Path) -> Path:
    return Path(catalog_root) / "test_definitions.json"


def load_catalog(catalog_root: Optional[Path] = None) -> Dict[str, Any]:
    root = Path(catalog_root) if catalog_root is not None else default_catalog_root()
    path = catalog_path(root)
    if not path.exists():
        raise CatalogError("Calamum catalog not found: {0}".format(path))

    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    definitions = payload.get("definitions", [])
    if not isinstance(definitions, list):
        raise CatalogError("Calamum catalog definitions must be a list.")

    return {
        "schema_version": str(payload.get("schema_version", CATALOG_SCHEMA_VERSION)),
        "catalog_root": str(root),
        "catalog_path": str(path),
        "definitions": [normalize_definition(item) for item in definitions],
    }


def list_definitions(catalog_root: Optional[Path] = None) -> List[Dict[str, Any]]:
    payload = load_catalog(catalog_root)
    return list(payload.get("definitions", []))


def get_definition(definition_id: str, catalog_root: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    candidate = str(definition_id or "").strip().lower()
    for definition in list_definitions(catalog_root):
        if str(definition.get("id", "")).strip().lower() == candidate:
            return dict(definition)
    return None


def normalize_string_list(
    raw_value: Any,
    *,
    field_name: str = "list",
    allowed_values: Optional[Sequence[str]] = None,
) -> List[str]:
    if raw_value is None:
        return []
    if not isinstance(raw_value, list):
        raise CatalogError("Expected a list of strings.")
    allowed = tuple(str(item or "").strip() for item in list(allowed_values or []) if str(item or "").strip())
    normalized = []
    for item in raw_value:
        text = str(item or "").strip()
        if text and allowed and text not in allowed:
            raise CatalogError(
                "Field {0} contains unsupported value: {1}. Allowed values: {2}".format(
                    field_name,
                    text,
                    ", ".join(allowed),
                )
            )
        if text and text not in normalized:
            normalized.append(text)
    return normalized


def normalize_choice(
    raw_value: Any,
    *,
    field_name: str,
    default_value: str,
    allowed_values: Sequence[str],
) -> str:
    normalized = str(raw_value or default_value).strip() or default_value
    allowed = tuple(str(item or "").strip() for item in list(allowed_values or []) if str(item or "").strip())
    if normalized not in allowed:
        raise CatalogError(
            "Field {0} contains unsupported value: {1}. Allowed values: {2}".format(
                field_name,
                normalized,
                ", ".join(allowed),
            )
        )
    return normalized


def normalize_mapping(raw_value: Any, *, field_name: str) -> Dict[str, str]:
    if raw_value is None:
        return {}
    if not isinstance(raw_value, dict):
        raise CatalogError("Field {0} must be an object.".format(field_name))
    normalized = {}
    for key, value in raw_value.items():
        normalized_key = str(key or "").strip()
        normalized_value = str(value or "").strip()
        if normalized_key and normalized_value:
            normalized[normalized_key] = normalized_value
    return normalized


def normalize_definition(raw_definition: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(raw_definition, dict):
        raise CatalogError("Each test definition must be an object.")

    definition_id = str(raw_definition.get("id", "")).strip()
    if not definition_id:
        raise CatalogError("Each test definition requires a non-empty id.")

    raw_lanes = raw_definition.get("lanes", {})
    if raw_lanes is None:
        raw_lanes = {}
    if not isinstance(raw_lanes, dict):
        raise CatalogError("Definition {0} has an invalid lanes block.".format(definition_id))

    normalized_lanes = {}
    for lane in CANONICAL_TEST_LANES:
        raw_steps = raw_lanes.get(lane, [])
        if raw_steps is None:
            raw_steps = []
        if not isinstance(raw_steps, list):
            raise CatalogError(
                "Definition {0} lane {1} must be a list of steps.".format(definition_id, lane)
            )
        normalized_lanes[lane] = [normalize_step(lane, index, step) for index, step in enumerate(raw_steps, start=1)]

    default_lanes = normalize_default_lanes(raw_definition.get("default_lanes", list(CANONICAL_TEST_LANES)), definition_id)
    return {
        "id": definition_id,
        "title": str(raw_definition.get("title", definition_id)).strip() or definition_id,
        "summary": str(raw_definition.get("summary", "")).strip(),
        "status": normalize_choice(
            raw_definition.get("status", "seed"),
            field_name="status",
            default_value="seed",
            allowed_values=CANONICAL_TEST_STATUSES,
        ),
        "category": normalize_choice(
            raw_definition.get("category", "general"),
            field_name="category",
            default_value="general",
            allowed_values=CANONICAL_TEST_CATEGORIES,
        ),
        "selector_policy": normalize_choice(
            raw_definition.get("selector_policy", "exact-name-only"),
            field_name="selector_policy",
            default_value="exact-name-only",
            allowed_values=CANONICAL_SELECTOR_POLICIES,
        ),
        "profiles": normalize_string_list(
            raw_definition.get("profiles", []),
            field_name="profiles",
            allowed_values=CANONICAL_TEST_PROFILES,
        ),
        "tags": normalize_string_list(
            raw_definition.get("tags", []),
            field_name="tags",
            allowed_values=CANONICAL_TEST_TAGS,
        ),
        "policy_flags": normalize_string_list(
            raw_definition.get("policy_flags", []),
            field_name="policy_flags",
            allowed_values=CANONICAL_TEST_POLICY_FLAGS,
        ),
        "evidence_requirements": normalize_string_list(
            raw_definition.get("evidence_requirements", []),
            field_name="evidence_requirements",
            allowed_values=CANONICAL_EVIDENCE_REQUIREMENTS,
        ),
        "default_lanes": default_lanes,
        "metadata": normalize_mapping(raw_definition.get("metadata", {}), field_name="metadata"),
        "lanes": normalized_lanes,
    }


def normalize_default_lanes(raw_value: Any, definition_id: str) -> List[str]:
    lanes = normalize_string_list(raw_value)
    if not lanes:
        return list(CANONICAL_TEST_LANES)
    normalized = []
    for lane in lanes:
        if lane not in CANONICAL_TEST_LANES:
            raise CatalogError(
                "Definition {0} declares unknown default lane: {1}".format(definition_id, lane)
            )
        if lane not in normalized:
            normalized.append(lane)
    return normalized


def normalize_step(lane: str, index: int, raw_step: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(raw_step, dict):
        raise CatalogError("Lane step {0}:{1} must be an object.".format(lane, index))

    command = normalize_command(raw_step.get("command", []), lane, index)
    step_id = str(raw_step.get("id", "{0}-{1}".format(lane, index))).strip() or "{0}-{1}".format(lane, index)
    title = str(raw_step.get("title", step_id)).strip() or step_id

    return {
        "id": step_id,
        "title": title,
        "command": command,
        "allow_failure": bool(raw_step.get("allow_failure", False)),
        "cwd": str(raw_step.get("cwd", "") or "").strip(),
        "env": normalize_mapping(raw_step.get("env", {}), field_name="env"),
        "shell": bool(raw_step.get("shell", False)),
        "expected_artifacts": normalize_string_list(
            raw_step.get("expected_artifacts", []),
            field_name="expected_artifacts",
            allowed_values=CANONICAL_EXPECTED_ARTIFACTS,
        ),
        "evidence_requirements": normalize_string_list(
            raw_step.get("evidence_requirements", []),
            field_name="evidence_requirements",
            allowed_values=CANONICAL_EVIDENCE_REQUIREMENTS,
        ),
        "policy_flags": normalize_string_list(
            raw_step.get("policy_flags", []),
            field_name="policy_flags",
            allowed_values=CANONICAL_TEST_POLICY_FLAGS,
        ),
        "notes": str(raw_step.get("notes", "") or "").strip(),
    }


def normalize_command(raw_command: Any, lane: str, index: int) -> CommandType:
    if isinstance(raw_command, str):
        command = str(raw_command).strip()
        if not command:
            raise CatalogError("Lane step {0}:{1} requires a non-empty command.".format(lane, index))
        return command

    if isinstance(raw_command, Sequence) and not isinstance(raw_command, (bytes, bytearray)):
        items = [str(part).strip() for part in raw_command if str(part).strip()]
        if len(items) == 0:
            raise CatalogError("Lane step {0}:{1} requires a non-empty command.".format(lane, index))
        return items

    raise CatalogError("Lane step {0}:{1} has an unsupported command format.".format(lane, index))
