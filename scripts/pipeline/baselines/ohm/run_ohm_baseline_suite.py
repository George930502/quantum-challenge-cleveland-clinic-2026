#!/usr/bin/env python3
"""Run Ohm sensitivity configurations and summarize validation scores."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from scripts.pipeline.baselines.ohm.run_ohm_like_baseline import DEFAULT_RANDOM_SEED, float_for_run_id, rel


ROOT = Path(__file__).resolve().parents[4]
ANALYSIS_ROOT = ROOT / "analysis"
DEFAULT_DATASETS = ["kras_g12c", "bcr_abl1"]
DEFAULT_ALPHAS = [1.0, 3.0, 5.0]
DEFAULT_SEED_CUTOFFS = [5.0, 8.0]
DEFAULT_ROUNDS = 1000
SUMMARY_JSON = ANALYSIS_ROOT / "cross_dataset" / "ohm-baseline-suite-summary.json"
SUMMARY_CSV = ANALYSIS_ROOT / "cross_dataset" / "ohm-baseline-suite-summary.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datasets", nargs="+", default=DEFAULT_DATASETS)
    parser.add_argument("--alphas", nargs="+", type=float, default=DEFAULT_ALPHAS)
    parser.add_argument("--seed-cutoffs-a", nargs="+", type=float, default=DEFAULT_SEED_CUTOFFS)
    parser.add_argument("--rounds", type=int, default=DEFAULT_ROUNDS)
    parser.add_argument("--seed", type=int, default=DEFAULT_RANDOM_SEED)
    parser.add_argument("--mode", choices=["custom", "smoke", "primary"], default="custom")
    parser.add_argument(
        "--skip-run",
        action="store_true",
        help="Only rescore and summarize existing run directories for the requested grid.",
    )
    return parser.parse_args()


def run_id(dataset_slug: str, mode: str, rounds: int, alpha: float, seed_cutoff_a: float) -> str:
    return (
        f"ohm_atom_contacts_strict_{mode}_{dataset_slug}_{rounds}r_"
        f"alpha{float_for_run_id(alpha)}_seedcutoff{float_for_run_id(seed_cutoff_a)}a"
    )


def run_command(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def score_report_path(dataset_slug: str, current_run_id: str) -> Path:
    return ANALYSIS_ROOT / dataset_slug / "runs" / current_run_id / "score-report.json"


def read_score_report(dataset_slug: str, current_run_id: str) -> dict:
    path = score_report_path(dataset_slug, current_run_id)
    if not path.exists():
        raise SystemExit(f"missing score report: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def metric_or_none(report: dict, path: list[str]) -> object:
    current: object = report
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def object_as_dict(value: object) -> dict | None:
    return value if isinstance(value, dict) else None


def summary_row(dataset_slug: str, current_run_id: str, alpha: float, seed_cutoff_a: float, report: dict) -> dict[str, object]:
    metrics = report["metrics"]
    top_10 = metrics["top_k"]["top_10"]
    hotspot_top_5 = object_as_dict(metric_or_none(metrics, ["hotspots", "top_k", "top_5"]))
    weighted_degree_top_10 = metric_or_none(
        metrics,
        ["graph_comparator_baselines", "weighted_total_degree", "top_k", "top_10", "hit_count"],
    )
    seed_distance_top_10 = metric_or_none(
        metrics,
        ["graph_comparator_baselines", "nearest_seed_graph_distance", "top_k", "top_10", "hit_count"],
    )
    seed_overlap = metrics["seed_label_overlap"]
    return {
        "dataset_slug": dataset_slug,
        "run_id": current_run_id,
        "alpha": alpha,
        "seed_cutoff_A": seed_cutoff_a,
        "ranked_non_seed_residue_count": metrics["ranked_non_seed_residue_count"],
        "validation_label_count": metrics["validation_label_count"],
        "seed_validation_label_overlap_count": seed_overlap["seed_validation_label_overlap_count"],
        "non_seed_validation_label_count": seed_overlap["non_seed_validation_label_count"],
        "top_10_hit_count": top_10["hit_count"],
        "top_10_expected_random_hits": top_10["expected_random_hits"],
        "top_10_enrichment_vs_random": top_10["enrichment_vs_random"],
        "average_precision": metrics["average_precision"],
        "auroc": metrics["auroc"],
        "selected_residue": metric_or_none(metrics, ["selected_allosteric_residue", "residue"]),
        "selected_is_validation_contact": metric_or_none(metrics, ["selected_allosteric_residue", "is_validation_contact"]),
        "hotspot_top_5_covered_member_count": None if hotspot_top_5 is None else hotspot_top_5["covered_member_count"],
        "hotspot_top_5_validation_hits": None if hotspot_top_5 is None else hotspot_top_5["covered_validation_residue_count"],
        "hotspot_top_5_enrichment_vs_same_size_random": None
        if hotspot_top_5 is None
        else hotspot_top_5["enrichment_vs_same_size_random"],
        "weighted_total_degree_top_10_hits": weighted_degree_top_10,
        "nearest_seed_distance_top_10_hits": seed_distance_top_10,
        "score_report_path": rel(score_report_path(dataset_slug, current_run_id)),
    }


def write_summary(rows: list[dict[str, object]], args: argparse.Namespace) -> None:
    SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "suite": "ohm_alpha_seed_cutoff_sensitivity",
        "parameters": {
            "datasets": args.datasets,
            "alphas": args.alphas,
            "seed_cutoffs_A": args.seed_cutoffs_a,
            "rounds": args.rounds,
            "random_seed": args.seed,
            "mode": args.mode,
            "skip_run": args.skip_run,
        },
        "summary_csv_path": rel(SUMMARY_CSV),
        "rows": rows,
    }
    SUMMARY_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if rows:
        with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)


def main() -> None:
    args = parse_args()
    run_specs = []
    for alpha in args.alphas:
        for seed_cutoff in args.seed_cutoffs_a:
            if not args.skip_run:
                run_command(
                    [
                        "python3",
                        "-m",
                        "scripts.pipeline.baselines.ohm.run_ohm_like_baseline",
                        "--datasets",
                        *args.datasets,
                        "--mode",
                        args.mode,
                        "--rounds",
                        str(args.rounds),
                        "--seed",
                        str(args.seed),
                        "--alpha",
                        str(alpha),
                        "--seed-cutoff-a",
                        str(seed_cutoff),
                    ]
                )
            for dataset_slug in args.datasets:
                current_run_id = run_id(dataset_slug, args.mode, args.rounds, alpha, seed_cutoff)
                run_specs.append((dataset_slug, current_run_id, alpha, seed_cutoff))

    run_command(
        [
            "python3",
            "-m",
            "scripts.pipeline.evaluation.score_residue_hit_lists",
            "--runs",
            *[f"{dataset_slug}:{current_run_id}" for dataset_slug, current_run_id, _alpha, _cutoff in run_specs],
        ]
    )
    rows = [
        summary_row(dataset_slug, current_run_id, alpha, seed_cutoff, read_score_report(dataset_slug, current_run_id))
        for dataset_slug, current_run_id, alpha, seed_cutoff in run_specs
    ]
    write_summary(rows, args)
    print(json.dumps({"summary_json": rel(SUMMARY_JSON), "summary_csv": rel(SUMMARY_CSV), "row_count": len(rows)}, indent=2))


if __name__ == "__main__":
    main()
