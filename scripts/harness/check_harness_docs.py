#!/usr/bin/env python3
"""Validate repository-local harness documentation invariants."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, cast


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "AGENTS.md",
    "docs/agent-harness/README.md",
    "docs/agent-harness/navigation/codebase-map.md",
    "docs/agent-harness/navigation/repository-structure-placement-guide.zh-TW.md",
    "docs/agent-harness/workflows/quantum-challenge-harness.zh-TW.md",
    "docs/agent-harness/workflows/harness-operations-loop.zh-TW.md",
    "docs/agent-harness/state/challenge-harness-state.md",
    "docs/agent-harness/schemas/eval-trace.schema.json",
    "docs/agent-harness/research/external-harness-resource-synthesis.zh-TW.md",
    "docs/agent-harness/research/deusyu-harness-engineering-alignment.zh-TW.md",
    "docs/agent-harness/reviews/code-review-checklist.md",
    ".codex/README.md",
    ".githooks/pre-commit",
    ".github/workflows/harness.yml",
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
    "harness-operations-loop.zh-TW.md",
]

OBSOLETE_FILES = [
    "docs/agent-harness/workflows/codex-large-project-harness.zh-TW.md",
]

STALE_PATH_TERMS = [
    "scripts/pipeline/download_allosteric_challenge_rcsb.py",
    "scripts/pipeline/analyze_allosteric_challenge_datasets.py",
    "scripts/pipeline/run_ohm_like_baseline.py",
    "scripts/pipeline/score_residue_hit_lists.py",
    "python3 scripts/pipeline",
    "scripts/download_allosteric_challenge_rcsb.py",
]

DATASET_SLUGS = ["kras_g12c", "bcr_abl1", "cardiac_myosin"]

TRACE_TOP_LEVEL_REQUIRED = {"run_id", "created_at", "dataset_slug", "input", "method", "outputs", "metrics", "verification"}
TRACE_INPUT_REQUIRED = {"pdb_id", "chain_id", "graph_path", "validation_paths_excluded_from_features"}
TRACE_METHOD_REQUIRED = {"name", "version", "parameters"}
TRACE_OUTPUT_REQUIRED = {"connectivity_matrix_path", "hit_list_path"}
TRACE_OUTPUT_ALLOWED = {
    "connectivity_matrix_path",
    "hit_list_path",
    "report_path",
    "hotspots_path",
    "hotspot_assignments_path",
    "pathways_path",
    "critical_residues_path",
    "pairwise_correlations_path",
}
TRACE_VERIFICATION_REQUIRED = {"command", "exit_code"}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fail(message: str) -> None:
    raise SystemExit(f"harness docs check failed: {message}")


def check_required_files() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        fail(f"missing required files: {', '.join(missing)}")


def check_entropy_cleanup() -> None:
    present = [path for path in OBSOLETE_FILES if (ROOT / path).exists()]
    if present:
        fail(f"obsolete harness docs should be removed: {', '.join(present)}")

    scanned_paths = [
        path
        for path in list(ROOT.rglob("*.md")) + list(ROOT.rglob("*.py"))
        if not any(part.startswith(".") for part in path.relative_to(ROOT).parts)
        and "node_modules" not in path.parts
        and "__pycache__" not in path.parts
        and path != Path(__file__).resolve()
    ]
    for path in scanned_paths:
        text = read_text(path)
        for stale_term in STALE_PATH_TERMS:
            if stale_term in text:
                fail(f"{path.relative_to(ROOT)} contains stale path term: {stale_term}")


def check_schema() -> None:
    schema_path = ROOT / "docs/agent-harness/schemas/eval-trace.schema.json"
    schema = json.loads(read_text(schema_path))
    required = set(schema.get("required", []))
    if required != TRACE_TOP_LEVEL_REQUIRED:
        fail(f"eval trace required fields changed: {sorted(required)}")
    enum = schema["properties"]["dataset_slug"]["enum"]
    if enum != DATASET_SLUGS:
        fail(f"dataset slug enum mismatch: {enum}")
    output_properties = set(schema["properties"]["outputs"]["properties"])
    if not TRACE_OUTPUT_ALLOWED.issubset(output_properties):
        fail(f"eval trace output schema missing fields: {sorted(TRACE_OUTPUT_ALLOWED - output_properties)}")


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
        path
        for path in ROOT.rglob("*.md")
        if not any(part.startswith(".") for part in path.relative_to(ROOT).parts)
        and "node_modules" not in path.parts
        and "__pycache__" not in path.parts
        and "data" not in path.parts
    ]
    pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for markdown_path in markdown_paths:
        text = read_text(markdown_path)
        for raw_link in pattern.findall(text):
            link = raw_link.strip("<>").split("#", 1)[0]
            if not link or "://" in link or link.startswith("mailto:"):
                continue
            target = (markdown_path.parent / link).resolve()
            try:
                target.relative_to(ROOT)
            except ValueError:
                fail(f"{markdown_path.relative_to(ROOT)} has out-of-repo link: {raw_link}")
            if not target.exists():
                fail(f"{markdown_path.relative_to(ROOT)} has missing link target: {raw_link}")


def check_hook_setup() -> None:
    makefile = read_text(ROOT / "Makefile")
    if "install-hooks:" not in makefile or "git config core.hooksPath .githooks" not in makefile:
        fail("Makefile missing install-hooks target for repo-local hooks")
    hook = read_text(ROOT / ".githooks/pre-commit")
    if "check_harness_docs.py" not in hook or "git diff --check --cached" not in hook:
        fail(".githooks/pre-commit missing harness docs or diff check gate")
    workflow = read_text(ROOT / ".github/workflows/harness.yml")
    if "make validate" not in workflow:
        fail(".github/workflows/harness.yml missing make validate CI gate")


def check_dataset_slug_consistency() -> None:
    for script_path in [
        ROOT / "scripts/pipeline/data_refresh/download_allosteric_challenge_rcsb.py",
        ROOT / "scripts/pipeline/analysis/analyze_allosteric_challenge_datasets.py",
        ROOT / "scripts/pipeline/baselines/ohm/run_ohm_like_baseline.py",
    ]:
        if not script_path.exists():
            continue
        text = read_text(script_path)
        missing = [slug for slug in DATASET_SLUGS if f'"{slug}"' not in text]
        if missing:
            fail(f"{script_path.relative_to(ROOT)} missing dataset slugs: {', '.join(missing)}")


def require_keys(container: object, keys: set[str], label: str) -> None:
    if not isinstance(container, dict):
        fail(f"{label} must be an object")
    container_dict = cast(dict[str, Any], container)
    missing = keys - set(container_dict)
    if missing:
        fail(f"{label} missing keys: {', '.join(sorted(missing))}")


def check_eval_trace_file(trace_path: Path) -> None:
    trace = json.loads(read_text(trace_path))
    label = str(trace_path.relative_to(ROOT))
    require_keys(trace, TRACE_TOP_LEVEL_REQUIRED, label)
    if trace["dataset_slug"] not in DATASET_SLUGS:
        fail(f"{label} has unknown dataset_slug: {trace['dataset_slug']}")
    require_keys(trace["input"], TRACE_INPUT_REQUIRED, f"{label}.input")
    require_keys(trace["method"], TRACE_METHOD_REQUIRED, f"{label}.method")
    require_keys(trace["outputs"], TRACE_OUTPUT_REQUIRED, f"{label}.outputs")
    require_keys(trace["verification"], TRACE_VERIFICATION_REQUIRED, f"{label}.verification")
    extra_outputs = set(trace["outputs"]) - TRACE_OUTPUT_ALLOWED
    if extra_outputs:
        fail(f"{label}.outputs has unsupported keys: {', '.join(sorted(extra_outputs))}")
    if not trace["input"]["validation_paths_excluded_from_features"]:
        fail(f"{label}.input.validation_paths_excluded_from_features must not be empty")
    for output_key, raw_path in trace["outputs"].items():
        if raw_path is None:
            continue
        output_path = ROOT / raw_path
        if not output_path.exists():
            fail(f"{label}.outputs.{output_key} target missing: {raw_path}")


def check_eval_traces() -> None:
    for trace_path in sorted((ROOT / "analysis").glob("*/runs/*/eval-trace.json")):
        check_eval_trace_file(trace_path)


def main() -> None:
    check_required_files()
    check_entropy_cleanup()
    check_schema()
    check_state_markers()
    check_blueprint_terms()
    check_internal_links()
    check_hook_setup()
    check_dataset_slug_consistency()
    check_eval_traces()
    print("harness docs check passed")


if __name__ == "__main__":
    main()
