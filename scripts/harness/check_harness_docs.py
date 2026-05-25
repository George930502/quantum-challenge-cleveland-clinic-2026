#!/usr/bin/env python3
"""Validate repository-local harness documentation invariants."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "AGENTS.md",
    "docs/agent-harness/README.md",
    "docs/agent-harness/navigation/codebase-map.md",
    "docs/agent-harness/navigation/repository-structure-placement-guide.zh-TW.md",
    "docs/agent-harness/workflows/quantum-challenge-harness.zh-TW.md",
    "docs/agent-harness/state/challenge-harness-state.md",
    "docs/agent-harness/schemas/eval-trace.schema.json",
    "docs/agent-harness/research/external-harness-resource-synthesis.zh-TW.md",
    "docs/agent-harness/reviews/code-review-checklist.md",
    ".codex/README.md",
]

REQUIRED_STATE_MARKERS = [
    "WP-1",
    "WP-2",
    "WP-3",
    "WP-4",
    "WP-5",
]

REQUIRED_BLUEPRINT_TERMS = [
    "blind feature extraction",
    "validation scoring",
    "eval-trace.schema.json",
    "challenge-harness-state.md",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fail(message: str) -> None:
    raise SystemExit(f"harness docs check failed: {message}")


def check_required_files() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        fail(f"missing required files: {', '.join(missing)}")


def check_schema() -> None:
    schema_path = ROOT / "docs/agent-harness/schemas/eval-trace.schema.json"
    schema = json.loads(read_text(schema_path))
    required = set(schema.get("required", []))
    expected = {"run_id", "created_at", "dataset_slug", "input", "method", "outputs", "metrics", "verification"}
    if required != expected:
        fail(f"eval trace required fields changed: {sorted(required)}")
    enum = schema["properties"]["dataset_slug"]["enum"]
    if enum != ["kras_g12c", "bcr_abl1", "cardiac_myosin"]:
        fail(f"dataset slug enum mismatch: {enum}")


def check_state_markers() -> None:
    text = read_text(ROOT / "docs/agent-harness/state/challenge-harness-state.md")
    missing = [marker for marker in REQUIRED_STATE_MARKERS if marker not in text]
    if missing:
        fail(f"challenge-harness-state.md missing work packages: {', '.join(missing)}")


def check_blueprint_terms() -> None:
    text = read_text(ROOT / "docs/agent-harness/workflows/quantum-challenge-harness.zh-TW.md")
    missing = [term for term in REQUIRED_BLUEPRINT_TERMS if term not in text]
    if missing:
        fail(f"quantum harness blueprint missing terms: {', '.join(missing)}")


def check_internal_links() -> None:
    markdown_paths = [
        ROOT / "README.md",
        ROOT / "AGENTS.md",
        ROOT / "docs/AGENTS.md",
        ROOT / "docs/agent-harness/README.md",
        ROOT / "docs/agent-harness/navigation/codebase-map.md",
        ROOT / "docs/agent-harness/navigation/repository-structure-placement-guide.zh-TW.md",
        ROOT / "docs/agent-harness/workflows/quantum-challenge-harness.zh-TW.md",
        ROOT / "docs/agent-harness/research/external-harness-resource-synthesis.zh-TW.md",
        ROOT / "docs/agent-harness/workflows/codex-large-project-harness.zh-TW.md",
    ]
    pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for markdown_path in markdown_paths:
        text = read_text(markdown_path)
        for raw_link in pattern.findall(text):
            link = raw_link.split("#", 1)[0]
            if not link or "://" in link or link.startswith("mailto:"):
                continue
            target = (markdown_path.parent / link).resolve()
            try:
                target.relative_to(ROOT)
            except ValueError:
                fail(f"{markdown_path.relative_to(ROOT)} has out-of-repo link: {raw_link}")
            if not target.exists():
                fail(f"{markdown_path.relative_to(ROOT)} has missing link target: {raw_link}")


def main() -> None:
    check_required_files()
    check_schema()
    check_state_markers()
    check_blueprint_terms()
    check_internal_links()
    print("harness docs check passed")


if __name__ == "__main__":
    main()
