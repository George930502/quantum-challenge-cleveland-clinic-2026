#!/usr/bin/env python3
"""Score residue-level method runs against validation ligand contact labels."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict


ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_ROOT = ROOT / "analysis"
DEFAULT_TOP_K = [1, 3, 5, 10, 20, 50]


class RunSpec(TypedDict):
    dataset_slug: str
    run_id: str


DEFAULT_RUNS: list[RunSpec] = [
    {
        "dataset_slug": "kras_g12c",
        "run_id": "ohm_atom_contacts_strict_primary_kras_g12c_10000r_alpha3p0_seedcutoff5p0a",
    },
    {
        "dataset_slug": "bcr_abl1",
        "run_id": "ohm_atom_contacts_strict_primary_bcr_abl1_10000r_alpha3p0_seedcutoff5p0a",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runs",
        nargs="*",
        help="Optional run specs as dataset_slug:run_id. Defaults to current Ohm primary KRAS/BCR-ABL1 runs.",
    )
    parser.add_argument(
        "--top-k",
        nargs="+",
        type=int,
        default=DEFAULT_TOP_K,
        help="Top-k residue cutoffs for hit overlap and enrichment metrics.",
    )
    return parser.parse_args()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def git_commit_or_none() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return result.stdout.strip()


def parse_run_specs(args: argparse.Namespace) -> list[RunSpec]:
    if not args.runs:
        return DEFAULT_RUNS
    specs: list[RunSpec] = []
    for raw_spec in args.runs:
        if ":" not in raw_spec:
            raise SystemExit(f"run spec must be dataset_slug:run_id, got {raw_spec!r}")
        dataset_slug, run_id = raw_spec.split(":", 1)
        specs.append({"dataset_slug": dataset_slug, "run_id": run_id})
    return specs


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validation_label_path(dataset_slug: str) -> Path:
    return ANALYSIS_ROOT / dataset_slug / f"{dataset_slug}-validation-ligand-contact-residues-8a.csv"


def run_dir(dataset_slug: str, run_id: str) -> Path:
    return ANALYSIS_ROOT / dataset_slug / "runs" / run_id


def validation_residues(dataset_slug: str) -> tuple[set[int], dict[str, list[int]]]:
    rows = read_csv_rows(validation_label_path(dataset_slug))
    by_ligand: dict[str, set[int]] = {}
    for row in rows:
        ligand = row["ligand"]
        by_ligand.setdefault(ligand, set()).add(int(row["residue"]))
    all_residues = set()
    output_by_ligand: dict[str, list[int]] = {}
    for ligand, residues in sorted(by_ligand.items()):
        sorted_residues = sorted(residues)
        output_by_ligand[ligand] = sorted_residues
        all_residues.update(sorted_residues)
    return all_residues, output_by_ligand


def ranked_predictions(path: Path) -> list[dict[str, int | str | float]]:
    rows = read_csv_rows(path)
    ranked = []
    for row in rows:
        if row["rank_non_seed"] == "":
            continue
        ranked.append(
            {
                "rank": int(row["rank_non_seed"]),
                "residue": int(row["residue"]),
                "resname": row["resname"],
                "score": float(row["aci_score"]),
            }
        )
    return sorted(ranked, key=lambda item: (int(item["rank"]), int(item["residue"])))


def average_precision(ranked: list[dict[str, int | str | float]], positives: set[int]) -> float:
    if not positives:
        return 0.0
    hits = 0
    precision_sum = 0.0
    for index, row in enumerate(ranked, start=1):
        if int(row["residue"]) not in positives:
            continue
        hits += 1
        precision_sum += hits / index
    return precision_sum / len(positives)


def auroc(ranked: list[dict[str, int | str | float]], positives: set[int]) -> float | None:
    total = len(ranked)
    positive_count = sum(1 for row in ranked if int(row["residue"]) in positives)
    negative_count = total - positive_count
    if positive_count == 0 or negative_count == 0:
        return None
    rank_sum = sum(index for index, row in enumerate(ranked, start=1) if int(row["residue"]) in positives)
    # Ranks are descending by score; convert Mann-Whitney U so higher score is better.
    u_low_score = rank_sum - positive_count * (positive_count + 1) / 2
    u_high_score = positive_count * negative_count - u_low_score
    return u_high_score / (positive_count * negative_count)


def top_k_metrics(ranked: list[dict[str, int | str | float]], positives: set[int], top_k_values: list[int]) -> dict[str, dict]:
    metrics = {}
    population_size = len(ranked)
    positive_count = sum(1 for row in ranked if int(row["residue"]) in positives)
    for top_k in sorted(set(top_k_values)):
        effective_k = min(top_k, population_size)
        top_rows = ranked[:effective_k]
        hit_residues = [int(row["residue"]) for row in top_rows if int(row["residue"]) in positives]
        expected_random_hits = effective_k * positive_count / population_size if population_size else 0.0
        enrichment = len(hit_residues) / expected_random_hits if expected_random_hits > 0.0 else None
        metrics[f"top_{top_k}"] = {
            "effective_k": effective_k,
            "hit_count": len(hit_residues),
            "hit_residues": hit_residues,
            "expected_random_hits": round(expected_random_hits, 8),
            "enrichment_vs_random": None if enrichment is None else round(enrichment, 8),
        }
    return metrics


def hotspot_metrics(path: Path, positives: set[int], top_k_values: list[int]) -> dict | None:
    if not path.exists():
        return None
    rows = read_csv_rows(path)
    hotspots = []
    for row in rows:
        members = [int(value) for value in row["member_residues"].split(";") if value]
        hit_residues = sorted(set(members) & positives)
        hotspots.append(
            {
                "hotspot_rank": int(row["hotspot_rank"]),
                "center_residue": int(row["center_residue"]),
                "center_resname": row["center_resname"],
                "member_count": int(row["member_count"]),
                "validation_hit_count": len(hit_residues),
                "validation_hit_residues": hit_residues,
            }
        )
    top_k = {}
    for cutoff in sorted(set(top_k_values)):
        selected = hotspots[: min(cutoff, len(hotspots))]
        covered = sorted({residue for hotspot in selected for residue in hotspot["validation_hit_residues"]})
        top_k[f"top_{cutoff}"] = {
            "effective_k": min(cutoff, len(hotspots)),
            "hotspots_with_hits": sum(1 for hotspot in selected if hotspot["validation_hit_count"] > 0),
            "covered_validation_residue_count": len(covered),
            "covered_validation_residues": covered,
        }
    return {
        "hotspot_count": len(hotspots),
        "top_k": top_k,
        "hotspots": hotspots,
    }


def selected_residue_metric(metadata: dict, positives: set[int]) -> dict | None:
    selected = metadata.get("selected_allosteric_residue")
    if not selected:
        return None
    residue = int(selected["residue"])
    return {
        "residue": residue,
        "resname": selected["resname"],
        "aci_score": selected["aci_score"],
        "is_validation_contact": residue in positives,
    }


def score_run(spec: RunSpec, top_k_values: list[int], git_commit: str | None) -> dict:
    dataset_slug = spec["dataset_slug"]
    current_run_dir = run_dir(dataset_slug, spec["run_id"])
    metadata_path = current_run_dir / "method-metadata.json"
    hit_list_path = current_run_dir / "residue-hit-list.csv"
    hotspots_path = current_run_dir / "hotspots.csv"
    if not metadata_path.exists() or not hit_list_path.exists():
        raise SystemExit(f"missing run outputs under {current_run_dir}")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    labels, labels_by_ligand = validation_residues(dataset_slug)
    ranked = ranked_predictions(hit_list_path)
    positive_count_in_ranked = sum(1 for row in ranked if int(row["residue"]) in labels)
    auroc_value = auroc(ranked, labels)
    metrics = {
        "scoring_status": "scored_against_validation_labels",
        "validation_label_cutoff_A": 8.0,
        "validation_label_count": len(labels),
        "validation_label_residues_by_ligand": labels_by_ligand,
        "ranked_non_seed_residue_count": len(ranked),
        "positive_count_in_ranked_non_seed": positive_count_in_ranked,
        "top_k": top_k_metrics(ranked, labels, top_k_values),
        "average_precision": round(average_precision(ranked, labels), 8),
        "auroc": None if auroc_value is None else round(auroc_value, 8),
        "selected_allosteric_residue": selected_residue_metric(metadata, labels),
        "hotspots": hotspot_metrics(hotspots_path, labels, top_k_values),
    }
    report = {
        "run_id": spec["run_id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "dataset_slug": dataset_slug,
        "prediction_run_metadata_path": rel(metadata_path),
        "validation_label_path": rel(validation_label_path(dataset_slug)),
        "metrics": metrics,
    }
    report_path = current_run_dir / "score-report.json"
    trace_path = current_run_dir / "score-trace.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    trace = {
        "run_id": f"{spec['run_id']}__score",
        "created_at": report["created_at"],
        "dataset_slug": dataset_slug,
        "input": {
            "pdb_id": metadata["input"]["pdb_id"],
            "chain_id": metadata["input"]["chain_id"],
            "graph_path": metadata["outputs"]["connectivity_matrix_path"],
            "metadata_paths": [metadata["outputs"]["metadata_path"], rel(validation_label_path(dataset_slug))],
            "validation_paths_excluded_from_features": metadata["input"]["validation_paths_excluded_from_features"],
        },
        "method": {
            "name": f"{metadata['method']['name']}__validation_scorer",
            "version": "0.1.0",
            "random_seed": None,
            "parameters": {
                "top_k": sorted(set(top_k_values)),
                "validation_label_cutoff_A": 8.0,
            },
            "coarse_graining": "post-prediction residue-level and hotspot-level validation scoring",
            "hardware_assumption": "classical deterministic scorer; validation labels are read only at scoring time",
        },
        "outputs": {
            "connectivity_matrix_path": metadata["outputs"]["connectivity_matrix_path"],
            "hit_list_path": metadata["outputs"]["hit_list_path"],
            "report_path": rel(report_path),
        },
        "metrics": {
            "baseline_name": metadata["method"]["name"],
            "scoring_status": metrics["scoring_status"],
            "top_5_validation_contact_hits": metrics["top_k"]["top_5"]["hit_count"] if "top_5" in metrics["top_k"] else 0,
            "top_10_validation_contact_hits": metrics["top_k"]["top_10"]["hit_count"] if "top_10" in metrics["top_k"] else 0,
            "random_baseline_mean": metrics["top_k"]["top_10"]["expected_random_hits"] if "top_10" in metrics["top_k"] else 0.0,
            "average_precision": metrics["average_precision"],
            "auroc": metrics["auroc"],
        },
        "verification": {
            "command": " ".join(["python3", "scripts/pipeline/score_residue_hit_lists.py", *sys.argv[1:]]),
            "exit_code": 0,
            "warnings": ["Validation labels are intentionally read only by this scorer."],
        },
    }
    if git_commit:
        trace["git_commit"] = git_commit
    trace_path.write_text(json.dumps(trace, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "dataset_slug": dataset_slug,
        "run_id": spec["run_id"],
        "score_report_path": rel(report_path),
        "score_trace_path": rel(trace_path),
        "top_10_validation_contact_hits": trace["metrics"]["top_10_validation_contact_hits"],
        "auroc": trace["metrics"]["auroc"],
        "average_precision": trace["metrics"]["average_precision"],
    }


def main() -> None:
    args = parse_args()
    git_commit = git_commit_or_none()
    results = [score_run(spec, args.top_k, git_commit) for spec in parse_run_specs(args)]
    print(json.dumps({"scored_runs": results}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
