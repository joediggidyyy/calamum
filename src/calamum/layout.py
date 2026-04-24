from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

CATALOG_SCHEMA_VERSION = "calamum-test-catalog-v2"
DEFAULT_CATALOG_ROOT_REL = Path("catalog")
DEFAULT_GENERATED_ROOT_REL = Path(".calamum") / "generated"
DEFAULT_RUNS_ROOT_REL = DEFAULT_GENERATED_ROOT_REL / "runs"
DEFAULT_REPORTS_ROOT_REL = DEFAULT_GENERATED_ROOT_REL / "reports"

DEFAULT_CATALOG_ROOT_TEXT = DEFAULT_CATALOG_ROOT_REL.as_posix()
DEFAULT_RUNS_ROOT_TEXT = DEFAULT_RUNS_ROOT_REL.as_posix()
DEFAULT_REPORTS_ROOT_TEXT = DEFAULT_REPORTS_ROOT_REL.as_posix()

DEFAULT_GENERATED_GITIGNORE_TEXT = (
    "# Calamum generated runtime outputs (local-only by default)\n"
    "*\n"
    "!.gitignore\n"
)

_ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*m")
_STYLE_CODES = {
    "structure": "36",
    "positive": "32",
    "negative": "31",
    "advisory": "33",
    "muted": "90",
    "brand": "1;96",
    "help_heading": "1;33",
}


def _resolve_base_root(base_root: Optional[Path] = None) -> Path:
    return Path(base_root or Path.cwd()).resolve()


def _terminal_width(default: int = 108) -> int:
    return max(88, min(120, shutil.get_terminal_size((default, 24)).columns))


def supports_color(stream: Optional[Any] = None) -> bool:
    target = stream or sys.stdout
    if os.environ.get("NO_COLOR"):
        return False
    if str(os.environ.get("TERM", "")).strip().lower() == "dumb":
        return False
    try:
        return bool(target.isatty())
    except Exception:
        return False


def strip_ansi(text: Any) -> str:
    return _ANSI_PATTERN.sub("", str(text or ""))


def ljust_ansi(text: Any, width: int) -> str:
    rendered = str(text or "")
    return rendered + (" " * max(0, int(width) - len(strip_ansi(rendered))))


def style_text(text: Any, role: str = "structure") -> str:
    rendered = str(text or "")
    code = _STYLE_CODES.get(str(role or "structure"), _STYLE_CODES["structure"])
    if not supports_color():
        return rendered
    return "\033[{0}m{1}\033[0m".format(code, rendered)


def style_heading(text: Any) -> str:
    return style_text(text, "brand")


def style_help_heading(text: Any) -> str:
    return style_text(text, "help_heading")


def style_decision_value(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in ("go", "ok", "pass", "success", "ready"):
        return style_text(str(value or ""), "positive")
    if normalized in ("no-go", "fail", "failed", "err", "error", "blocked"):
        return style_text(str(value or ""), "negative")
    return style_text(str(value or ""), "advisory")


def style_structural_label(text: Any) -> str:
    return style_text(text, "structure")


def style_choice_label(prefix: str, label: str, role: str = "structure") -> str:
    return "{0}{1}".format(str(prefix or ""), style_text(str(label or ""), role))


def yes_no_text(value: Any) -> str:
    return "yes" if bool(value) else "no"


def render_human_path_tail(value: Any) -> str:
    text = str(value or "").strip().replace("\\", "/")
    if not text:
        return ""
    parts = [part for part in text.split("/") if part]
    if not parts:
        return text
    lowered = [part.lower() for part in parts]
    for anchor in ("local_untracked", ".calamum", "catalog", "runs", "reports"):
        if anchor in lowered:
            return "/".join(parts[lowered.index(anchor) :])
    if len(parts) >= 3:
        return "/".join(parts[-3:])
    if len(parts) >= 2:
        return "/".join(parts[-2:])
    return parts[-1]


def render_human_kv_rows(
    rows: Iterable[Tuple[str, Any]],
    min_label_width: int = 12,
    max_label_width: int = 28,
    indent: str = "",
) -> List[str]:
    cleaned: List[Tuple[str, str]] = []
    for label, value in rows:
        label_text = str(label or "").strip()
        value_text = str(value or "").strip()
        if not label_text or not value_text:
            continue
        cleaned.append((label_text, value_text))
    if not cleaned:
        return []
    label_width = max(min_label_width, min(max_label_width, max(len(label) for label, _ in cleaned)))
    lines: List[str] = []
    for label_text, value_text in cleaned:
        chunks = [chunk.rstrip() for chunk in value_text.splitlines()] or [""]
        lines.append("{0}{1:<{2}} {3}".format(indent, label_text + ":", label_width + 1, chunks[0]))
        continuation_prefix = indent + (" " * (label_width + 2))
        for chunk in chunks[1:]:
            lines.append("{0}{1}".format(continuation_prefix, chunk))
    return lines


def append_human_section(lines: List[str], title: str, body_lines: Iterable[str]) -> None:
    body = [str(line).rstrip() for line in body_lines]
    while body and not body[0].strip():
        body.pop(0)
    while body and not body[-1].strip():
        body.pop()
    if not body:
        return
    if lines and str(lines[-1]).strip():
        lines.append("")
    lines.append(style_heading(str(title or "")))
    lines.extend(body)


def render_help_rows(rows: Sequence[Tuple[str, str]], name_width: int = 18, indent: str = "  ") -> List[str]:
    lines: List[str] = []
    for name, description in rows:
        command = ljust_ansi(style_structural_label(str(name or "")), int(name_width))
        lines.append("{0}{1} {2}".format(indent, command, str(description or "").strip()))
    return lines


def render_help_overview(
    *,
    usage: str,
    summary: str,
    groups: Sequence[Tuple[str, Sequence[Tuple[str, str]]]],
    options: Optional[Sequence[Tuple[str, str]]] = None,
    examples: Optional[Sequence[str]] = None,
) -> str:
    lines: List[str] = ["usage: {0}".format(str(usage or "").strip()), "", str(summary or "").strip()]
    for title, rows in groups:
        if not rows:
            continue
        lines.extend(["", style_help_heading("[{0}]".format(str(title or "").strip())), ""])
        lines.extend(render_help_rows(list(rows)))
    if options:
        lines.extend(["", style_help_heading("[Options]"), ""])
        lines.extend(render_help_rows(list(options), name_width=16))
    if examples:
        lines.extend(["", style_help_heading("[Examples]"), ""])
        for example in examples:
            lines.append("  {0}".format(style_structural_label(str(example or "").strip())))
    return "\n".join(line for line in lines if line is not None).rstrip() + "\n"


class CalamumHelpFormatter(argparse.RawTextHelpFormatter):
    def __init__(self, prog: str) -> None:
        super().__init__(prog, max_help_position=32, width=_terminal_width())


class CalamumArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("formatter_class", CalamumHelpFormatter)
        super().__init__(*args, **kwargs)
        self._custom_help_renderer: Optional[Callable[[argparse.ArgumentParser], str]] = None

    def set_custom_help_renderer(self, renderer: Callable[[argparse.ArgumentParser], str]) -> None:
        self._custom_help_renderer = renderer

    def format_help(self) -> str:
        if self._custom_help_renderer is not None:
            return self._custom_help_renderer(self)
        return super().format_help()


def path_is_within_root(path: Path, root: Path) -> bool:
    try:
        Path(path).resolve().relative_to(Path(root).resolve())
        return True
    except Exception:
        return False


def default_catalog_root(base_root: Optional[Path] = None) -> Path:
    return (_resolve_base_root(base_root) / DEFAULT_CATALOG_ROOT_REL).resolve()


def default_runs_root(base_root: Optional[Path] = None) -> Path:
    return (_resolve_base_root(base_root) / DEFAULT_RUNS_ROOT_REL).resolve()


def default_reports_root(base_root: Optional[Path] = None) -> Path:
    return (_resolve_base_root(base_root) / DEFAULT_REPORTS_ROOT_REL).resolve()


def infer_project_root_from_runtime_root(runtime_root: Path, fallback: Optional[Path] = None) -> Path:
    resolved = Path(runtime_root).resolve()
    normalized_parts = [part.lower() for part in resolved.parts]
    for relative_root in (DEFAULT_RUNS_ROOT_REL, DEFAULT_REPORTS_ROOT_REL):
        tail = [part.lower() for part in relative_root.parts]
        if len(normalized_parts) >= len(tail) and normalized_parts[-len(tail) :] == tail:
            candidate_parts = resolved.parts[: len(resolved.parts) - len(tail)]
            if len(candidate_parts) == 0:
                return _resolve_base_root(fallback)
            return Path(*candidate_parts).resolve()
    return _resolve_base_root(fallback)


def catalog_file(catalog_root: Path) -> Path:
    return Path(catalog_root).resolve() / "test_definitions.json"


def empty_catalog_payload() -> Dict[str, object]:
    return {
        "schema_version": CATALOG_SCHEMA_VERSION,
        "definitions": [],
    }


def ensure_catalog_bootstrap(base_root: Optional[Path] = None, catalog_root: Optional[Path] = None) -> Path:
    root = Path(catalog_root).resolve() if catalog_root is not None else default_catalog_root(base_root)
    root.mkdir(parents=True, exist_ok=True)
    path = catalog_file(root)
    if not path.exists():
        path.write_text(json.dumps(empty_catalog_payload(), indent=2) + "\n", encoding="utf-8")
    return path


def ensure_generated_output_layout(
    base_root: Optional[Path] = None,
    runs_root: Optional[Path] = None,
    reports_root: Optional[Path] = None,
) -> Dict[str, Path]:
    base = _resolve_base_root(base_root)
    resolved_runs = Path(runs_root).resolve() if runs_root is not None else default_runs_root(base)
    resolved_reports = Path(reports_root).resolve() if reports_root is not None else default_reports_root(base)

    resolved_runs.mkdir(parents=True, exist_ok=True)
    resolved_reports.mkdir(parents=True, exist_ok=True)

    generated_root = (base / DEFAULT_GENERATED_ROOT_REL).resolve()
    gitignore_path = generated_root / ".gitignore"
    if path_is_within_root(resolved_runs, generated_root) and path_is_within_root(resolved_reports, generated_root):
        generated_root.mkdir(parents=True, exist_ok=True)
        if not gitignore_path.exists() or gitignore_path.read_text(encoding="utf-8") != DEFAULT_GENERATED_GITIGNORE_TEXT:
            gitignore_path.write_text(DEFAULT_GENERATED_GITIGNORE_TEXT, encoding="utf-8")

    return {
        "runs_root": resolved_runs,
        "reports_root": resolved_reports,
        "generated_root": generated_root,
        "gitignore_path": gitignore_path,
    }
