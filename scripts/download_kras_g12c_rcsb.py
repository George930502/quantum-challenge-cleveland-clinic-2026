#!/usr/bin/env python3
"""Download KRAS G12C challenge structures and RCSB metadata.

The Cleveland Clinic challenge uses 4OBE as the KRAS input structure and
6OIM as the validation structure for the AMG 510/Sotorasib Switch-II pocket.
This script keeps the download step reproducible and records a manifest with
source URLs, byte sizes, and HTTP status for every fetched artifact.
"""

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
DATA_ROOT = ROOT / "data" / "kras_g12c" / "rcsb"
PDB_IDS = ("4OBE", "6OIM")


@dataclass(frozen=True)
class Resource:
    name: str
    url: str
    filename: str
    binary: bool = True
    decompress_gzip: bool = False


def request_bytes(url: str, timeout: int = 45) -> tuple[int, bytes, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "quantum-challenge-kras-g12c-dataset/1.0",
            "Accept": "*/*",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        status = getattr(resp, "status", 200)
        final_url = resp.geturl()
        return status, resp.read(), final_url


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
    except Exception as exc:  # noqa: BLE001 - manifest should capture download failures.
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
            f"https://files.rcsb.org/validation/view/{lower}_full_validation.pdf.gz",
            f"{pid}_full_validation.pdf.gz",
        ),
    ]


def json_from_path(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


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


def download_entry(pdb_id: str) -> dict:
    out_dir = DATA_ROOT / pdb_id.lower()
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []

    for resource in base_resources(pdb_id):
        result = save_resource(resource, out_dir)
        manifest.append(result)
        print(f"{pdb_id} {resource.name}: {'ok' if result['ok'] else 'failed'}")

    entry = json_from_path(out_dir / f"{pdb_id.upper()}_entry.json")
    for resource in metadata_resources(pdb_id, entry):
        result = save_resource(resource, out_dir)
        manifest.append(result)
        print(f"{pdb_id} {resource.name}: {'ok' if result['ok'] else 'failed'}")

    manifest_path = out_dir / f"{pdb_id.upper()}_download_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return {
        "pdb_id": pdb_id.upper(),
        "directory": str(out_dir.relative_to(ROOT)),
        "ok": sum(1 for item in manifest if item["ok"]),
        "failed": sum(1 for item in manifest if not item["ok"]),
        "manifest": str(manifest_path.relative_to(ROOT)),
    }


def main() -> int:
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    summary = [download_entry(pdb_id) for pdb_id in PDB_IDS]
    summary_path = DATA_ROOT / "kras_g12c_download_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if all(item["failed"] == 0 for item in summary) else 1


if __name__ == "__main__":
    sys.exit(main())
