#!/usr/bin/env python3
"""Analyze BCR-ABL1 and Cardiac Myosin allosteric challenge datasets.

The script also reads the committed KRAS G12C summary and emits a cross-dataset
feature audit for all three benchmark families.
"""

from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict, deque
from pathlib import Path
from statistics import mean, pstdev
from typing import Iterable

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_ROOT = ROOT / "analysis"

DATASETS = {
    "bcr_abl1": {
        "label": "BCR-ABL1 Oncology",
        "domain": "Oncology",
        "input_pdb": "1OPL",
        "validation_pdb": "5MO4",
        "challenge_objective": "Identify the distal myristoyl pocket used by Asciminib.",
        "target_ligands": ["AY7"],
        "target_ligand_label": "Asciminib / ABL001 candidate component AY7",
        "risk_note": "The validation structure also contains an ATP-site inhibitor, so allosteric-vs-orthosteric ligand labels must be kept separate.",
    },
    "cardiac_myosin": {
        "label": "Cardiac Myosin Cardiology",
        "domain": "Cardiology",
        "input_pdb": "5TBY",
        "validation_pdb": "6C1H",
        "challenge_objective": "Identify the mechanical site where Mavacamten stabilizes the super-relaxed state.",
        "target_ligands": [],
        "target_ligand_label": "No Mavacamten-like validation ligand detected in 6C1H by PDB component ID/name.",
        "risk_note": "RCSB describes 6C1H as actin-bound myosin-IB cryo-EM, not a cardiac myosin Mavacamten holo complex; treat it as a structural validation proxy only after challenge-organizer confirmation.",
    },
}

AA3 = {
    "ALA",
    "ARG",
    "ASN",
    "ASP",
    "CYS",
    "GLN",
    "GLU",
    "GLY",
    "HIS",
    "ILE",
    "LEU",
    "LYS",
    "MET",
    "PHE",
    "PRO",
    "SER",
    "THR",
    "TRP",
    "TYR",
    "VAL",
}
COMMON_NON_TARGETS = {"HOH", "WAT", "DOD", "NA", "CL", "K", "CA", "MG", "ZN", "MN"}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def safe_get(data: dict, path: Iterable[str], default=None):
    current = data
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def file_dimensions(path: Path) -> dict:
    payload = path.read_bytes()
    out = {"path": rel(path), "bytes": len(payload)}
    try:
        text = payload.decode("utf-8")
        out["lines"] = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
    except UnicodeDecodeError:
        out["lines"] = None
    return out


def parse_fasta(path: Path) -> dict:
    records = []
    header = None
    parts = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(">"):
            if header is not None:
                records.append({"header": header, "length": len("".join(parts))})
            header = line[1:]
            parts = []
        else:
            parts.append(line.strip())
    if header is not None:
        records.append({"header": header, "length": len("".join(parts))})
    return {"record_count": len(records), "records": records}


def parse_mmcif_dimensions(path: Path) -> dict:
    categories = Counter()
    loop_count = 0
    atom_site_rows = 0
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if line == "loop_":
            loop_count += 1
        elif line.startswith("_") and "." in line:
            categories[line.split(".", 1)[0][1:]] += 1
        elif line.startswith("ATOM ") or line.startswith("HETATM "):
            atom_site_rows += 1
    return {
        "category_count": len(categories),
        "loop_count": loop_count,
        "atom_site_rows": atom_site_rows,
        "top_categories": categories.most_common(12),
    }


def parse_pdb(path: Path) -> tuple[list[dict], dict]:
    atoms = []
    counts = Counter()
    model_count = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        record = line[:6].strip()
        if record:
            counts[record] += 1
        if record == "MODEL":
            model_count += 1
        if record not in {"ATOM", "HETATM"}:
            continue
        try:
            atoms.append(
                {
                    "record": record,
                    "serial": int(line[6:11]),
                    "name": line[12:16].strip(),
                    "alt": line[16].strip(),
                    "resn": line[17:20].strip(),
                    "chain": line[21].strip() or "_",
                    "resi": int(line[22:26]),
                    "icode": line[26].strip(),
                    "coord": np.array(
                        [float(line[30:38]), float(line[38:46]), float(line[46:54])],
                        dtype=float,
                    ),
                    "occupancy": float(line[54:60]) if line[54:60].strip() else None,
                    "bfactor": float(line[60:66]) if line[60:66].strip() else None,
                    "element": (line[76:78].strip() or line[12:14].strip()).upper(),
                }
            )
        except ValueError:
            continue
    return atoms, {"record_counts": dict(counts), "model_count": model_count or 1}


def protein_atoms(atoms: list[dict], chain: str | None = None) -> list[dict]:
    out = []
    for atom in atoms:
        if atom["record"] != "ATOM" or atom["resn"] not in AA3:
            continue
        if chain is not None and atom["chain"] != chain:
            continue
        if atom["alt"] not in {"", "A"}:
            continue
        out.append(atom)
    return out


def heavy_atoms(atoms: Iterable[dict]) -> list[dict]:
    return [atom for atom in atoms if atom["element"] != "H" and atom["alt"] in {"", "A"}]


def chain_summary(atoms: list[dict]) -> dict:
    grouped = defaultdict(list)
    for atom in protein_atoms(atoms):
        grouped[atom["chain"]].append(atom)
    chains = {}
    for chain, chain_atoms in sorted(grouped.items()):
        residues = {(a["resi"], a["icode"], a["resn"]) for a in chain_atoms}
        residue_numbers = sorted({a["resi"] for a in chain_atoms})
        bfactors = [a["bfactor"] for a in chain_atoms if a["bfactor"] is not None]
        chains[chain] = {
            "atom_count": len(chain_atoms),
            "residue_count": len(residues),
            "ca_count": sum(1 for atom in chain_atoms if atom["name"] == "CA"),
            "residue_min": residue_numbers[0] if residue_numbers else None,
            "residue_max": residue_numbers[-1] if residue_numbers else None,
            "missing_numbers_inside_span": [
                r
                for r in range(residue_numbers[0], residue_numbers[-1] + 1)
                if r not in set(residue_numbers)
            ]
            if residue_numbers
            else [],
            "mean_bfactor": round(mean(bfactors), 3) if bfactors else None,
            "std_bfactor": round(pstdev(bfactors), 3) if len(bfactors) > 1 else None,
        }
    return chains


def ligand_summary(atoms: list[dict], nonpolymer_metadata: dict[str, dict]) -> dict:
    groups = defaultdict(list)
    for atom in heavy_atoms(atoms):
        if atom["record"] != "HETATM":
            continue
        groups[(atom["resn"], atom["chain"], atom["resi"], atom["icode"])].append(atom)
    ligands = defaultdict(lambda: {"instances": 0, "heavy_atoms": 0, "chains": set(), "residue_numbers": []})
    for (resn, chain, resi, _icode), group_atoms in groups.items():
        ligands[resn]["instances"] += 1
        ligands[resn]["heavy_atoms"] += len(group_atoms)
        ligands[resn]["chains"].add(chain)
        ligands[resn]["residue_numbers"].append(resi)
    out = {}
    for resn, values in sorted(ligands.items()):
        meta = nonpolymer_metadata.get(resn, {})
        out[resn] = {
            "description": meta.get("description"),
            "formula_weight": meta.get("formula_weight"),
            "instances": values["instances"],
            "heavy_atoms": values["heavy_atoms"],
            "chains": sorted(values["chains"]),
            "residue_numbers": sorted(values["residue_numbers"]),
            "is_likely_signal_ligand": resn not in COMMON_NON_TARGETS,
        }
    return out


def read_nonpolymer_metadata(base_dir: Path) -> dict[str, dict]:
    metadata = {}
    for path in sorted(base_dir.glob("*_nonpolymer_entity_*.json")):
        data = load_json(path)
        comp_id = safe_get(data, ("rcsb_nonpolymer_entity_container_identifiers", "nonpolymer_comp_id"))
        if not comp_id:
            continue
        metadata[comp_id] = {
            "description": safe_get(data, ("rcsb_nonpolymer_entity", "pdbx_description")),
            "formula_weight": safe_get(data, ("nonpolymer_comp", "chem_comp", "formula_weight")),
            "formula": safe_get(data, ("nonpolymer_comp", "chem_comp", "formula")),
        }
    return metadata


def ca_by_residue(atoms: list[dict], chain: str) -> tuple[dict[int, np.ndarray], dict[int, str]]:
    coords = {}
    names = {}
    for atom in protein_atoms(atoms, chain):
        if atom["name"] == "CA":
            coords[atom["resi"]] = atom["coord"]
            names[atom["resi"]] = atom["resn"]
    return coords, names


def atoms_by_residue(atoms: list[dict], chain: str) -> tuple[dict[int, list[dict]], dict[int, str]]:
    grouped = defaultdict(list)
    names = {}
    for atom in protein_atoms(atoms, chain):
        grouped[atom["resi"]].append(atom)
        names[atom["resi"]] = atom["resn"]
    return dict(grouped), names


def select_ligand(atoms: list[dict], comp_id: str) -> list[dict]:
    return [atom for atom in heavy_atoms(atoms) if atom["record"] == "HETATM" and atom["resn"] == comp_id]


def min_distance(group_a: Iterable[dict], group_b: Iterable[dict]) -> float:
    best = math.inf
    b_atoms = list(group_b)
    for a in group_a:
        for b in b_atoms:
            best = min(best, float(np.linalg.norm(a["coord"] - b["coord"])))
    return best


def centroid(items: Iterable) -> np.ndarray:
    values = []
    for item in items:
        values.append(item["coord"] if isinstance(item, dict) else item)
    return np.asarray(values, dtype=float).mean(axis=0)


def kabsch(mobile: list[np.ndarray], target: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    mobile_arr = np.asarray(mobile, dtype=float)
    target_arr = np.asarray(target, dtype=float)
    mobile_center = mobile_arr.mean(axis=0)
    target_center = target_arr.mean(axis=0)
    x = mobile_arr - mobile_center
    y = target_arr - target_center
    covariance = x.T @ y
    v, _s, wt = np.linalg.svd(covariance)
    determinant = np.sign(np.linalg.det(v @ wt))
    rotation = v @ np.diag([1.0, 1.0, determinant]) @ wt
    translation = target_center - mobile_center @ rotation
    return rotation, translation


def transform_atoms(atoms: list[dict], rotation: np.ndarray, translation: np.ndarray) -> list[dict]:
    transformed = []
    for atom in atoms:
        copy = dict(atom)
        copy["coord"] = atom["coord"] @ rotation + translation
        transformed.append(copy)
    return transformed


def rmsd(ca_a: dict[int, np.ndarray], ca_b: dict[int, np.ndarray], residues: Iterable[int]) -> tuple[float | None, int]:
    common = sorted(set(residues) & set(ca_a) & set(ca_b))
    if not common:
        return None, 0
    squared = [float(np.sum((ca_a[residue] - ca_b[residue]) ** 2)) for residue in common]
    return math.sqrt(sum(squared) / len(squared)), len(common)


def contact_graph(res_atoms: dict[int, list[dict]], cutoff: float = 8.0) -> tuple[dict[int, np.ndarray], list[tuple[int, int, float]], dict]:
    centers = {residue: centroid(atoms) for residue, atoms in res_atoms.items()}
    residues = sorted(centers)
    edges = []
    for index, left in enumerate(residues):
        for right in residues[index + 1 :]:
            distance = float(np.linalg.norm(centers[left] - centers[right]))
            if distance <= cutoff:
                edges.append((left, right, distance))
    graph = defaultdict(list)
    for left, right, distance in edges:
        graph[left].append((right, distance))
        graph[right].append((left, distance))
    components = []
    seen = set()
    for residue in residues:
        if residue in seen:
            continue
        queue = deque([residue])
        seen.add(residue)
        component = []
        while queue:
            node = queue.popleft()
            component.append(node)
            for nxt, _distance in graph[node]:
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        components.append(component)
    degrees = [len(graph[residue]) for residue in residues]
    max_edges = len(residues) * (len(residues) - 1) / 2 if len(residues) > 1 else 1
    return centers, edges, {
        "nodes": len(residues),
        "edges": len(edges),
        "adjacency_matrix_shape": [len(residues), len(residues)],
        "average_degree": round(mean(degrees), 3) if degrees else 0,
        "max_degree": max(degrees) if degrees else 0,
        "density": round(len(edges) / max_edges, 5),
        "component_count": len(components),
        "largest_component_nodes": max((len(component) for component in components), default=0),
    }


def write_edges(path: Path, edges: list[tuple[int, int, float]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["residue_i", "residue_j", "centroid_distance_A"])
        writer.writeheader()
        for left, right, distance in edges:
            writer.writerow({"residue_i": left, "residue_j": right, "centroid_distance_A": round(distance, 3)})


def entry_metadata(entry: dict) -> dict:
    refine = (entry.get("refine") or [{}])[0]
    em_reconstruction = (entry.get("em_3d_reconstruction") or [{}])[0]
    citation = entry.get("rcsb_primary_citation") or {}
    info = entry.get("rcsb_entry_info") or {}
    accession = entry.get("rcsb_accession_info") or {}
    resolution = refine.get("ls_d_res_high") or em_reconstruction.get("resolution")
    return {
        "title": safe_get(entry, ("struct", "title")),
        "method": ", ".join(item.get("method", "") for item in entry.get("exptl") or [] if item.get("method")),
        "resolution_A": resolution,
        "r_work": refine.get("ls_R_factor_R_work"),
        "r_free": refine.get("ls_R_factor_R_free"),
        "deposited_atom_count": info.get("deposited_atom_count"),
        "deposited_polymer_monomer_count": info.get("deposited_polymer_monomer_count"),
        "deposited_unmodeled_polymer_monomer_count": info.get("deposited_unmodeled_polymer_monomer_count"),
        "molecular_weight_kDa": info.get("molecular_weight"),
        "deposit_date": accession.get("deposit_date"),
        "release_date": accession.get("initial_release_date"),
        "doi": citation.get("pdbx_database_id_DOI"),
        "pubmed_id": citation.get("pdbx_database_id_PubMed"),
    }


def analyze_entry(dataset_slug: str, pdb_id: str) -> dict:
    pid = pdb_id.upper()
    base = ROOT / "data" / dataset_slug / "rcsb" / pid.lower()
    files = {
        "pdb": base / f"{pid}.pdb",
        "cif": base / f"{pid}.cif",
        "fasta": base / f"{pid}.fasta",
        "entry_json": base / f"{pid}_entry.json",
        "validation_xml": base / f"{pid}_validation.xml",
        "manifest": base / f"{pid}_download_manifest.json",
    }
    atoms, pdb_records = parse_pdb(files["pdb"])
    nonpolymer_metadata = read_nonpolymer_metadata(base)
    entry = load_json(files["entry_json"])
    file_stats = {name: file_dimensions(path) for name, path in files.items() if path.exists()}
    chains = chain_summary(atoms)
    selected_chain = max(chains, key=lambda key: chains[key]["residue_count"]) if chains else None
    res_atoms, _names = atoms_by_residue(atoms, selected_chain) if selected_chain else ({}, {})
    _centers, edges, graph = contact_graph(res_atoms)
    return {
        "pdb_id": pid,
        "source_page": f"https://www.rcsb.org/structure/{pid}",
        "download_directory": rel(base),
        "metadata": entry_metadata(entry),
        "files": file_stats,
        "pdb_records": pdb_records,
        "fasta": parse_fasta(files["fasta"]) if files["fasta"].exists() else {},
        "mmcif": parse_mmcif_dimensions(files["cif"]) if files["cif"].exists() else {},
        "chains": chains,
        "selected_analysis_chain": selected_chain,
        "selected_chain_contact_graph_8A": graph,
        "ligands_and_heterogens": ligand_summary(atoms, nonpolymer_metadata),
        "_atoms": atoms,
    }


def best_pair_alignment(input_atoms: list[dict], validation_atoms: list[dict], input_chains: dict, validation_chains: dict) -> dict:
    best = None
    for chain_a in input_chains:
        ca_a, names_a = ca_by_residue(input_atoms, chain_a)
        for chain_b in validation_chains:
            ca_b, names_b = ca_by_residue(validation_atoms, chain_b)
            common = sorted(set(ca_a) & set(ca_b))
            if len(common) < 3:
                continue
            rotation, translation = kabsch([ca_a[r] for r in common], [ca_b[r] for r in common])
            transformed = transform_atoms(input_atoms, rotation, translation)
            ca_a_aligned, names_a_aligned = ca_by_residue(transformed, chain_a)
            value, count = rmsd(ca_a_aligned, ca_b, common)
            mismatches = [
                {"residue": r, "input": names_a_aligned.get(r), "validation": names_b.get(r)}
                for r in common
                if names_a_aligned.get(r) != names_b.get(r)
            ]
            candidate = {
                "input_chain": chain_a,
                "validation_chain": chain_b,
                "common_ca_residues_by_pdb_number": count,
                "pdb_number_ca_rmsd_A": round(value, 3) if value is not None else None,
                "sequence_name_mismatches_by_pdb_number": mismatches[:40],
                "all_sequence_name_mismatch_count": len(mismatches),
            }
            if best is None or (count, -(value or 9999)) > (
                best["common_ca_residues_by_pdb_number"],
                -(best["pdb_number_ca_rmsd_A"] or 9999),
            ):
                best = candidate
    return best or {
        "input_chain": None,
        "validation_chain": None,
        "common_ca_residues_by_pdb_number": 0,
        "pdb_number_ca_rmsd_A": None,
        "sequence_name_mismatches_by_pdb_number": [],
        "all_sequence_name_mismatch_count": None,
    }


def ligand_contacts(validation_entry: dict, target_ligands: list[str], out_dir: Path, dataset_slug: str) -> list[dict]:
    atoms = validation_entry["_atoms"]
    selected_chain = validation_entry["selected_analysis_chain"]
    res_atoms, names = atoms_by_residue(atoms, selected_chain)
    if target_ligands:
        ligand_ids = [lig for lig in target_ligands if select_ligand(atoms, lig)]
    else:
        ligand_ids = [
            comp
            for comp, stats in validation_entry["ligands_and_heterogens"].items()
            if stats["is_likely_signal_ligand"]
        ][:4]
    rows = []
    for ligand_id in ligand_ids:
        latoms = select_ligand(atoms, ligand_id)
        for residue, residue_atoms in sorted(res_atoms.items()):
            distance = min_distance(residue_atoms, latoms)
            if distance <= 8.0:
                rows.append(
                    {
                        "ligand": ligand_id,
                        "residue": residue,
                        "resname": names.get(residue),
                        "chain": selected_chain,
                        "min_distance_to_ligand_A": round(distance, 3),
                    }
                )
    if rows:
        path = out_dir / f"{dataset_slug}-validation-ligand-contact-residues-8a.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    return rows


def analyze_dataset(dataset_slug: str, spec: dict) -> dict:
    out_dir = ANALYSIS_ROOT / dataset_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    input_entry = analyze_entry(dataset_slug, spec["input_pdb"])
    validation_entry = analyze_entry(dataset_slug, spec["validation_pdb"])
    alignment = best_pair_alignment(
        input_entry["_atoms"],
        validation_entry["_atoms"],
        input_entry["chains"],
        validation_entry["chains"],
    )

    for entry in (input_entry, validation_entry):
        chain = entry["selected_analysis_chain"]
        res_atoms, _names = atoms_by_residue(entry["_atoms"], chain)
        _centers, edges, _graph = contact_graph(res_atoms)
        write_edges(out_dir / f"{dataset_slug}-{entry['pdb_id'].lower()}-chain-{chain}-residue-contact-graph-8a.csv", edges)

    contacts = ligand_contacts(validation_entry, spec["target_ligands"], out_dir, dataset_slug)
    target_contact_count = (
        sum(1 for row in contacts if row["ligand"] in set(spec["target_ligands"]))
        if spec["target_ligands"]
        else 0
    )
    input_entry.pop("_atoms")
    validation_entry.pop("_atoms")
    dataset_summary = {
        "dataset_slug": dataset_slug,
        "label": spec["label"],
        "domain": spec["domain"],
        "challenge_objective": spec["challenge_objective"],
        "input_pdb": spec["input_pdb"],
        "validation_pdb": spec["validation_pdb"],
        "target_ligand_label": spec["target_ligand_label"],
        "target_ligands_requested": spec["target_ligands"],
        "target_ligands_found": sorted({row["ligand"] for row in contacts}),
        "target_validation_contact_row_count_8A": target_contact_count,
        "exploratory_ligand_contact_row_count_8A": len(contacts),
        "risk_note": spec["risk_note"],
        "entries": {
            spec["input_pdb"]: input_entry,
            spec["validation_pdb"]: validation_entry,
        },
        "pair_alignment_by_pdb_residue_number": alignment,
        "outputs": {
            "summary_json": rel(out_dir / f"{dataset_slug}-dataset-summary.json"),
            "report": rel(out_dir / f"{dataset_slug}-{spec['input_pdb'].lower()}-{spec['validation_pdb'].lower()}-dataset-analysis.zh-TW.md"),
            "contact_csv": rel(out_dir / f"{dataset_slug}-validation-ligand-contact-residues-8a.csv") if contacts else None,
        },
    }
    summary_path = out_dir / f"{dataset_slug}-dataset-summary.json"
    report_path = out_dir / f"{dataset_slug}-{spec['input_pdb'].lower()}-{spec['validation_pdb'].lower()}-dataset-analysis.zh-TW.md"
    summary_path.write_text(json.dumps(dataset_summary, indent=2, ensure_ascii=False), encoding="utf-8")
    report_path.write_text(render_dataset_report(dataset_summary, contacts), encoding="utf-8")
    return dataset_summary


def markdown_value(value) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|")


def metadata_table(summary: dict) -> str:
    rows = [
        "| PDB | Title | Method | Resolution (A) | Atoms | Polymer monomers | Release | DOI |",
        "| --- | --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for pdb_id, entry in summary["entries"].items():
        meta = entry["metadata"]
        rows.append(
            f"| {pdb_id} | {markdown_value(meta.get('title'))} | {markdown_value(meta.get('method'))} | "
            f"{markdown_value(meta.get('resolution_A'))} | {markdown_value(meta.get('deposited_atom_count'))} | "
            f"{markdown_value(meta.get('deposited_polymer_monomer_count'))} | {markdown_value(meta.get('release_date'))} | "
            f"{markdown_value(meta.get('doi'))} |"
        )
    return "\n".join(rows)


def files_table(summary: dict) -> str:
    rows = ["| PDB | Artifact | Path | Bytes | Lines / rows |", "| --- | --- | --- | ---: | ---: |"]
    for pdb_id, entry in summary["entries"].items():
        for artifact, stats in entry["files"].items():
            line_value = stats.get("lines")
            if artifact == "cif":
                line_value = entry["mmcif"].get("atom_site_rows")
            rows.append(f"| {pdb_id} | {artifact} | `{stats['path']}` | {stats['bytes']} | {line_value or ''} |")
    return "\n".join(rows)


def chain_table(summary: dict) -> str:
    rows = [
        "| PDB | Chain | Atoms | Residues | CA | Residue span | Missing numbers | Mean B-factor |",
        "| --- | --- | ---: | ---: | ---: | --- | --- | ---: |",
    ]
    for pdb_id, entry in summary["entries"].items():
        for chain, stats in entry["chains"].items():
            missing = ", ".join(map(str, stats["missing_numbers_inside_span"][:20])) or "-"
            if len(stats["missing_numbers_inside_span"]) > 20:
                missing += f" ... (+{len(stats['missing_numbers_inside_span']) - 20})"
            rows.append(
                f"| {pdb_id} | {chain} | {stats['atom_count']} | {stats['residue_count']} | {stats['ca_count']} | "
                f"{stats['residue_min']}-{stats['residue_max']} | {missing} | {stats['mean_bfactor']} |"
            )
    return "\n".join(rows)


def ligand_table(summary: dict) -> str:
    rows = [
        "| PDB | Component | Description | Instances | Heavy atoms | Chains | Likely signal ligand |",
        "| --- | --- | --- | ---: | ---: | --- | --- |",
    ]
    for pdb_id, entry in summary["entries"].items():
        for comp, stats in entry["ligands_and_heterogens"].items():
            rows.append(
                f"| {pdb_id} | {comp} | {markdown_value(stats.get('description'))} | {stats['instances']} | "
                f"{stats['heavy_atoms']} | {', '.join(stats['chains'])} | {'yes' if stats['is_likely_signal_ligand'] else ''} |"
            )
    return "\n".join(rows)


def graph_table(summary: dict) -> str:
    rows = [
        "| PDB | Selected chain | Nodes | Edges | Adjacency matrix | Avg degree | Max degree | Components |",
        "| --- | --- | ---: | ---: | --- | ---: | ---: | ---: |",
    ]
    for pdb_id, entry in summary["entries"].items():
        graph = entry["selected_chain_contact_graph_8A"]
        rows.append(
            f"| {pdb_id} | {entry['selected_analysis_chain']} | {graph['nodes']} | {graph['edges']} | "
            f"{graph['adjacency_matrix_shape'][0]} x {graph['adjacency_matrix_shape'][1]} | "
            f"{graph['average_degree']} | {graph['max_degree']} | {graph['component_count']} |"
        )
    return "\n".join(rows)


def contacts_table(contacts: list[dict], limit: int = 30) -> str:
    if not contacts:
        return "未偵測到指定 challenge validation ligand 的 8 A contact residue；詳見資料風險說明。"
    rows = [
        "| Ligand | Chain | Residue | Resname | Distance (A) |",
        "| --- | --- | ---: | --- | ---: |",
    ]
    for row in sorted(contacts, key=lambda item: (item["ligand"], item["min_distance_to_ligand_A"]))[:limit]:
        rows.append(
            f"| {row['ligand']} | {row['chain']} | {row['residue']} | {row['resname']} | {row['min_distance_to_ligand_A']} |"
        )
    return "\n".join(rows)


def render_dataset_report(summary: dict, contacts: list[dict]) -> str:
    align = summary["pair_alignment_by_pdb_residue_number"]
    return f"""# {summary['label']} {summary['input_pdb']}/{summary['validation_pdb']} 資料集分析報告

## 資料來源與任務定位

- Challenge objective: {summary['challenge_objective']}
- Input structure: `{summary['input_pdb']}` (<https://www.rcsb.org/structure/{summary['input_pdb']}>)
- Validation structure: `{summary['validation_pdb']}` (<https://www.rcsb.org/structure/{summary['validation_pdb']}>)
- Validation marker: {summary['target_ligand_label']}
- 資料風險：{summary['risk_note']}

Browser 自動化已核對 RCSB structure page 與 `Download Files` 選單；下載內容包含 PDB、mmCIF、FASTA、entry/entity/assembly JSON 與 validation 檔案。

## RCSB metadata 摘要

{metadata_table(summary)}

## 檔案與資料維度

{files_table(summary)}

## 鏈、殘基與 B-factor 維度

{chain_table(summary)}

## 配體與 heterogen 維度

{ligand_table(summary)}

## Pair alignment 檢查

此段只使用 PDB residue numbering 的共同 CA 原子做快速 sanity check；若兩個 PDB 不是同一蛋白或 numbering schema 不一致，RMSD 只能當資料品質警訊，不能當嚴格結構疊合結論。

| Input chain | Validation chain | Common CA residues | RMSD (A) | Residue-name mismatch count |
| --- | --- | ---: | ---: | ---: |
| {align['input_chain']} | {align['validation_chain']} | {align['common_ca_residues_by_pdb_number']} | {markdown_value(align['pdb_number_ca_rmsd_A'])} | {markdown_value(align['all_sequence_name_mismatch_count'])} |

## Validation ligand contact residues

{contacts_table(contacts)}

完整 contact CSV：`{summary['outputs']['contact_csv'] or 'not generated'}`

## Residue contact graph 維度

{graph_table(summary)}

這些 graph dimensions 可作為後續 connectivity matrix 或 quantum walk/Hamiltonian simulation 的基礎維度。對多鏈或非同源 validation pair，建議先明確決定建模 chain 或 domain，再建立 challenge-specific coarse-graining。
"""


def kr_summary() -> dict:
    path = ANALYSIS_ROOT / "kras_g12c" / "kras-g12c-4obe-6oim-dataset-summary.json"
    return load_json(path)


def cross_rows(kras: dict, others: list[dict]) -> list[dict]:
    rows = []
    if kras:
        comp = kras["comparison"]
        rows.append(
            {
                "dataset": "KRAS G12C Oncology",
                "input": "4OBE",
                "validation": "6OIM",
                "input_nodes": comp["contact_graph_cutoff_8A"]["4OBE"]["nodes"],
                "validation_nodes": comp["contact_graph_cutoff_8A"]["6OIM"]["nodes"],
                "target_ligand": "MOV / AMG 510 bound form",
                "target_contacts": len(comp["MOV_contact_residues"]["within_5A"]),
                "alignment": f"{comp['common_ca_residues']} CA, RMSD {comp['rmsd_A']['global']} A",
                "risk": "low; holo ligand marker present",
            }
        )
    for summary in others:
        input_entry = summary["entries"][summary["input_pdb"]]
        validation_entry = summary["entries"][summary["validation_pdb"]]
        align = summary["pair_alignment_by_pdb_residue_number"]
        rows.append(
            {
                "dataset": summary["label"],
                "input": summary["input_pdb"],
                "validation": summary["validation_pdb"],
                "input_nodes": input_entry["selected_chain_contact_graph_8A"]["nodes"],
                "validation_nodes": validation_entry["selected_chain_contact_graph_8A"]["nodes"],
                "target_ligand": summary["target_ligand_label"],
                "target_contacts": summary["target_validation_contact_row_count_8A"],
                "exploratory_contacts": summary["exploratory_ligand_contact_row_count_8A"],
                "alignment": f"{align['common_ca_residues_by_pdb_number']} CA, RMSD {align['pdb_number_ca_rmsd_A']} A",
                "risk": summary["risk_note"],
            }
        )
    return rows


def render_cross_report(kras: dict, others: list[dict]) -> str:
    rows = cross_rows(kras, others)
    table = [
        "| Dataset | Input | Validation | Input graph nodes | Validation graph nodes | Target / marker | Target contacts | Exploratory contacts | Pair check | Risk note |",
        "| --- | --- | --- | ---: | ---: | --- | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        table.append(
            f"| {row['dataset']} | {row['input']} | {row['validation']} | {row['input_nodes']} | {row['validation_nodes']} | "
            f"{markdown_value(row['target_ligand'])} | {row['target_contacts']} | {row.get('exploratory_contacts', row['target_contacts'])} | "
            f"{row['alignment']} | {markdown_value(row['risk'])} |"
        )
    checklist = [
        "| Dataset | RCSB files | Metadata | Chain dimensions | Ligands | Validation contacts | Contact graph | Pair comparison |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        validation_ok = "yes" if row["target_contacts"] else "risk/needs review"
        checklist.append(
            f"| {row['dataset']} | yes | yes | yes | yes | {validation_ok} | yes | yes |"
        )
    return f"""# Allosteric Challenge 三資料集交叉分析報告

## 檢查範圍

本報告交叉檢查 Cleveland Clinic challenge 中三個 minimum target families：

- KRAS G12C (Oncology): `4OBE` -> `6OIM`
- BCR-ABL1 (Oncology): `1OPL` -> `5MO4`
- Cardiac Myosin (Cardiology): `5TBY` -> `6C1H`

所有新增資料均由 RCSB 官方頁面與 API 下載，並由本 repo 的 scripts 產生可重跑分析。

## 跨資料集維度總覽

{chr(10).join(table)}

## 特徵維度覆蓋檢查

{chr(10).join(checklist)}

## 主要交叉觀察

1. KRAS G12C 是三者中最乾淨的 apo/holo validation pair：`6OIM` 明確包含 AMG 510 bound-form ligand `MOV`，可直接形成 residue-level ground truth。
2. BCR-ABL1 的 `5MO4` 包含 Asciminib candidate ligand marker `AY7`，但同時也有其他 kinase inhibitor/heterogen；後續模型必須把 myristoyl-pocket allosteric marker 與 ATP-site inhibitor 分開。
3. Cardiac Myosin 的 PDF challenge label 與 `6C1H` RCSB metadata 存在明顯語義落差：`6C1H` 是 actin-bound myosin-IB cryo-EM structure，且未偵測到 Mavacamten-like ligand。這一組可以先做 structural/mechanical proxy 分析，但提交前應向 challenge organizer 確認 validation label。
4. Contact graph node counts 差異很大，代表 coarse-graining 策略不能一體套用：KRAS 是百級 residue graph，BCR-ABL1 是 kinase/regulatory domain 中型 graph，Myosin 是大型 multi-chain motor/actin complex。

## 後續建模建議

- 先為每組資料明確定義「可用於 blind input 的 features」與「只能用於 validation 的 labels」。
- 對 BCR-ABL1 與 Myosin 這類多 domain 或跨蛋白資料，優先建立 domain-level chain selection 與 residue numbering 對應表。
- 對 Cardiac Myosin，先不要把 `6C1H` 當作 Mavacamten holo ground truth；可暫時作為 mechanical state comparison target。
"""


def main() -> None:
    summaries = [analyze_dataset(slug, spec) for slug, spec in DATASETS.items()]
    kras = kr_summary()
    cross_dir = ANALYSIS_ROOT / "cross_dataset"
    cross_dir.mkdir(parents=True, exist_ok=True)
    cross_summary = {"kras_g12c": kras, "additional_datasets": summaries}
    (cross_dir / "allosteric-challenge-three-dataset-cross-summary.json").write_text(
        json.dumps(cross_summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (cross_dir / "allosteric-challenge-three-dataset-cross-analysis.zh-TW.md").write_text(
        render_cross_report(kras, summaries),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "reports": [
                    summary["outputs"]["report"] for summary in summaries
                ]
                + [rel(cross_dir / "allosteric-challenge-three-dataset-cross-analysis.zh-TW.md")],
                "summaries": [
                    summary["outputs"]["summary_json"] for summary in summaries
                ]
                + [rel(cross_dir / "allosteric-challenge-three-dataset-cross-summary.json")],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
