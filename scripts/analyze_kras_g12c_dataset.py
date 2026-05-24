#!/usr/bin/env python3
"""Analyze the KRAS G12C 4OBE/6OIM challenge dataset.

Outputs:
- dataset-level JSON summary
- residue contacts around AMG 510 / MOV
- residue contact graph edge lists
- Traditional Chinese Markdown report
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
DATA = ROOT / "data" / "kras_g12c" / "rcsb"
OUT = ROOT / "analysis" / "kras_g12c"
REPORT = OUT / "kras-g12c-4obe-6oim-dataset-analysis.zh-TW.md"
SUMMARY_JSON = OUT / "kras-g12c-4obe-6oim-dataset-summary.json"
MOV_CONTACTS_CSV = OUT / "kras-g12c-6oim-amg510-mov-contact-residues.csv"

PDB_IDS = ("4OBE", "6OIM")
SWITCH_I = set(range(30, 41))
SWITCH_II = set(range(60, 77))
P_LOOP = set(range(10, 18))
ACTIVE_SITE_RESIDUES = P_LOOP | set(range(30, 36)) | set(range(57, 62))
REFERENCE_SIIP_RESIDUES = {12, 41, 58, 64, 67, 68, 71, 80, 95, 96, 99, 103}
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
    seq_parts = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(">"):
            if header is not None:
                records.append({"header": header, "length": len("".join(seq_parts))})
            header = line[1:]
            seq_parts = []
        else:
            seq_parts.append(line.strip())
    if header is not None:
        records.append({"header": header, "length": len("".join(seq_parts))})
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


def residue_region(resi: int) -> str:
    if resi in P_LOOP:
        return "P-loop / nucleotide active site"
    if resi in SWITCH_I:
        return "Switch-I"
    if resi in SWITCH_II:
        return "Switch-II / SII-P"
    if resi in ACTIVE_SITE_RESIDUES:
        return "active-site neighborhood"
    return "distal/core/surface"


def residue_id(atom: dict) -> tuple[str, int, str, str]:
    return (atom["chain"], atom["resi"], atom["icode"], atom["resn"])


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
    chains: dict[str, dict] = {}
    by_chain = defaultdict(list)
    for atom in protein_atoms(atoms):
        by_chain[atom["chain"]].append(atom)
    for chain, chain_atoms in sorted(by_chain.items()):
        residues = {(a["resi"], a["icode"], a["resn"]) for a in chain_atoms}
        residue_numbers = sorted({a["resi"] for a in chain_atoms})
        ca_count = sum(1 for a in chain_atoms if a["name"] == "CA")
        bfactors = [a["bfactor"] for a in chain_atoms if a["bfactor"] is not None]
        chains[chain] = {
            "atom_count": len(chain_atoms),
            "residue_count": len(residues),
            "ca_count": ca_count,
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


def ligand_summary(atoms: list[dict]) -> dict:
    groups = defaultdict(list)
    for atom in heavy_atoms(atoms):
        if atom["record"] != "HETATM":
            continue
        groups[(atom["resn"], atom["chain"], atom["resi"], atom["icode"])].append(atom)
    compounds = defaultdict(lambda: {"instances": 0, "heavy_atoms": 0, "chains": set()})
    for (resn, chain, _resi, _icode), group_atoms in groups.items():
        compounds[resn]["instances"] += 1
        compounds[resn]["heavy_atoms"] += len(group_atoms)
        compounds[resn]["chains"].add(chain)
    return {
        resn: {
            "instances": values["instances"],
            "heavy_atoms": values["heavy_atoms"],
            "chains": sorted(values["chains"]),
        }
        for resn, values in sorted(compounds.items())
    }


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


def select_ligand(atoms: list[dict], resn: str, chain: str | None = None) -> list[dict]:
    return [
        atom
        for atom in heavy_atoms(atoms)
        if atom["record"] == "HETATM"
        and atom["resn"] == resn
        and (chain is None or atom["chain"] == chain)
    ]


def min_distance(group_a: Iterable[dict], group_b: Iterable[dict]) -> float:
    best = math.inf
    b_atoms = list(group_b)
    for a in group_a:
        for b in b_atoms:
            best = min(best, float(np.linalg.norm(a["coord"] - b["coord"])))
    return best


def centroid(coords_or_atoms: Iterable) -> np.ndarray:
    values = []
    for item in coords_or_atoms:
        values.append(item["coord"] if isinstance(item, dict) else item)
    return np.asarray(values, dtype=float).mean(axis=0)


def kabsch(mobile: list[np.ndarray], target: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    mobile_arr = np.asarray(mobile, dtype=float)
    target_arr = np.asarray(target, dtype=float)
    mobile_centroid = mobile_arr.mean(axis=0)
    target_centroid = target_arr.mean(axis=0)
    x = mobile_arr - mobile_centroid
    y = target_arr - target_centroid
    covariance = x.T @ y
    v, _s, wt = np.linalg.svd(covariance)
    determinant = np.sign(np.linalg.det(v @ wt))
    rotation = v @ np.diag([1.0, 1.0, determinant]) @ wt
    translation = target_centroid - mobile_centroid @ rotation
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
    squared = [float(np.sum((ca_a[r] - ca_b[r]) ** 2)) for r in common]
    return math.sqrt(sum(squared) / len(squared)), len(common)


def contact_graph(res_atoms: dict[int, list[dict]], cutoff: float = 8.0) -> tuple[dict[int, np.ndarray], list[tuple[int, int, float]], dict]:
    centers = {resi: centroid(atoms) for resi, atoms in res_atoms.items()}
    residues = sorted(centers)
    edges = []
    for idx, left in enumerate(residues):
        for right in residues[idx + 1 :]:
            distance = float(np.linalg.norm(centers[left] - centers[right]))
            if distance <= cutoff:
                edges.append((left, right, distance))
    graph = defaultdict(list)
    for left, right, distance in edges:
        graph[left].append((right, distance))
        graph[right].append((left, distance))
    seen = set()
    components = []
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
    node_count = len(residues)
    max_edges = node_count * (node_count - 1) / 2 if node_count > 1 else 1
    degrees = [len(graph[residue]) for residue in residues]
    summary = {
        "nodes": node_count,
        "edges": len(edges),
        "adjacency_matrix_shape": [node_count, node_count],
        "average_degree": round(mean(degrees), 3) if degrees else 0,
        "max_degree": max(degrees) if degrees else 0,
        "density": round(len(edges) / max_edges, 5),
        "component_count": len(components),
        "largest_component_nodes": max((len(c) for c in components), default=0),
    }
    return centers, edges, summary


def shortest_paths(edges: list[tuple[int, int, float]], sources: Iterable[int]) -> dict[int, int]:
    graph = defaultdict(list)
    for left, right, _distance in edges:
        graph[left].append(right)
        graph[right].append(left)
    distances = {source: 0 for source in sources if source in graph}
    queue = deque(distances)
    while queue:
        node = queue.popleft()
        for nxt in graph[node]:
            if nxt not in distances:
                distances[nxt] = distances[node] + 1
                queue.append(nxt)
    return distances


def write_edges(path: Path, edges: list[tuple[int, int, float]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["residue_i", "residue_j", "centroid_distance_A"])
        writer.writeheader()
        for left, right, distance in edges:
            writer.writerow(
                {
                    "residue_i": left,
                    "residue_j": right,
                    "centroid_distance_A": round(distance, 3),
                }
            )


def entry_metadata(entry: dict) -> dict:
    refine = (entry.get("refine") or [{}])[0]
    citation = entry.get("rcsb_primary_citation") or {}
    info = entry.get("rcsb_entry_info") or {}
    accession = entry.get("rcsb_accession_info") or {}
    return {
        "title": safe_get(entry, ("struct", "title")),
        "method": ", ".join(item.get("method", "") for item in entry.get("exptl") or [] if item.get("method")),
        "resolution_A": refine.get("ls_d_res_high"),
        "r_work": refine.get("ls_R_factor_R_work"),
        "r_free": refine.get("ls_R_factor_R_free"),
        "deposited_atom_count": info.get("deposited_atom_count"),
        "deposited_polymer_monomer_count": info.get("deposited_polymer_monomer_count"),
        "molecular_weight_kDa": info.get("molecular_weight"),
        "deposit_date": accession.get("deposit_date"),
        "release_date": accession.get("initial_release_date"),
        "doi": citation.get("pdbx_database_id_DOI"),
        "pubmed_id": citation.get("pdbx_database_id_PubMed"),
    }


def analyze_entry(pdb_id: str) -> dict:
    pid = pdb_id.upper()
    base = DATA / pid.lower()
    files = {
        "pdb": base / f"{pid}.pdb",
        "cif": base / f"{pid}.cif",
        "fasta": base / f"{pid}.fasta",
        "entry_json": base / f"{pid}_entry.json",
        "validation_xml": base / f"{pid}_validation.xml",
        "manifest": base / f"{pid}_download_manifest.json",
    }
    atoms, pdb_extra = parse_pdb(files["pdb"])
    entry = load_json(files["entry_json"])
    file_stats = {name: file_dimensions(path) for name, path in files.items() if path.exists()}
    return {
        "pdb_id": pid,
        "source_page": f"https://www.rcsb.org/structure/{pid}",
        "download_directory": rel(base),
        "metadata": entry_metadata(entry),
        "files": file_stats,
        "pdb_records": pdb_extra,
        "fasta": parse_fasta(files["fasta"]) if files["fasta"].exists() else {},
        "mmcif": parse_mmcif_dimensions(files["cif"]) if files["cif"].exists() else {},
        "chains": chain_summary(atoms),
        "ligands_and_heterogens": ligand_summary(atoms),
        "atoms": atoms,
    }


def mutation_differences(names4: dict[int, str], names6: dict[int, str]) -> list[dict]:
    rows = []
    for resi in sorted(set(names4) & set(names6)):
        if names4[resi] != names6[resi]:
            rows.append({"residue": resi, "4OBE": names4[resi], "6OIM": names6[resi]})
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    entries = {pdb_id: analyze_entry(pdb_id) for pdb_id in PDB_IDS}
    atoms4 = entries["4OBE"].pop("atoms")
    atoms6 = entries["6OIM"].pop("atoms")

    ca4_raw, names4 = ca_by_residue(atoms4, "A")
    ca6, names6 = ca_by_residue(atoms6, "A")
    common_ca = sorted(set(ca4_raw) & set(ca6))
    rotation, translation = kabsch([ca4_raw[r] for r in common_ca], [ca6[r] for r in common_ca])
    atoms4_aligned = transform_atoms(atoms4, rotation, translation)
    ca4, names4 = ca_by_residue(atoms4_aligned, "A")

    res4, names4 = atoms_by_residue(atoms4_aligned, "A")
    res6, names6 = atoms_by_residue(atoms6, "A")
    mov_atoms = select_ligand(atoms6, "MOV", "A")
    gdp6_atoms = select_ligand(atoms6, "GDP", "A")
    gdp4_atoms = select_ligand(atoms4_aligned, "GDP", "A")

    centers4, edges4, graph4 = contact_graph(res4)
    centers6, edges6, graph6 = contact_graph(res6)
    write_edges(OUT / "kras-g12c-4obe-residue-contact-graph-8a.csv", edges4)
    write_edges(OUT / "kras-g12c-6oim-residue-contact-graph-8a.csv", edges6)

    active_center6 = centroid(centers6[r] for r in sorted(ACTIVE_SITE_RESIDUES & set(centers6)))
    mov_center = centroid(mov_atoms)
    gdp6_center = centroid(gdp6_atoms)
    gdp4_center = centroid(gdp4_atoms) if gdp4_atoms else None

    contact_rows = []
    for resi, residue_atoms in sorted(res6.items()):
        d_mov = min_distance(residue_atoms, mov_atoms)
        if d_mov > 8.0:
            continue
        d_gdp = min_distance(residue_atoms, gdp6_atoms) if gdp6_atoms else math.inf
        contact_rows.append(
            {
                "residue": resi,
                "resname_6OIM": names6.get(resi),
                "resname_4OBE": names4.get(resi),
                "min_distance_to_MOV_A": round(d_mov, 3),
                "min_distance_to_GDP_6OIM_A": round(d_gdp, 3) if math.isfinite(d_gdp) else None,
                "region": residue_region(resi),
                "challenge_reference_residue": resi in REFERENCE_SIIP_RESIDUES,
            }
        )

    with MOV_CONTACTS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(contact_rows[0]))
        writer.writeheader()
        writer.writerows(contact_rows)

    contact_5a = {row["residue"] for row in contact_rows if row["min_distance_to_MOV_A"] <= 5.0}
    contact_6a = {row["residue"] for row in contact_rows if row["min_distance_to_MOV_A"] <= 6.0}
    active_dist = shortest_paths(edges6, ACTIVE_SITE_RESIDUES)
    rmsd_all, n_all = rmsd(ca4, ca6, common_ca)
    rmsd_switch_i, n_switch_i = rmsd(ca4, ca6, SWITCH_I)
    rmsd_switch_ii, n_switch_ii = rmsd(ca4, ca6, SWITCH_II)
    rmsd_p_loop, n_p_loop = rmsd(ca4, ca6, P_LOOP)
    rmsd_contact_5a, n_contact_5a = rmsd(ca4, ca6, contact_5a)

    comparison = {
        "chain_compared": "A",
        "common_ca_residues": len(common_ca),
        "sequence_residue_differences_chain_A": mutation_differences(names4, names6),
        "rmsd_A": {
            "global": round(rmsd_all, 3),
            "p_loop": round(rmsd_p_loop, 3),
            "switch_i": round(rmsd_switch_i, 3),
            "switch_ii": round(rmsd_switch_ii, 3),
            "mov_contact_residues_5A": round(rmsd_contact_5a, 3),
        },
        "rmsd_residue_counts": {
            "global": n_all,
            "p_loop": n_p_loop,
            "switch_i": n_switch_i,
            "switch_ii": n_switch_ii,
            "mov_contact_residues_5A": n_contact_5a,
        },
        "ligand_geometry_6OIM": {
            "MOV_heavy_atoms": len(mov_atoms),
            "GDP_heavy_atoms": len(gdp6_atoms),
            "MOV_centroid_to_GDP_centroid_A": round(float(np.linalg.norm(mov_center - gdp6_center)), 3),
            "MOV_centroid_to_active_site_centroid_A": round(float(np.linalg.norm(mov_center - active_center6)), 3),
            "GDP_centroid_shift_4OBE_to_6OIM_after_alignment_A": round(
                float(np.linalg.norm(gdp4_center - gdp6_center)), 3
            )
            if gdp4_center is not None
            else None,
        },
        "MOV_contact_residues": {
            "within_5A": sorted(contact_5a),
            "within_6A": sorted(contact_6a),
            "within_8A_count": len(contact_rows),
            "graph_distance_from_active_site_for_5A_contacts": {
                str(resi): active_dist.get(resi) for resi in sorted(contact_5a)
            },
        },
        "contact_graph_cutoff_8A": {"4OBE": graph4, "6OIM": graph6},
    }

    summary = {
        "dataset": "KRAS G12C Oncology challenge pair",
        "pdb_ids": list(PDB_IDS),
        "rcsb_pages_checked_with_browser": [
            "https://www.rcsb.org/structure/4OBE",
            "https://www.rcsb.org/structure/6OIM",
        ],
        "download_menu_items_seen": [
            "FASTA Sequence",
            "PDBx/mmCIF Format",
            "Legacy PDB Format",
            "PDBML/XML Format",
            "Structure Factors",
            "Validation XML",
            "Biological Assembly",
        ],
        "entries": entries,
        "comparison": comparison,
        "outputs": {
            "report": rel(REPORT),
            "summary_json": rel(SUMMARY_JSON),
            "mov_contacts_csv": rel(MOV_CONTACTS_CSV),
            "contact_graph_4OBE_csv": rel(OUT / "kras-g12c-4obe-residue-contact-graph-8a.csv"),
            "contact_graph_6OIM_csv": rel(OUT / "kras-g12c-6oim-residue-contact-graph-8a.csv"),
        },
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    REPORT.write_text(render_report(summary, contact_rows), encoding="utf-8")
    print(json.dumps(summary["outputs"], indent=2, ensure_ascii=False))


def metadata_table(entries: dict) -> str:
    rows = [
        "| PDB | Title | Method | Resolution (A) | Atoms | Polymer monomers | Release | DOI |",
        "| --- | --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for pdb_id in PDB_IDS:
        meta = entries[pdb_id]["metadata"]
        rows.append(
            "| {pdb} | {title} | {method} | {res} | {atoms} | {monomers} | {release} | {doi} |".format(
                pdb=pdb_id,
                title=(meta.get("title") or "").replace("|", "\\|"),
                method=meta.get("method") or "",
                res=meta.get("resolution_A") or "",
                atoms=meta.get("deposited_atom_count") or "",
                monomers=meta.get("deposited_polymer_monomer_count") or "",
                release=meta.get("release_date") or "",
                doi=meta.get("doi") or "",
            )
        )
    return "\n".join(rows)


def file_table(entries: dict) -> str:
    rows = [
        "| PDB | Artifact | Path | Bytes | Lines / rows |",
        "| --- | --- | --- | ---: | ---: |",
    ]
    for pdb_id in PDB_IDS:
        for name, stats in entries[pdb_id]["files"].items():
            line_value = stats.get("lines")
            if name == "cif":
                line_value = entries[pdb_id]["mmcif"].get("atom_site_rows")
            rows.append(
                f"| {pdb_id} | {name} | `{stats['path']}` | {stats['bytes']} | {line_value if line_value is not None else ''} |"
            )
    return "\n".join(rows)


def chain_table(entries: dict) -> str:
    rows = [
        "| PDB | Chain | Atoms | Residues | CA count | Residue span | Missing numbers inside span | Mean B-factor |",
        "| --- | --- | ---: | ---: | ---: | --- | --- | ---: |",
    ]
    for pdb_id in PDB_IDS:
        for chain, stats in entries[pdb_id]["chains"].items():
            missing = ", ".join(map(str, stats["missing_numbers_inside_span"])) or "-"
            rows.append(
                f"| {pdb_id} | {chain} | {stats['atom_count']} | {stats['residue_count']} | {stats['ca_count']} | "
                f"{stats['residue_min']}-{stats['residue_max']} | {missing} | {stats['mean_bfactor']} |"
            )
    return "\n".join(rows)


def ligand_table(entries: dict) -> str:
    rows = [
        "| PDB | Component | Instances | Heavy atoms | Chains | Interpretation |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    notes = {
        "GDP": "nucleotide ligand / active-site reference",
        "MG": "magnesium ion",
        "MOV": "AMG 510/Sotorasib bound-form ligand; validation allosteric pocket marker",
    }
    for pdb_id in PDB_IDS:
        for comp, stats in entries[pdb_id]["ligands_and_heterogens"].items():
            rows.append(
                f"| {pdb_id} | {comp} | {stats['instances']} | {stats['heavy_atoms']} | "
                f"{', '.join(stats['chains'])} | {notes.get(comp, '')} |"
            )
    return "\n".join(rows)


def contact_table(contact_rows: list[dict], limit: int = 30) -> str:
    rows = [
        "| Residue | 6OIM | 4OBE | MOV distance (A) | GDP distance (A) | Region | Ref. SII-P residue |",
        "| ---: | --- | --- | ---: | ---: | --- | --- |",
    ]
    for row in sorted(contact_rows, key=lambda item: item["min_distance_to_MOV_A"])[:limit]:
        rows.append(
            f"| {row['residue']} | {row['resname_6OIM']} | {row['resname_4OBE'] or ''} | "
            f"{row['min_distance_to_MOV_A']} | {row['min_distance_to_GDP_6OIM_A']} | "
            f"{row['region']} | {'yes' if row['challenge_reference_residue'] else ''} |"
        )
    return "\n".join(rows)


def render_report(summary: dict, contact_rows: list[dict]) -> str:
    entries = summary["entries"]
    comparison = summary["comparison"]
    graph4 = comparison["contact_graph_cutoff_8A"]["4OBE"]
    graph6 = comparison["contact_graph_cutoff_8A"]["6OIM"]
    ligand_geometry = comparison["ligand_geometry_6OIM"]
    rmsd_values = comparison["rmsd_A"]
    mutation_rows = comparison["sequence_residue_differences_chain_A"]
    mutation_text = ", ".join(f"{row['residue']}:{row['4OBE']}->{row['6OIM']}" for row in mutation_rows) or "none"
    return f"""# KRAS G12C Oncology 4OBE/6OIM 資料集分析報告

## 資料來源與網站核對

本報告分析 Cleveland Clinic Global Quantum + AI Challenge 2026 中 KRAS G12C (Oncology) 的 benchmark pair。PDF 表格中的 PDB ID 是 `4OBE` 與 `6OIM`；使用 Browser 自動化開啟 RCSB 頁面後確認：

- `4OBE`: <https://www.rcsb.org/structure/4OBE>
- `6OIM`: <https://www.rcsb.org/structure/6OIM>
- 兩個頁面的 `Download Files` 選單包含 FASTA、PDBx/mmCIF、Legacy PDB、PDBML/XML、validation 與 biological assembly 下載項目。

下載腳本：`scripts/download_kras_g12c_rcsb.py`
分析腳本：`scripts/analyze_kras_g12c_dataset.py`

## RCSB metadata 摘要

{metadata_table(entries)}

重要解讀：

- `4OBE` 是挑戰指定的輸入結構，RCSB title 為 GDP-bound Human KRas。它不是 G12C holo inhibitor complex；在 chain A 的第 12 位為 GLY。
- `6OIM` 是驗證結構，title 顯示 human KRAS G12C covalently bound to AMG 510。PDB 中 AMG 510 的 bound-form component ID 為 `MOV`。
- chain A residue comparison 顯示主要挑戰相關突變差異為：{mutation_text}。

## 檔案與資料維度

{file_table(entries)}

mmCIF 維度補充：

- `4OBE`: {entries['4OBE']['mmcif']['category_count']} 個 mmCIF category、{entries['4OBE']['mmcif']['loop_count']} 個 loop、atom_site rows = {entries['4OBE']['mmcif']['atom_site_rows']}。
- `6OIM`: {entries['6OIM']['mmcif']['category_count']} 個 mmCIF category、{entries['6OIM']['mmcif']['loop_count']} 個 loop、atom_site rows = {entries['6OIM']['mmcif']['atom_site_rows']}。

## 鏈與殘基維度

{chain_table(entries)}

對後續建模而言，chain A 是最直接的比較對象。若建立殘基接觸圖，可把每個 modeled residue 視為一個節點；本分析使用 residue centroid 距離小於等於 8 A 作為無向邊。

## 配體與 heterogen

{ligand_table(entries)}

對本競賽的意義：

- GDP/MG 代表 nucleotide active-site 的幾何參考。
- `6OIM` 的 `MOV` 是 AMG 510/Sotorasib 的 bound form，可當作 Switch-II pocket 的 validation marker。
- `4OBE` 沒有 `MOV`，因此適合作為 blind input；演算法應從 apo/GDP-bound topology 預測 6OIM 中會被 AMG 510 佔據的異位口袋。

## 4OBE 對 6OIM 結構對齊

本分析以 chain A 的 common C-alpha residues 做 Kabsch alignment，使用 {comparison['common_ca_residues']} 個共同 CA 原子。

| Region | RMSD (A) |
| --- | ---: |
| Global chain A | {rmsd_values['global']} |
| P-loop / nucleotide active site | {rmsd_values['p_loop']} |
| Switch-I | {rmsd_values['switch_i']} |
| Switch-II / SII-P | {rmsd_values['switch_ii']} |
| MOV 5 A contact residues | {rmsd_values['mov_contact_residues_5A']} |

解讀：Switch-II 的 RMSD 明顯高於 Switch-I 與 global average，符合 AMG 510/Sotorasib 在 KRAS G12C 中打開或穩定 Switch-II pocket 的挑戰設定。這也是量子訊號傳播模型應特別捕捉的區域。

## AMG 510 / MOV 接觸殘基

`6OIM` 中 `MOV` ligand 的 heavy atom 數：{ligand_geometry['MOV_heavy_atoms']}。
`6OIM` 中 GDP heavy atom 數：{ligand_geometry['GDP_heavy_atoms']}。

- MOV centroid 到 GDP centroid 距離：{ligand_geometry['MOV_centroid_to_GDP_centroid_A']} A
- MOV centroid 到 active-site centroid 距離：{ligand_geometry['MOV_centroid_to_active_site_centroid_A']} A
- 4OBE/6OIM 對齊後 GDP centroid shift：{ligand_geometry['GDP_centroid_shift_4OBE_to_6OIM_after_alignment_A']} A

MOV 周圍最接近的 residues：

{contact_table(contact_rows)}

完整表格輸出：`{rel(MOV_CONTACTS_CSV)}`

## 殘基接觸圖維度

| Structure | Nodes | Edges | Adjacency matrix | Avg degree | Max degree | Density | Components |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| 4OBE chain A | {graph4['nodes']} | {graph4['edges']} | {graph4['adjacency_matrix_shape'][0]} x {graph4['adjacency_matrix_shape'][1]} | {graph4['average_degree']} | {graph4['max_degree']} | {graph4['density']} | {graph4['component_count']} |
| 6OIM chain A | {graph6['nodes']} | {graph6['edges']} | {graph6['adjacency_matrix_shape'][0]} x {graph6['adjacency_matrix_shape'][1]} | {graph6['average_degree']} | {graph6['max_degree']} | {graph6['density']} | {graph6['component_count']} |

圖資料輸出：

- `analysis/kras_g12c/kras-g12c-4obe-residue-contact-graph-8a.csv`
- `analysis/kras_g12c/kras-g12c-6oim-residue-contact-graph-8a.csv`

這個 adjacency matrix 維度可直接對應到挑戰要求的 connectivity matrix prototype。若後續改用量子 walk、Hamiltonian evolution 或 variational circuit，可把此 residue graph 作為拓撲輸入。

## 對量子挑戰的建議建模重點

1. **輸入應從 4OBE 出發，而不是使用 6OIM 的 MOV 坐標。**
   `6OIM` 的 MOV contact residues 只能作為 validation label，不能洩漏到 blind prediction feature。

2. **Residue indexing 要固定。**
   4OBE 與 6OIM chain A 有共同 residue numbering，但第 12 位是關鍵差異：4OBE 為 GLY，6OIM 為 CYS。報告與 hit list 應保留 PDB residue number、chain ID 與 residue name。

3. **Switch-II pocket 不只是局部口袋偵測問題。**
   MOV 5 A contacts 同時包含 P-loop、Switch-II 與 distal/core residues。好的 connectivity metric 應該能把 active-site/nucleotide 狀態與遠端 Switch-II pocket 聯繫起來。

4. **建議 baseline。**
   建議先以 4OBE chain A 建立 8 A residue contact graph，輸出 graph diffusion、shortest path、Laplacian heat kernel 或 random walk baseline，再與量子 metric 比較。

5. **建議 submission output。**
   對 KRAS G12C 的 top hit list 可先用 `6OIM` MOV 5 A/6 A contact residues 作為 ground-truth set，評估 predicted residues 是否富集於 Switch-II pocket 周邊。

## 產出檔案

- JSON summary: `{summary['outputs']['summary_json']}`
- MOV contact CSV: `{summary['outputs']['mov_contacts_csv']}`
- 4OBE contact graph CSV: `{summary['outputs']['contact_graph_4OBE_csv']}`
- 6OIM contact graph CSV: `{summary['outputs']['contact_graph_6OIM_csv']}`

"""


if __name__ == "__main__":
    main()
