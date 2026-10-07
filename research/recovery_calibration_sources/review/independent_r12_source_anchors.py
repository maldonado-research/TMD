#!/usr/bin/env python3
"""Check quantitative source anchors in separately read R12 primary XML.

Source acquisition is not performed here. Primary XML snapshots must exist
locally and match the accepted acquisition hashes before downstream use.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


SOURCE_ANCHORS = {
    "PMC13228076.xml": {
        "doi": "10.1128/spectrum.03910-25",
        "sha256": "01474346220301ca3803e1db4150b8e229ceb0e95b1980faca20b389d4661f6e",
        "facts": {
            "paired_samples": "Seventy-two clinical urine samples",
            "pellet_volume": "10 mL of urine was centrifuged at 3,000",
            "resuspension_volume": "pellet was resuspended in 1 mL of 0.1% DTT solution",
            "pretreatment_duration": "15 min at room temperature under gentle agitation",
            "flow_staining_volume": "10 µL of microbeads were added to 1 mL",
            "flow_acquisition_events": "minimum of 10,000 events",
            "flow_bead_normalization": "calculated by normalizing the number of total beads counted",
            "plating_volume": "1 µL of each DTT-treated and untreated suspension",
            "plate_readout": "incubated for 12 h at 37°C",
            "negative_threshold": "Plates yielding <10 CFU/mL were interpreted as negative",
            "species_identity_limit": "species-level identification was not systematically performed",
            "zero_log_handling": "For culture-negative samples (CFU = 0), a constant value of 1 CFU was added",
            "cross_method_denominators": "N = 69 for No-DTT (three samples) and N = 71 for +DTT (one sample)",
            "all_pair_retention": "All 72 pairs were retained for within-method comparisons",
            "raw_supplement_exists": "Raw paired FACS and culture data used for all statistical analyses are provided in Data set S1",
            "pretreatment_medians": "10 CFU/mL (No DTT) to 5.5 × 10³ CFU/mL (+DTT)",
            "viability_medians": "7.45 × 10³ (No DTT) and 7.72 × 10³ (+DTT)",
            "correlation_untreated": "Pearson r = 0.45; Spearman ρ = 0.48",
            "correlation_treated": "Pearson r = 0.44; Spearman ρ = 0.47",
            "VBNC_limit": "do not directly demonstrate the presence of VBNC subpopulations",
        },
    },
    "PMC13272224.xml": {
        "doi": "10.1007/s00203-026-04995-3",
        "sha256": "d46d998f6aa4d84fbb23b49fb201c260068b4b459a23a71a037eea54cb2b284e",
        "facts": {
            "PA14_reference": "Pseudomonas aeruginosa PA14 reference strain",
            "antibiotic_factor": "30 × MIC imipenem (60 µg/mL) or ciprofloxacin (3.75 µg/mL)",
            "culture_volume": "resuspended in 50 mL of LB",
            "sampled_volume": "1 mL samples were collected at 0, 2, 4, 6, 8, 12, and 24 h",
            "wash_and_plate": "washed to remove residual antibiotic, serially diluted in 0.9% saline",
            "recovered_growth_period": "transferred to LB medium for 24 h at 37 °C",
            "flow_redox_stain": "BacLight™ RedoxSensor™ Green Vitality Kit",
            "flow_rescaled_suspension": "resuspended in filtered PBS to an OD 600nm of 0.1",
            "flow_fixed_cells": "fixed with 2% formaldehyde for 20 min",
            "variable_flow_events": "between 1,000 and 50,000 events recorded per sample",
            "relative_flow_normalization": "percentage of cells was normalized based on the gated percentage and the initial inoculum",
            "MIC_evidence": "MIC assays confirmed the absence of acquired resistance",
            "minimum_biological_replicates": "at least three independent biological replicates",
        },
    },
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\u00a0", " ").replace("\u2009", " ").replace("\u202f", " ")).strip()


def run(base: Path):
    records = []
    checks = 0
    for filename, expected in SOURCE_ANCHORS.items():
        path = base / filename
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != expected["sha256"]:
            raise RuntimeError(f"Frozen source hash mismatch: {filename}")
        checks += 1
        root = ET.fromstring(payload)
        whole = normalize(" ".join(root.itertext()))
        title = normalize("".join(root.find(".//article-title").itertext()))
        if expected["doi"] not in whole:
            raise RuntimeError(f"DOI mismatch: {filename}")
        checks += 1
        licenses = root.findall(".//license")
        license_text = " ".join(" ".join(x.itertext()) for x in licenses)
        if "creativecommons.org/licenses/by/4.0" not in license_text:
            raise RuntimeError(f"CC-BY-4.0 license not found: {filename}")
        checks += 1
        checked = {}
        for key, anchor in expected["facts"].items():
            normalized = normalize(anchor)
            if normalized not in whole:
                raise RuntimeError(f"Missing source anchor {filename}: {key}: {normalized}")
            checks += 1
            checked[key] = normalized
        records.append({"filename": filename, "title": title, "doi": expected["doi"],
                        "byte_size": len(payload), "sha256": hashlib.sha256(payload).hexdigest(),
                        "license": "CC-BY-4.0", "anchors": checked})
    return {"status": "PASS", "source_files": len(records), "exact_source_anchor_checks": checks,
            "primary_source_records": records,
            "limits": ["source-text checks, not a reanalysis of sample-level data", "supplement raw data unacquired by this reviewer", "no empirical recovery probability transferred to TMD", "correlation or ratios of medians are not capture calibration", "membrane integrity is not independent confirmation of VBNC"]}


def main():
    if sys.flags.optimize:
        raise SystemExit("Refusing optimized Python: source review guards must remain active.")
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    receipt = run(args.source_dir)
    receipt["oracle_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": receipt["status"], "source_files": receipt["source_files"], "exact_source_anchor_checks": receipt["exact_source_anchor_checks"]}, sort_keys=True))


if __name__ == "__main__":
    main()
