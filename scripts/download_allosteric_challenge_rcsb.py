#!/usr/bin/env python3
"""Download RCSB artifacts for the non-KRAS allosteric challenge datasets."""

from __future__ import annotations

import gzip
import json
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]

DATASETS = {
    "bcr_abl1": {
        "label": "BCR-ABL1 Oncology",
        "pdb_ids": ("1OPL", "5MO4"),
    },
    "cardiac_myosin": {
        "label": "Cardiac Myosin Cardiology",
        "pdb_ids": ("5TBY", "6C1H"),
    },
}


@dataclass(frozen=True)
class Resource:
    name: str
    url: str
    filename: str
    binary: bool = True
    decompress_gzip: bool = False


def request_bytes(url: str, timeout: int = 60) -> tuple[int, bytes, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "quantum-challenge-allosteric-dataset/1.0",
            "Accept": "*/*",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return getattr(response, "status", 200), response.read(), response.geturl()


def save_resource(resource: Resource, out_dir: Path) -> dict:
    path = out_dir / resource.filename
    started = time.time()
    try:
        status, payload, final_url = request_bytes(resource.url)
        if resource.decompress_gzip:
            payload = gzip.decompress(payload)
        if resource.binary:
            path.write_bytes(payload)
        else:
            path.write_text(payload.decode("utf-8"), encoding="utf-8")
        return {
            "name": resource.name,
            "url": resource.url,
            "final_url": final_url,
            "path": str(path.relative_to(ROOT)),
            "status": status,
            "ok": True,
            "bytes": len(payload),
            "elapsed_sec": round(time.time() - started, 3),
        }
    except urllib.error.HTTPError as exc:
        return {
            "name": resource.name,
            "url": resource.url,
            "path": str(path.relative_to(ROOT)),
            "status": exc.code,
            "ok": False,
            "error": exc.reason,
            "elapsed_sec": round(time.time() - started, 3),
        }
    except Exception as exc:  # noqa: BLE001 - keep failures in the manifest.
        return {
            "name": resource.name,
            "url": resource.url,
            "path": str(path.relative_to(ROOT)),
            "status": None,
            "ok": False,
            "error": repr(exc),
            "elapsed_sec": round(time.time() - started, 3),
        }


def base_resources(pdb_id: str) -> list[Resource]:
    pid = pdb_id.upper()
    lower = pid.lower()
    return [
        Resource("legacy_pdb", f"https://files.rcsb.org/download/{pid}.pdb", f"{pid}.pdb"),
        Resource("mmcif", f"https://files.rcsb.org/download/{pid}.cif", f"{pid}.cif"),
        Resource(
            "fasta",
            f"https://www.rcsb.org/fasta/entry/{pid}/download",
            f"{pid}.fasta",
            binary=False,
        ),
        Resource("entry_json", f"https://data.rcsb.org/rest/v1/core/entry/{pid}", f"{pid}_entry.json"),
        Resource(
            "validation_xml",
            f"https://files.rcsb.org/validation/download/{lower}_validation.xml.gz",
            f"{pid}_validation.xml",
            decompress_gzip=True,
        ),
        Resource(
            "full_validation_pdf_gz",
            f"https://files.rcsb.org/validation/download/{lower}_full_validation.pdf.gz",
            f"{pid}_full_validation.pdf.gz",
        ),
    ]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def metadata_resources(pdb_id: str, entry: dict) -> Iterable[Resource]:
    pid = pdb_id.upper()
    ids = entry.get("rcsb_entry_container_identifiers", {})
    for assembly_id in ids.get("assembly_ids") or []:
        yield Resource(
            f"assembly_{assembly_id}_json",
            f"https://data.rcsb.org/rest/v1/core/assembly/{pid}/{assembly_id}",
            f"{pid}_assembly_{assembly_id}.json",
        )
    for entity_id in ids.get("polymer_entity_ids") or ids.get("entity_ids") or []:
        yield Resource(
            f"polymer_entity_{entity_id}_json",
            f"https://data.rcsb.org/rest/v1/core/polymer_entity/{pid}/{entity_id}",
            f"{pid}_polymer_entity_{entity_id}.json",
        )
    for entity_id in ids.get("non_polymer_entity_ids") or []:
        yield Resource(
            f"nonpolymer_entity_{entity_id}_json",
            f"https://data.rcsb.org/rest/v1/core/nonpolymer_entity/{pid}/{entity_id}",
            f"{pid}_nonpolymer_entity_{entity_id}.json",
        )


def download_entry(dataset_slug: str, pdb_id: str) -> dict:
    out_dir = ROOT / "data" / dataset_slug / "rcsb" / pdb_id.lower()
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []
    for resource in base_resources(pdb_id):
        result = save_resource(resource, out_dir)
        manifest.append(result)
        print(f"{dataset_slug} {pdb_id} {resource.name}: {'ok' if result['ok'] else 'failed'}")

    entry = read_json(out_dir / f"{pdb_id.upper()}_entry.json")
    for resource in metadata_resources(pdb_id, entry):
        result = save_resource(resource, out_dir)
        manifest.append(result)
        print(f"{dataset_slug} {pdb_id} {resource.name}: {'ok' if result['ok'] else 'failed'}")

    manifest_path = out_dir / f"{pdb_id.upper()}_download_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return {
        "dataset": dataset_slug,
        "pdb_id": pdb_id.upper(),
        "directory": str(out_dir.relative_to(ROOT)),
        "ok": sum(1 for item in manifest if item["ok"]),
        "failed": sum(1 for item in manifest if not item["ok"]),
        "manifest": str(manifest_path.relative_to(ROOT)),
    }


def main() -> int:
    all_summaries = []
    for dataset_slug, spec in DATASETS.items():
        for pdb_id in spec["pdb_ids"]:
            all_summaries.append(download_entry(dataset_slug, pdb_id))

    summary_path = ROOT / "data" / "allosteric_challenge_rcsb_download_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(all_summaries, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(all_summaries, indent=2, ensure_ascii=False))
    return 0 if all(item["failed"] == 0 for item in all_summaries) else 1


if __name__ == "__main__":
    sys.exit(main())
