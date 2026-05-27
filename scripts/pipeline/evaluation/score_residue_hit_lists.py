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


ROOT = Path(__file__).resolve().parents[3]
ANALYSIS_ROOT = ROOT / "analysis"
DEFAULT_TOP_K = [1, 3, 5, 10, 20, 50]
SCORER_VERSION = "0.2.0"


class RunSpec(TypedDict):
    dataset_slug: str
    run_id: str


class HitRow(TypedDict):
    rank_all: int
    rank_non_seed: int | None
    residue: int
    resname: str
    score: float
    is_seed: bool


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


def hit_list_rows(path: Path) -> list[HitRow]:
    rows: list[HitRow] = []
    for row in read_csv_rows(path):
        rows.append(
            {
                "rank_all": int(row["rank_all"]),
                "rank_non_seed": None if row["rank_non_seed"] == "" else int(row["rank_non_seed"]),
                "residue": int(row["residue"]),
                "resname": row["resname"],
                "score": float(row["aci_score"]),
                "is_seed": row["is_seed"] == "yes",
            }
        )
    return rows


def seed_label_metrics(hit_rows: list[HitRow], labels: set[int]) -> dict:
    seed_residues = sorted(int(row["residue"]) for row in hit_rows if row["is_seed"])
    seed_label_overlap = sorted(set(seed_residues) & labels)
    non_seed_residues = sorted(int(row["residue"]) for row in hit_rows if not row["is_seed"])
    non_seed_labels = sorted(set(non_seed_residues) & labels)
    return {
        "seed_residue_count": len(seed_residues),
        "seed_residues": seed_residues,
        "seed_validation_label_overlap_count": len(seed_label_overlap),
        "seed_validation_label_overlap_residues": seed_label_overlap,
        "non_seed_validation_label_count": len(non_seed_labels),
        "non_seed_validation_label_residues": non_seed_labels,
        "validation_labels_excluded_by_seed_fraction": round(len(seed_label_overlap) / len(labels), 8) if labels else 0.0,
    }


def average_precision(ranked: list[dict[str, int | str | float]], positives: set[int]) -> float:
    positive_count = sum(1 for row in ranked if int(row["residue"]) in positives)
    if positive_count == 0:
        return 0.0
    hits = 0
    precision_sum = 0.0
    for index, row in enumerate(ranked, start=1):
        if int(row["residue"]) not in positives:
            continue
        hits += 1
        precision_sum += hits / index
    return precision_sum / positive_count


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


def hotspot_metrics(path: Path, positives: set[int], ranked_population: set[int], top_k_values: list[int]) -> dict | None:
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
                "member_residues": members,
                "validation_hit_count": len(hit_residues),
                "validation_hit_residues": hit_residues,
            }
        )
    top_k = {}
    population_size = len(ranked_population)
    positive_count = len(ranked_population & positives)
    for cutoff in sorted(set(top_k_values)):
        selected = hotspots[: min(cutoff, len(hotspots))]
        covered_members = sorted({residue for hotspot in selected for residue in hotspot["validation_hit_residues"]} & ranked_population)
        selected_members = sorted({residue for hotspot in selected for residue in hotspot["member_residues"]} & ranked_population)
        member_count = len(selected_members)
        expected_random_hits = member_count * positive_count / population_size if population_size else 0.0
        enrichment = len(covered_members) / expected_random_hits if expected_random_hits > 0.0 else None
        precision = len(covered_members) / member_count if member_count else 0.0
        recall = len(covered_members) / positive_count if positive_count else 0.0
        union_count = len(set(selected_members) | (ranked_population & positives))
        jaccard = len(covered_members) / union_count if union_count else 0.0
        top_k[f"top_{cutoff}"] = {
            "effective_k": min(cutoff, len(hotspots)),
            "hotspots_with_hits": sum(1 for hotspot in selected if hotspot["validation_hit_count"] > 0),
            "covered_member_count": member_count,
            "covered_validation_residue_count": len(covered_members),
            "covered_validation_residues": covered_members,
            "expected_random_hits_same_member_count": round(expected_random_hits, 8),
            "enrichment_vs_same_size_random": None if enrichment is None else round(enrichment, 8),
            "member_precision": round(precision, 8),
            "validation_recall": round(recall, 8),
            "jaccard_vs_validation_labels": round(jaccard, 8),
        }
    return {
        "hotspot_count": len(hotspots),
        "top_k": top_k,
        "hotspots": hotspots,
    }


def pathway_metrics(path: Path, positives: set[int], ranked_population: set[int], top_k_values: list[int]) -> dict | None:
    if not path.exists():
        return None
    rows = read_csv_rows(path)
    pathways = []
    for row in rows:
        residues = [int(value) for value in row["residue_path"].split(";") if value]
        hit_residues = sorted(set(residues) & positives & ranked_population)
        pathways.append(
            {
                "pathway_rank": int(row["pathway_rank"]),
                "round_count": int(row["round_count"]),
                "weight": float(row["weight"]),
                "path_length": int(row["path_length"]),
                "residue_path": residues,
                "validation_hit_count": len(hit_residues),
                "validation_hit_residues": hit_residues,
            }
        )
    top_k = {}
    positive_count = len(ranked_population & positives)
    for cutoff in sorted(set(top_k_values)):
        selected = pathways[: min(cutoff, len(pathways))]
        selected_members = sorted({residue for pathway in selected for residue in pathway["residue_path"]} & ranked_population)
        covered = sorted(set(selected_members) & positives)
        recall = len(covered) / positive_count if positive_count else 0.0
        precision = len(covered) / len(selected_members) if selected_members else 0.0
        top_k[f"top_{cutoff}"] = {
            "effective_k": min(cutoff, len(pathways)),
            "covered_member_count": len(selected_members),
            "covered_validation_residue_count": len(covered),
            "covered_validation_residues": covered,
            "member_precision": round(precision, 8),
            "validation_recall": round(recall, 8),
        }
    return {
        "pathway_count": len(pathways),
        "top_k": top_k,
        "pathways": pathways[: min(50, len(pathways))],
    }


def critical_residue_metrics(path: Path, positives: set[int], top_k_values: list[int]) -> dict | None:
    if not path.exists():
        return None
    rows = read_csv_rows(path)
    ranked = [
        {
            "rank": int(row["critical_rank"]),
            "residue": int(row["residue"]),
            "resname": row["resname"],
            "score": float(row["importance"]),
        }
        for row in rows
    ]
    ranked = sorted(ranked, key=lambda item: (int(item["rank"]), int(item["residue"])))
    summary = ranking_summary(ranked, positives, top_k_values)
    summary["critical_residue_count"] = len(ranked)
    return summary


def pairwise_correlation_metrics(path: Path, positives: set[int], ranked_population: set[int], top_k_values: list[int]) -> dict | None:
    if not path.exists():
        return None
    rows = read_csv_rows(path)
    pairs = []
    for row in rows:
        left = int(row["residue_i"])
        right = int(row["residue_j"])
        endpoints = {left, right}
        validation_endpoints = sorted(endpoints & positives & ranked_population)
        pairs.append(
            {
                "pair_rank": int(row["pair_rank"]),
                "residue_i": left,
                "residue_j": right,
                "correlation_score": float(row["correlation_score"]),
                "validation_endpoint_count": len(validation_endpoints),
                "validation_endpoints": validation_endpoints,
                "both_endpoints_validation_contacts": len(validation_endpoints) == 2,
            }
        )
    top_k = {}
    for cutoff in sorted(set(top_k_values)):
        selected = pairs[: min(cutoff, len(pairs))]
        endpoint_hits = sorted({residue for pair in selected for residue in pair["validation_endpoints"]})
        top_k[f"top_{cutoff}"] = {
            "effective_k": min(cutoff, len(pairs)),
            "pairs_with_any_validation_endpoint": sum(1 for pair in selected if pair["validation_endpoint_count"] > 0),
            "pairs_with_both_validation_endpoints": sum(1 for pair in selected if pair["both_endpoints_validation_contacts"]),
            "covered_validation_endpoint_count": len(endpoint_hits),
            "covered_validation_endpoints": endpoint_hits,
        }
    return {
        "pair_count_scored": len(pairs),
        "top_k": top_k,
        "pairs": pairs[: min(50, len(pairs))],
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


def read_connectivity(path: Path) -> dict[int, dict[str, float | int]]:
    metrics: dict[int, dict[str, float | int]] = {}
    for row in read_csv_rows(path):
        left = int(row["residue_i"])
        right = int(row["residue_j"])
        probability = float(row["propagation_probability"])
        left_metrics = metrics.setdefault(
            left,
            {
                "weighted_out_degree": 0.0,
                "weighted_in_degree": 0.0,
                "unweighted_out_degree": 0,
                "unweighted_in_degree": 0,
            },
        )
        right_metrics = metrics.setdefault(
            right,
            {
                "weighted_out_degree": 0.0,
                "weighted_in_degree": 0.0,
                "unweighted_out_degree": 0,
                "unweighted_in_degree": 0,
            },
        )
        left_metrics["weighted_out_degree"] = float(left_metrics["weighted_out_degree"]) + probability
        left_metrics["unweighted_out_degree"] = int(left_metrics["unweighted_out_degree"]) + 1
        right_metrics["weighted_in_degree"] = float(right_metrics["weighted_in_degree"]) + probability
        right_metrics["unweighted_in_degree"] = int(right_metrics["unweighted_in_degree"]) + 1
    return metrics


def graph_neighbors(path: Path) -> dict[int, set[int]]:
    neighbors: dict[int, set[int]] = {}
    for row in read_csv_rows(path):
        left = int(row["residue_i"])
        right = int(row["residue_j"])
        neighbors.setdefault(left, set()).add(right)
        neighbors.setdefault(right, set()).add(left)
    return neighbors


def shortest_seed_distances(neighbors: dict[int, set[int]], seeds: set[int]) -> dict[int, int]:
    distances: dict[int, int] = {}
    frontier = sorted(seed for seed in seeds if seed in neighbors)
    for seed in frontier:
        distances[seed] = 0
    distance = 0
    while frontier:
        distance += 1
        next_frontier: list[int] = []
        for residue in frontier:
            for neighbor in sorted(neighbors.get(residue, set())):
                if neighbor in distances:
                    continue
                distances[neighbor] = distance
                next_frontier.append(neighbor)
        frontier = next_frontier
    return distances


def ranked_from_scores(scores: dict[int, float], names: dict[int, str], reverse: bool = True) -> list[dict[str, int | str | float]]:
    ranked = []
    key = (lambda item: (-item[1], item[0])) if reverse else (lambda item: (item[1], item[0]))
    for rank, (residue, score) in enumerate(sorted(scores.items(), key=key), start=1):
        ranked.append(
            {
                "rank": rank,
                "residue": residue,
                "resname": names[residue],
                "score": score,
            }
        )
    return ranked


def ranking_summary(ranked: list[dict[str, int | str | float]], positives: set[int], top_k_values: list[int]) -> dict:
    auroc_value = auroc(ranked, positives)
    return {
        "top_k": top_k_metrics(ranked, positives, top_k_values),
        "average_precision": round(average_precision(ranked, positives), 8),
        "auroc": None if auroc_value is None else round(auroc_value, 8),
    }


def comparator_metrics(
    connectivity_path: Path,
    hit_rows: list[HitRow],
    positives: set[int],
    top_k_values: list[int],
) -> dict:
    names = {int(row["residue"]): str(row["resname"]) for row in hit_rows if not row["is_seed"]}
    non_seed_residues = set(names)
    seeds = {int(row["residue"]) for row in hit_rows if row["is_seed"]}
    connectivity_metrics = read_connectivity(connectivity_path)
    neighbors = graph_neighbors(connectivity_path)
    seed_distances = shortest_seed_distances(neighbors, seeds)

    weighted_out = {residue: float(connectivity_metrics.get(residue, {}).get("weighted_out_degree", 0.0)) for residue in non_seed_residues}
    weighted_in = {residue: float(connectivity_metrics.get(residue, {}).get("weighted_in_degree", 0.0)) for residue in non_seed_residues}
    weighted_total = {residue: weighted_out[residue] + weighted_in[residue] for residue in non_seed_residues}
    unweighted_total = {
        residue: float(
            int(connectivity_metrics.get(residue, {}).get("unweighted_out_degree", 0))
            + int(connectivity_metrics.get(residue, {}).get("unweighted_in_degree", 0))
        )
        for residue in non_seed_residues
    }
    max_distance = max(seed_distances.values()) if seed_distances else 0
    seed_distance = {residue: float(seed_distances.get(residue, max_distance + 1)) for residue in non_seed_residues}
    return {
        "weighted_out_degree": ranking_summary(ranked_from_scores(weighted_out, names), positives, top_k_values),
        "weighted_in_degree": ranking_summary(ranked_from_scores(weighted_in, names), positives, top_k_values),
        "weighted_total_degree": ranking_summary(ranked_from_scores(weighted_total, names), positives, top_k_values),
        "unweighted_total_degree": ranking_summary(ranked_from_scores(unweighted_total, names), positives, top_k_values),
        "nearest_seed_graph_distance": ranking_summary(ranked_from_scores(seed_distance, names, reverse=False), positives, top_k_values),
    }


def score_run(spec: RunSpec, top_k_values: list[int], git_commit: str | None) -> dict:
    dataset_slug = spec["dataset_slug"]
    current_run_dir = run_dir(dataset_slug, spec["run_id"])
    metadata_path = current_run_dir / "method-metadata.json"
    hit_list_path = current_run_dir / "residue-hit-list.csv"
    hotspots_path = current_run_dir / "hotspots.csv"
    pathways_path = current_run_dir / "allosteric-pathways.csv"
    critical_residues_path = current_run_dir / "critical-residues.csv"
    pairwise_correlations_path = current_run_dir / "pairwise-correlations.csv"
    if not metadata_path.exists() or not hit_list_path.exists():
        raise SystemExit(f"missing run outputs under {current_run_dir}")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    labels, labels_by_ligand = validation_residues(dataset_slug)
    ranked = ranked_predictions(hit_list_path)
    hit_rows = hit_list_rows(hit_list_path)
    ranked_population = {int(row["residue"]) for row in ranked}
    positive_count_in_ranked = sum(1 for row in ranked if int(row["residue"]) in labels)
    auroc_value = auroc(ranked, labels)
    metrics = {
        "scoring_status": "scored_against_validation_labels",
        "validation_label_cutoff_A": 8.0,
        "validation_label_count": len(labels),
        "validation_label_residues_by_ligand": labels_by_ligand,
        "seed_label_overlap": seed_label_metrics(hit_rows, labels),
        "ranked_non_seed_residue_count": len(ranked),
        "positive_count_in_ranked_non_seed": positive_count_in_ranked,
        "top_k": top_k_metrics(ranked, labels, top_k_values),
        "average_precision": round(average_precision(ranked, labels), 8),
        "auroc": None if auroc_value is None else round(auroc_value, 8),
        "selected_allosteric_residue": selected_residue_metric(metadata, labels),
        "hotspots": hotspot_metrics(hotspots_path, labels, ranked_population, top_k_values),
        "pathways": pathway_metrics(pathways_path, labels, ranked_population, top_k_values),
        "critical_residues": critical_residue_metrics(critical_residues_path, labels, top_k_values),
        "pairwise_correlations": pairwise_correlation_metrics(pairwise_correlations_path, labels, ranked_population, top_k_values),
        "graph_comparator_baselines": comparator_metrics(
            current_run_dir / "connectivity-matrix.csv",
            hit_rows,
            labels,
            top_k_values,
        ),
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
            "version": SCORER_VERSION,
            "random_seed": None,
            "parameters": {
                "top_k": sorted(set(top_k_values)),
                "validation_label_cutoff_A": 8.0,
                "includes_seed_label_overlap": True,
                "includes_hotspot_same_size_random_enrichment": True,
                "includes_pathway_validation_coverage": True,
                "includes_critical_residue_ranking": True,
                "includes_pairwise_correlation_endpoint_scoring": True,
                "includes_graph_comparator_baselines": True,
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
            "seed_validation_label_overlap_count": metrics["seed_label_overlap"]["seed_validation_label_overlap_count"],
        },
        "verification": {
            "command": " ".join(["python3", "-m", "scripts.pipeline.evaluation.score_residue_hit_lists", *sys.argv[1:]]),
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
