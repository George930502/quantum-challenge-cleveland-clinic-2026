#!/usr/bin/env python3
"""Run blind Ohm allosteric propagation baselines."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, TypedDict

import numpy as np

from analyze_allosteric_challenge_datasets import DATASETS, heavy_atoms, min_distance, parse_pdb, protein_atoms, rel


ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_ROOT = ROOT / "analysis"
DATA_ROOT = ROOT / "data"

DEFAULT_ALPHA = 3.0
DEFAULT_ATOM_CONTACT_CUTOFF_A = 3.4
DEFAULT_RANDOM_SEED = 20260525
DEFAULT_PRIMARY_ROUNDS = 10000
DEFAULT_SMOKE_ROUNDS = 100
DEFAULT_SEED_CUTOFF_A = 5.0
DEFAULT_HOTSPOT_NEIGHBOR_CUTOFF_A = 4.5
METHOD_VERSION = "0.3.0"
FORMULA_TAG = "wang_2020_eq_3"
TRAVERSAL_TAG = "wang_2020_v_w_vectors"
HOTSPOT_TAG = "wang_2020_4p5a_direction_to_higher_aci"
BACKBONE_ATOMS = {"N", "CA", "C", "O", "OXT"}


class DatasetRunSpec(TypedDict):
    input_pdb: str
    input_chain: str
    seed_ligands: list[str]
    excluded_input_ligands: list[str]
    strict_scoring_ready: bool
    note: str


RUN_SPECS: dict[str, DatasetRunSpec] = {
    "kras_g12c": {
        "input_pdb": "4OBE",
        "input_chain": "A",
        "seed_ligands": ["GDP", "MG"],
        "excluded_input_ligands": [],
        "strict_scoring_ready": True,
        "note": "KRAS strict run uses input GDP/MG active-site contacts as the perturbation seed.",
    },
    "bcr_abl1": {
        "input_pdb": "1OPL",
        "input_chain": "A",
        "seed_ligands": ["P16"],
        "excluded_input_ligands": ["MYR"],
        "strict_scoring_ready": True,
        "note": "BCR-ABL1 strict run uses input P16 ATP-site contacts and excludes input MYR from the primary benchmark.",
    },
    "cardiac_myosin": {
        "input_pdb": "5TBY",
        "input_chain": "A",
        "seed_ligands": [],
        "excluded_input_ligands": [],
        "strict_scoring_ready": False,
        "note": "Cardiac Myosin has no strict small-molecule active-site seed in the MVP; outputs are exploratory only.",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--datasets",
        nargs="+",
        choices=sorted(RUN_SPECS),
        default=["kras_g12c", "bcr_abl1"],
        help="Dataset slugs to run. Defaults to strict-scoring-ready KRAS and BCR-ABL1.",
    )
    parser.add_argument("--rounds", type=int, default=DEFAULT_PRIMARY_ROUNDS)
    parser.add_argument("--seed", type=int, default=DEFAULT_RANDOM_SEED)
    parser.add_argument("--alpha", type=float, default=DEFAULT_ALPHA)
    parser.add_argument("--atom-contact-cutoff-a", type=float, default=DEFAULT_ATOM_CONTACT_CUTOFF_A)
    parser.add_argument("--seed-cutoff-a", type=float, default=DEFAULT_SEED_CUTOFF_A)
    parser.add_argument("--hotspot-neighbor-cutoff-a", type=float, default=DEFAULT_HOTSPOT_NEIGHBOR_CUTOFF_A)
    parser.add_argument("--mode", choices=["smoke", "primary", "custom"], default="primary")
    return parser.parse_args()


def input_pdb_path(dataset_slug: str, pdb_id: str) -> Path:
    return DATA_ROOT / dataset_slug / "rcsb" / pdb_id.lower() / f"{pdb_id}.pdb"


def validation_paths_for_metadata(dataset_slug: str) -> list[str]:
    spec = DATASETS[dataset_slug]
    validation_pdb = spec["validation_pdb"]
    validation_dir = DATA_ROOT / dataset_slug / "rcsb" / validation_pdb.lower()
    analysis_dir = ANALYSIS_ROOT / dataset_slug
    candidates = [
        validation_dir / f"{validation_pdb}.pdb",
        validation_dir / f"{validation_pdb}.cif",
        validation_dir / f"{validation_pdb}_entry.json",
        analysis_dir / f"{dataset_slug}-validation-ligand-contact-residues-8a.csv",
    ]
    return [rel(path) for path in candidates]


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


def residue_atoms_for_chain(atoms: list[dict], chain: str) -> tuple[list[int], dict[int, str], dict[int, list[dict]]]:
    grouped: dict[int, list[dict]] = defaultdict(list)
    names: dict[int, str] = {}
    for atom in protein_atoms(atoms, chain):
        if atom["element"] == "H":
            continue
        grouped[atom["resi"]].append(atom)
        names[atom["resi"]] = atom["resn"]
    residues = sorted(grouped)
    return residues, names, dict(grouped)


def ligand_atoms(atoms: list[dict], ligand_ids: Iterable[str], chain: str) -> list[dict]:
    allowed = set(ligand_ids)
    return [
        atom
        for atom in heavy_atoms(atoms)
        if atom["record"] == "HETATM" and atom["resn"] in allowed and atom["chain"] == chain
    ]


def seed_residues_from_ligands(
    atoms: list[dict],
    residue_atoms: dict[int, list[dict]],
    ligand_ids: list[str],
    chain: str,
    cutoff_a: float,
) -> tuple[list[int], dict[str, list[int]]]:
    by_ligand: dict[str, list[int]] = {}
    selected: set[int] = set()
    for ligand_id in ligand_ids:
        latoms = ligand_atoms(atoms, [ligand_id], chain)
        residues = []
        for residue, ratoms in sorted(residue_atoms.items()):
            if latoms and min_distance(ratoms, latoms) <= cutoff_a:
                residues.append(residue)
                selected.add(residue)
        by_ligand[ligand_id] = residues
    return sorted(selected), by_ligand


def is_sequence_adjacent_backbone_contact(left_atom: dict, right_atom: dict) -> bool:
    if abs(left_atom["resi"] - right_atom["resi"]) != 1:
        return False
    return left_atom["name"] in BACKBONE_ATOMS and right_atom["name"] in BACKBONE_ATOMS


def atom_contact_counts(
    residues: list[int],
    residue_atoms: dict[int, list[dict]],
    cutoff_a: float,
) -> tuple[np.ndarray, dict[str, int]]:
    index = {residue: pos for pos, residue in enumerate(residues)}
    counts = np.zeros((len(residues), len(residues)), dtype=np.float64)
    cutoff_sq = cutoff_a * cutoff_a
    raw_contacts = 0
    excluded_backbone_contacts = 0
    for left_pos, left_residue in enumerate(residues):
        left_atoms = residue_atoms[left_residue]
        for right_residue in residues[left_pos + 1 :]:
            right_atoms = residue_atoms[right_residue]
            contact_count = 0
            for left_atom in left_atoms:
                left_coord = left_atom["coord"]
                for right_atom in right_atoms:
                    delta = left_coord - right_atom["coord"]
                    distance_sq = float(np.dot(delta, delta))
                    if distance_sq > cutoff_sq:
                        continue
                    raw_contacts += 1
                    if is_sequence_adjacent_backbone_contact(left_atom, right_atom):
                        excluded_backbone_contacts += 1
                        continue
                    contact_count += 1
            if contact_count:
                right_pos = index[right_residue]
                counts[left_pos, right_pos] = contact_count
                counts[right_pos, left_pos] = contact_count
    stats = {
        "raw_atom_contacts_within_cutoff": raw_contacts,
        "excluded_sequence_adjacent_backbone_contacts": excluded_backbone_contacts,
        "retained_atom_contacts": int(counts.sum() / 2),
    }
    return counts, stats


def propagation_matrix(contact_counts: np.ndarray, residues: list[int], residue_atoms: dict[int, list[dict]], alpha: float) -> np.ndarray:
    probabilities = np.zeros_like(contact_counts, dtype=np.float64)
    for row_index, residue in enumerate(residues):
        atom_count = len(residue_atoms[residue])
        if atom_count == 0:
            continue
        average_atom_contacts = contact_counts[row_index, :] / atom_count
        probabilities[row_index, :] = 1.0 - np.exp(-alpha * average_atom_contacts)
    np.fill_diagonal(probabilities, 0.0)
    return probabilities


def propagate_aci(probabilities: np.ndarray, seed_indices: list[int], rounds: int, random_seed: int) -> np.ndarray:
    rng = np.random.default_rng(random_seed)
    affected_counts = np.zeros(probabilities.shape[0], dtype=np.int64)
    neighbors = [np.flatnonzero(probabilities[row] > 0.0) for row in range(probabilities.shape[0])]
    for _round in range(rounds):
        affected = np.zeros(probabilities.shape[0], dtype=bool)
        visited = np.zeros(probabilities.shape[0], dtype=bool)
        frontier = list(seed_indices)
        affected[seed_indices] = True
        visited[seed_indices] = True
        while frontier:
            next_frontier = []
            for source in frontier:
                candidates = [candidate for candidate in neighbors[source] if not visited[candidate]]
                if not candidates:
                    continue
                draws = rng.random(len(candidates))
                for candidate, draw in zip(candidates, draws):
                    if affected[source] and draw < probabilities[source, candidate]:
                        affected[candidate] = True
                    visited[candidate] = True
                    next_frontier.append(int(candidate))
            frontier = next_frontier
        affected_counts += affected.astype(np.int64)
    return affected_counts / rounds


def selected_allosteric_residue(
    residues: list[int],
    names: dict[int, str],
    aci_scores: np.ndarray,
    seed_residues: list[int],
) -> dict[str, int | str | float] | None:
    seed_set = set(seed_residues)
    candidates = [
        (residue, float(aci_scores[index]))
        for index, residue in enumerate(residues)
        if residue not in seed_set
    ]
    if not candidates:
        return None
    residue, score = sorted(candidates, key=lambda item: (-item[1], item[0]))[0]
    return {
        "residue": residue,
        "resname": names[residue],
        "aci_score": round(score, 8),
        "selection_rule": "highest_non_seed_aci",
    }


def residue_min_distance_matrix(residues: list[int], residue_atoms: dict[int, list[dict]]) -> np.ndarray:
    distances = np.full((len(residues), len(residues)), np.inf, dtype=np.float64)
    np.fill_diagonal(distances, 0.0)
    for left_pos, left_residue in enumerate(residues):
        left_coords = np.array([atom["coord"] for atom in residue_atoms[left_residue]])
        for right_pos in range(left_pos + 1, len(residues)):
            right_residue = residues[right_pos]
            right_coords = np.array([atom["coord"] for atom in residue_atoms[right_residue]])
            if left_coords.size == 0 or right_coords.size == 0:
                continue
            deltas = left_coords[:, np.newaxis, :] - right_coords[np.newaxis, :, :]
            min_distance_a = float(np.sqrt(np.min(np.sum(deltas * deltas, axis=2))))
            distances[left_pos, right_pos] = min_distance_a
            distances[right_pos, left_pos] = min_distance_a
    return distances


def hotspot_assignments(
    residues: list[int],
    names: dict[int, str],
    aci_scores: np.ndarray,
    residue_atoms: dict[int, list[dict]],
    neighbor_cutoff_a: float,
) -> dict:
    min_distances = residue_min_distance_matrix(residues, residue_atoms)
    directions: list[int] = []
    for row_index, residue in enumerate(residues):
        neighbor_indices = [
            col_index
            for col_index in np.flatnonzero(min_distances[row_index] <= neighbor_cutoff_a)
            if col_index != row_index and aci_scores[col_index] > aci_scores[row_index]
        ]
        if not neighbor_indices:
            directions.append(-1)
            continue
        target_index = sorted(
            neighbor_indices,
            key=lambda index: (-float(aci_scores[index]), residues[index]),
        )[0]
        directions.append(int(target_index))

    center_for_index: list[int] = []
    for start_index in range(len(residues)):
        seen: set[int] = set()
        current = start_index
        while directions[current] != -1 and current not in seen:
            seen.add(current)
            current = directions[current]
        center_for_index.append(current)

    centers = sorted(set(center_for_index), key=lambda index: (-float(aci_scores[index]), residues[index]))
    center_rank = {center_index: rank for rank, center_index in enumerate(centers, start=1)}
    members_by_center: dict[int, list[int]] = {center_index: [] for center_index in centers}
    for residue_index, center_index in enumerate(center_for_index):
        members_by_center[center_index].append(residue_index)

    hotspot_rows = []
    for center_index in centers:
        member_indices = sorted(members_by_center[center_index], key=lambda index: residues[index])
        member_scores = [float(aci_scores[index]) for index in member_indices]
        hotspot_rows.append(
            {
                "hotspot_rank": center_rank[center_index],
                "center_residue": residues[center_index],
                "center_resname": names[residues[center_index]],
                "center_aci_score": round(float(aci_scores[center_index]), 8),
                "member_count": len(member_indices),
                "member_residues": ";".join(str(residues[index]) for index in member_indices),
                "max_member_aci_score": round(max(member_scores), 8),
                "mean_member_aci_score": round(sum(member_scores) / len(member_scores), 8),
            }
        )

    assignment_rows = []
    for residue_index, residue in enumerate(residues):
        direction_index = directions[residue_index]
        center_index = center_for_index[residue_index]
        row = {
            "residue": residue,
            "resname": names[residue],
            "aci_score": round(float(aci_scores[residue_index]), 8),
            "hotspot_rank": center_rank[center_index],
            "hotspot_center_residue": residues[center_index],
            "hotspot_center_resname": names[residues[center_index]],
            "direction_residue": "" if direction_index == -1 else residues[direction_index],
            "direction_resname": "" if direction_index == -1 else names[residues[direction_index]],
            "distance_to_direction_A": "" if direction_index == -1 else round(float(min_distances[residue_index, direction_index]), 8),
        }
        assignment_rows.append(row)

    return {
        "hotspot_rows": hotspot_rows,
        "assignment_rows": assignment_rows,
        "hotspot_count": len(hotspot_rows),
        "clustered_residue_count": len(residues),
    }


def float_for_run_id(value: float) -> str:
    return str(value).replace(".", "p")


def run_id(dataset_slug: str, mode: str, rounds: int, alpha: float, seed_cutoff_a: float) -> str:
    alpha_text = float_for_run_id(alpha)
    cutoff_text = float_for_run_id(seed_cutoff_a)
    return f"ohm_atom_contacts_strict_{mode}_{dataset_slug}_{rounds}r_alpha{alpha_text}_seedcutoff{cutoff_text}a"


def write_connectivity_matrix(path: Path, residues: list[int], names: dict[int, str], probabilities: np.ndarray) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = ["residue_i", "resname_i", "residue_j", "resname_j", "propagation_probability"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        rows, cols = np.nonzero(probabilities > 0.0)
        for row, col in sorted(zip(rows, cols), key=lambda item: (residues[item[0]], residues[item[1]])):
            writer.writerow(
                {
                    "residue_i": residues[row],
                    "resname_i": names[residues[row]],
                    "residue_j": residues[col],
                    "resname_j": names[residues[col]],
                    "propagation_probability": round(float(probabilities[row, col]), 8),
                }
            )


def write_hit_list(path: Path, residues: list[int], names: dict[int, str], aci_scores: np.ndarray, seed_residues: list[int]) -> None:
    seed_set = set(seed_residues)
    rows = []
    rank_non_seed = 0
    sorted_items = sorted(
        ((residue, float(aci_scores[index])) for index, residue in enumerate(residues)),
        key=lambda item: (-item[1], item[0]),
    )
    for rank_all, (residue, score) in enumerate(sorted_items, start=1):
        is_seed = residue in seed_set
        if is_seed:
            non_seed_rank = ""
        else:
            rank_non_seed += 1
            non_seed_rank = rank_non_seed
        rows.append(
            {
                "rank_all": rank_all,
                "rank_non_seed": non_seed_rank,
                "residue": residue,
                "resname": names[residue],
                "aci_score": round(score, 8),
                "is_seed": "yes" if is_seed else "no",
            }
        )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_rows(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def dataset_run(dataset_slug: str, args: argparse.Namespace, git_commit: str | None) -> dict:
    spec = RUN_SPECS[dataset_slug]
    pdb_path = input_pdb_path(dataset_slug, spec["input_pdb"])
    atoms, _records = parse_pdb(pdb_path)
    residues, names, residue_atoms = residue_atoms_for_chain(atoms, spec["input_chain"])
    seed_residues, seed_by_ligand = seed_residues_from_ligands(
        atoms,
        residue_atoms,
        spec["seed_ligands"],
        spec["input_chain"],
        args.seed_cutoff_a,
    )
    if not seed_residues:
        raise SystemExit(f"{dataset_slug}: no active-site seed residues found; skip or define a seed policy first")

    contact_counts, contact_stats = atom_contact_counts(residues, residue_atoms, args.atom_contact_cutoff_a)
    probabilities = propagation_matrix(contact_counts, residues, residue_atoms, args.alpha)
    residue_to_index = {residue: index for index, residue in enumerate(residues)}
    seed_indices = [residue_to_index[residue] for residue in seed_residues if residue in residue_to_index]
    aci_scores = propagate_aci(probabilities, seed_indices, args.rounds, args.seed)
    non_seed_residues = [residue for residue in residues if residue not in set(seed_residues)]
    non_seed_aci_scores = np.array([aci_scores[residue_to_index[residue]] for residue in non_seed_residues])
    hotspots = hotspot_assignments(
        non_seed_residues,
        names,
        non_seed_aci_scores,
        residue_atoms,
        args.hotspot_neighbor_cutoff_a,
    )

    current_run_id = run_id(dataset_slug, args.mode, args.rounds, args.alpha, args.seed_cutoff_a)
    out_dir = ANALYSIS_ROOT / dataset_slug / "runs" / current_run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    matrix_path = out_dir / "connectivity-matrix.csv"
    hit_list_path = out_dir / "residue-hit-list.csv"
    hotspots_path = out_dir / "hotspots.csv"
    hotspot_assignments_path = out_dir / "residue-hotspot-assignments.csv"
    metadata_path = out_dir / "method-metadata.json"
    trace_path = out_dir / "eval-trace.json"

    write_connectivity_matrix(matrix_path, residues, names, probabilities)
    write_hit_list(hit_list_path, residues, names, aci_scores, seed_residues)
    write_rows(hotspots_path, hotspots["hotspot_rows"])
    write_rows(hotspot_assignments_path, hotspots["assignment_rows"])

    validation_exclusions = validation_paths_for_metadata(dataset_slug)
    input_metadata_paths = [
        rel(pdb_path),
        rel(pdb_path.with_suffix(".cif")),
        rel(pdb_path.parent / f"{spec['input_pdb']}_entry.json"),
    ]
    metadata = {
        "run_id": current_run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "dataset_slug": dataset_slug,
        "method": {
            "name": "ohm_atom_contacts_strict",
            "version": METHOD_VERSION,
            "paper": "Wang et al. 2020, Nature Communications, doi:10.1038/s41467-020-17618-2",
            "formula_provenance": FORMULA_TAG,
            "traversal_provenance": TRAVERSAL_TAG,
            "hotspot_provenance": HOTSPOT_TAG,
            "note": spec["note"],
        },
        "input": {
            "pdb_id": spec["input_pdb"],
            "chain_id": spec["input_chain"],
            "pdb_path": rel(pdb_path),
            "metadata_paths": input_metadata_paths,
            "validation_paths_excluded_from_features": validation_exclusions,
            "excluded_input_ligands": spec["excluded_input_ligands"],
        },
        "parameters": {
            "rounds": args.rounds,
            "random_seed": args.seed,
            "alpha": args.alpha,
            "atom_contact_cutoff_A": args.atom_contact_cutoff_a,
            "seed_cutoff_A": args.seed_cutoff_a,
            "sequence_adjacent_backbone_contacts": "excluded",
            "seed_ligands": spec["seed_ligands"],
            "hotspot_neighbor_cutoff_A": args.hotspot_neighbor_cutoff_a,
            "propagation_probability_formula": "P_ij = 1 - exp(-alpha * C_ij / atom_count_i)",
            "traversal_semantics": "separate V affected vector and W visited vector; failed propagation still marks the candidate visited",
            "hotspot_direction_rule": "exclude active-site seed residues, then assign each residue to the higher-ACI neighbor within the hotspot cutoff; tie-break by highest ACI then lowest residue number",
        },
        "seed_residues": {
            "all": seed_residues,
            "by_ligand": seed_by_ligand,
        },
        "selected_allosteric_residue": selected_allosteric_residue(residues, names, aci_scores, seed_residues),
        "hotspots": {
            "count": hotspots["hotspot_count"],
            "clustered_residue_count": hotspots["clustered_residue_count"],
            "active_site_seed_residues_excluded": True,
            "hotspot_neighbor_cutoff_A": args.hotspot_neighbor_cutoff_a,
            "hotspots_path": rel(hotspots_path),
            "assignments_path": rel(hotspot_assignments_path),
        },
        "graph": {
            "residue_count": len(residues),
            "directed_probability_edges": int(np.count_nonzero(probabilities > 0.0)),
            "contact_stats": contact_stats,
        },
        "outputs": {
            "connectivity_matrix_path": rel(matrix_path),
            "hit_list_path": rel(hit_list_path),
            "hotspots_path": rel(hotspots_path),
            "hotspot_assignments_path": rel(hotspot_assignments_path),
            "metadata_path": rel(metadata_path),
            "eval_trace_path": rel(trace_path),
        },
    }
    write_json(metadata_path, metadata)

    trace = {
        "run_id": current_run_id,
        "created_at": metadata["created_at"],
        "dataset_slug": dataset_slug,
        "input": {
            "pdb_id": spec["input_pdb"],
            "chain_id": spec["input_chain"],
            "graph_path": rel(matrix_path),
            "metadata_paths": input_metadata_paths,
            "validation_paths_excluded_from_features": validation_exclusions,
        },
        "method": {
            "name": "ohm_atom_contacts_strict",
            "version": METHOD_VERSION,
            "random_seed": args.seed,
            "parameters": metadata["parameters"],
            "coarse_graining": "residue-level propagation probabilities from atom-wise contacts using Wang et al. 2020 Eq. 3",
            "hardware_assumption": "classical paper-reproduction baseline for later quantum-inspired comparison",
        },
        "outputs": {
            "connectivity_matrix_path": rel(matrix_path),
            "hit_list_path": rel(hit_list_path),
            "hotspots_path": rel(hotspots_path),
            "hotspot_assignments_path": rel(hotspot_assignments_path),
            "report_path": rel(metadata_path),
        },
        "metrics": {
            "baseline_name": "ohm_atom_contacts_strict",
            "scoring_status": "not_scored_prediction_stage_only",
            "strict_scoring_ready": spec["strict_scoring_ready"],
        },
        "verification": {
            "command": " ".join(["python3", "scripts/pipeline/run_ohm_like_baseline.py", *sys.argv[1:]]),
            "exit_code": 0,
            "warnings": ["Validation labels intentionally not read by this prediction runner."],
        },
    }
    if git_commit:
        trace["git_commit"] = git_commit
    write_json(trace_path, trace)
    return {
        "dataset_slug": dataset_slug,
        "run_id": current_run_id,
        "hit_list_path": rel(hit_list_path),
        "connectivity_matrix_path": rel(matrix_path),
        "hotspots_path": rel(hotspots_path),
        "hotspot_assignments_path": rel(hotspot_assignments_path),
        "metadata_path": rel(metadata_path),
        "eval_trace_path": rel(trace_path),
    }


def main() -> None:
    args = parse_args()
    git_commit = git_commit_or_none()
    results = [dataset_run(dataset_slug, args, git_commit) for dataset_slug in args.datasets]
    print(json.dumps({"runs": results}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
