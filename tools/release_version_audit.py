from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Iterable, List

DEFAULT_TOKENS = [
    "0.2.0",
    "0.3.0",
    "__version__",
    'version =',
    "calamum-test",
    "calamum --version",
]
TEXT_EXTENSIONS = {
    ".md",
    ".toml",
    ".py",
    ".json",
    ".jsonl",
    ".txt",
    ".ini",
    ".cfg",
    ".yml",
    ".yaml",
    ".rst",
}
SKIP_DIRS = {".git", ".venv", ".venv-core", "__pycache__"}


def classify_path(path: Path, repo_root: Path) -> str:
    rel = path.relative_to(repo_root).as_posix()
    if rel.startswith("src/calamum_test.egg-info/") or "/src/calamum_test.egg-info/" in rel or rel.startswith("dist/"):
        return "regenerate"
    if rel.startswith("runs/") or rel.startswith("reports/generated/") or rel.startswith(".calamum/generated/") or "/.calamum/generated/" in rel:
        return "historical"
    if rel.startswith("planning/") or rel.startswith("jobs/"):
        return "supporting"
    return "direct-update"


def should_scan(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    return path.name in {"README", "LICENSE", "PKG-INFO"}


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if should_scan(path):
            yield path


def scan_file(path: Path, tokens: List[str]) -> List[Dict[str, object]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    matches: List[Dict[str, object]] = []
    lines = text.splitlines()
    for line_no, line in enumerate(lines, start=1):
        found = [token for token in tokens if token in line]
        if found:
            matches.append(
                {
                    "line": line_no,
                    "tokens": found,
                    "text": line.strip(),
                }
            )
    return matches


def build_markdown(summary: Dict[str, object]) -> str:
    lines = [
        "# Calamum release version audit",
        "",
        "## Summary",
        "",
        "- Root: `{0}`".format(summary["root"]),
        "- Tokens: `{0}`".format(", ".join(summary["tokens"])),
        "- Files with matches: `{0}`".format(summary["files_with_matches"]),
        "- Total matches: `{0}`".format(summary["total_matches"]),
        "",
        "## Buckets",
        "",
    ]
    bucket_counts = summary["bucket_counts"]
    for bucket in ["direct-update", "regenerate", "historical", "supporting"]:
        lines.append("- {0}: `{1}`".format(bucket, bucket_counts.get(bucket, 0)))
    lines.append("")
    lines.append("## Matches")
    lines.append("")
    for item in summary["files"]:
        lines.append("### `{0}`".format(item["path"]))
        lines.append("")
        lines.append("- bucket: `{0}`".format(item["bucket"]))
        lines.append("- match count: `{0}`".format(item["match_count"]))
        lines.append("")
        for match in item["matches"]:
            lines.append("- line `{0}` | tokens: `{1}` | `{2}`".format(match["line"], ", ".join(match["tokens"]), match["text"]))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Calamum version/name references across the repo.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]), help="Repo root to scan")
    parser.add_argument("--token", action="append", dest="tokens", default=[], help="Additional literal token to search for")
    parser.add_argument("--json-out", default="", help="Optional JSON output path")
    parser.add_argument("--md-out", default="", help="Optional Markdown output path")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    tokens = DEFAULT_TOKENS + [token for token in args.tokens if token]
    files: List[Dict[str, object]] = []
    bucket_counts: Dict[str, int] = {}
    total_matches = 0
    files_with_matches = 0

    for path in iter_files(root):
        matches = scan_file(path, tokens)
        if not matches:
            continue
        files_with_matches += 1
        total_matches += len(matches)
        bucket = classify_path(path, root)
        bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1
        files.append(
            {
                "path": path.relative_to(root).as_posix(),
                "bucket": bucket,
                "match_count": len(matches),
                "matches": matches,
            }
        )

    summary: Dict[str, object] = {
        "root": str(root),
        "tokens": tokens,
        "files_with_matches": files_with_matches,
        "total_matches": total_matches,
        "bucket_counts": bucket_counts,
        "files": files,
    }

    json_text = json.dumps(summary, indent=2) + "\n"
    if args.json_out:
        Path(args.json_out).resolve().write_text(json_text, encoding="utf-8")
    if args.md_out:
        Path(args.md_out).resolve().write_text(build_markdown(summary), encoding="utf-8")
    print(json_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
