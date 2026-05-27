# Quantum Challenge Context

Glossary for the Cleveland Clinic quantum AI challenge workflow in this repository. This file defines domain language only; implementation decisions belong in scripts, workflow docs, or ADRs.

## Language

**Blind feature extraction**:
Model input construction from challenge input structures and permitted metadata only. Validation structures, validation ligands, and validation-derived labels are excluded.
_Avoid_: blind prediction when referring specifically to feature construction

**Validation scoring**:
Evaluation performed after blind predictions already exist, using validation contact labels or other declared validation targets.
_Avoid_: feature extraction, training signal

**Input structure**:
The PDB structure declared as the challenge input for a dataset. It may contain cofactors or ligands in the source artifact, so permitted use must be decided explicitly.
_Avoid_: apo structure when the checked-in source artifact contains bound components

**Validation ligand contact label**:
Residues in a validation structure that contact the declared validation ligand under the chosen distance cutoff. These labels are for scoring only.
_Avoid_: blind input feature, seed residue

**Active-site seed**:
Residues used as the perturbation starting set for active-site-aware allosteric propagation methods.
_Avoid_: allosteric label, validation seed

## Flagged Ambiguities

**Apo structure**:
The challenge prose describes inputs as apo/unbound, but checked-in RCSB artifacts can contain bound components. Use **input structure** for the artifact and decide component permissions explicitly.

## Example Dialogue

Dev: "Can I use the validation ligand contacts to build the graph?"

Domain expert: "No. The graph is blind feature extraction from the input structure. Validation ligand contact labels are only read during validation scoring."

Dev: "Can the Ohm-style method start from active-site residues?"

Domain expert: "Yes, if the active-site seed comes from permitted input-structure evidence or external biological prior, and the run metadata records that source."
