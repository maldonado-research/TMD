#!/usr/bin/env python3
"""Offline, standard-library replay of SLST Table 1 and bounded archive metadata.

This reads source files as data. It fetches nothing and executes no author code.
Source hashes pin the exact representations inspected on 2026-11-05.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

JATS_SHA256 = "8e86d14d30a55fa672ec950379d03a7d3b57df2ece2ea297f2b5720fb09c7cb4"
METADATA_HASHES = {
    "bioproject_record.xml": "2048b8e9fbd8a21d290bdb6606319655382dd7dbfaa6d472eb7272f87db8ccf8",
    "bioproject_nuccore_links.json": "b72572bfe8470325723e184f4c27c6e4d4fa82e6f4e8eaa38479f802955d4fcd",
    "bioproject_sra_links.json": "56a48802d44c00bd2c341a003ecd4de1fa0bc61191edb852f9332edb75632338",
    "tls_master.gb": "725b7cc48cf1babb979024d5c32f9fd6aaeefe8e3f02c303ce5966ff11d7af81",
    "biosample_first_six.xml": "579211c1d1870b8a0f794a2a64d2e36d22bb4323f3a76174fe1363f3d248a884",
    "biosample_remaining_100.xml": "d8334a4abf605a14aaea1e5da11242f3e619e8fe19d7e69305460c7161e95bee",
    "tls_first_sequence.gb": "fbdad7765dab40dfcae37412e22bd72dd0c12caf069a12ca0afb0a2e2ce55c11",
}
HEADERS = [
    "Mix", "Sequenced read pairs (M)", "Full-length SLST sequences reconstructed",
    "Sequences assigned to any SLST type", "Sequences assigned to expected SLST types",
    "% assigned (of total)", "% assigned expected (of total)",
    "Bray-curtis similarity (observed vs. expected)",
]
EXPECTED_ROWS = [
    ["FixedMix", "1.1", "8192", "7639", "7634", "93.2", "93.2", "0.939"],
    ["StaggeredMix-L1", "1.2", "7732", "7368", "7367", "95.3", "95.3", "0.976"],
    ["StaggeredMix-G1", "1.1", "7043", "6739", "6739", "95.7", "95.7", "0.983"],
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pinned(path, digest):
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == digest, f"Hash mismatch: {path.name}")
    return data


def normalized(node):
    return " ".join("".join(node.itertext()).split())


def ratio(numerator, denominator):
    return {
        "numerator": numerator, "denominator": denominator,
        "reduced_fraction": str(Fraction(numerator, denominator)),
    }


def source_replay(path):
    raw = pinned(path, JATS_SHA256)
    require(len(raw) == 126193, "Unexpected JATS byte length")
    root = ET.fromstring(raw)
    table = root.find(".//table-wrap[@id='T1']")
    require(table is not None, "Missing Table 1")
    rows = [[normalized(cell) for cell in tr] for tr in table.iter("tr")]
    require(rows[0] == HEADERS, "Table 1 column labels differ")
    require(rows[1:] == EXPECTED_ROWS, "Table 1 rows differ")
    output = []
    for row in rows[1:]:
        total, assigned, expected = map(int, row[2:5])
        unassigned, off_set = total - assigned, assigned - expected
        require(0 <= expected <= assigned <= total, "Counts do not nest")
        require(expected + off_set + unassigned == total, "Partition does not sum")
        for count, published in [(assigned, row[5]), (expected, row[6])]:
            require(abs(Fraction(100 * count, total) - Fraction(published)) <= Fraction(1, 20),
                    "Published percentage is inconsistent with rounding")
        output.append({
            "source_row": dict(zip(HEADERS, row)),
            "observed_reconstructed_sequences": total,
            "assigned_to_expected_set": expected,
            "assigned_outside_expected_set": off_set,
            "unassigned_after_reconstruction": unassigned,
            "rates": {
                "expected_set_among_reconstructed": ratio(expected, total),
                "outside_expected_set_among_reconstructed": ratio(off_set, total),
                "unassigned_among_reconstructed": ratio(unassigned, total),
                "expected_set_among_assigned": ratio(expected, assigned),
            },
        })
    anchors = {
        "s2_1": "an average of 93% of sequences were correctly assigned",
        "s4_2": "Each defined mixture (FixedMix, StaggeredMix-L1 and StaggeredMix-G1) was prepared and sequenced in triplicate",
        "s4_6": "Families supported by ≥50 reads were assembled",
        "s5": "KJKS01000000",
    }
    for section, phrase in anchors.items():
        node = root.find(f".//sec[@id='{section}']")
        require(node is not None and phrase in normalized(node), f"Missing anchor {section}")
    return {
        "status": "PASS", "doi": "10.3389/fcimb.2026.1807759", "pmcid": "PMC13231282",
        "jats_bytes": len(raw), "jats_sha256": JATS_SHA256, "table_id": "T1",
        "rows": output, "section_anchors_checked": list(anchors),
        "interpretation": {
            "denominator": "Observed full-length SLST sequences reconstructed; excludes failures before this stage.",
            "expected_set_is_correct_per_true_type": False,
            "why_not": "Calls to another type inside the expected mixture set remain in the expected-set count.",
            "known_introduced_cell_denominator_obtained": False,
            "classwise_correct_call_lower_bounds_obtained": False,
        },
    }


def metadata_replay(directory):
    data = {name: pinned(directory / name, digest) for name, digest in METADATA_HASHES.items()}
    master = data["tls_master.gb"].decode()
    listed = re.findall(r"SAMN\d+", master)
    require(len(listed) == len(set(listed)) == 106, "Unexpected master BioSample list")
    require("KJKS01000001-KJKS01338437" in master, "Unexpected TLS accession range")
    records = []
    for name in ["biosample_first_six.xml", "biosample_remaining_100.xml"]:
        for node in ET.fromstring(data[name]).iter("BioSample"):
            sample_names = [i.text for i in node.iter("Id") if i.get("db_label") == "Sample name"]
            require(len(sample_names) == 1, "Expected one sample name")
            attrs = {a.get("attribute_name"): a.text for a in node.iter("Attribute")}
            records.append({"accession": node.get("accession"), "sample_name": sample_names[0],
                            "isolate": attrs.get("isolate"), "isolation_source": attrs.get("isolation_source")})
    require(len(records) == 106 and {r["accession"] for r in records} == set(listed),
            "Retrieved metadata does not exactly cover master BioSample list")
    groups = Counter()
    for record in records:
        name = record["sample_name"]
        if name.startswith("FixedMix_"): group = "FixedMix"
        elif name.startswith("StaggeredMix-G1_"): group = "StaggeredMix-G1"
        elif name.startswith("StaggeredMix-L1_"): group = "StaggeredMix-L1"
        elif name.startswith("Mock_run-"): group = "Mock"
        elif name.startswith("SpikeMix-"): group = "SpikeMix"
        elif record["isolate"].startswith("Patient_"): group = "clinical"
        else: group = "other"
        groups[group] += 1
    require(dict(groups) == {"FixedMix": 2, "StaggeredMix-G1": 2, "StaggeredMix-L1": 2,
                             "Mock": 12, "SpikeMix": 40, "clinical": 48}, "Unexpected sample roster")
    sra = json.loads(data["bioproject_sra_links.json"])
    require(all(not s.get("linksetdbs") for s in sra["linksets"]), "SRA link response differs")
    nuccore = json.loads(data["bioproject_nuccore_links.json"])
    require(nuccore["linksets"][0]["linksetdbs"][0]["links"] == ["3279182772"], "TLS link differs")
    return {
        "status": "PASS", "bioproject": "PRJNA1422617", "master_accession": "KJKS00000000.1",
        "tls_version": "01", "sequence_accession_range": "KJKS01000001-KJKS01338437",
        "master_reported_sequence_records": 338437, "listed_biosamples": 106,
        "retrieved_biosamples": 106, "groups_by_sample_name_and_isolate": dict(sorted(groups.items())),
        "sample_records": records, "source_sha256": METADATA_HASHES,
        "figure2_single_isolate_controls_identified_in_this_roster": 0,
        "negative_controls_identified_in_this_roster": 0,
        "sra_links_returned_for_bioproject": 0,
        "coverage_issue": "Two named samples per defined mixture appear here; Methods s4_2 says triplicate. The bounded archive roster does not resolve this difference.",
        "scope": "All BioSamples listed by this TLS master were inspected, plus one sequence record. This is not an exhaustive search of all deposits or an analysis of the 338437 sequences.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Pinned original SLST JATS XML")
    parser.add_argument("--metadata-dir", type=Path, help="Optional directory of pinned official metadata")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = {"schema_version": 1, "mode": "offline_source_replay",
              "table_replay": source_replay(args.source),
              "metadata_replay": metadata_replay(args.metadata_dir) if args.metadata_dir else
              {"status": "UNRUN_METADATA_NOT_SUPPLIED"},
              "admission": {"native_Wsp_Aws_Mws_controls": 0, "empirical_t_bounds": 0,
                            "author_code_executed": False, "network_requests": 0}}
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"table_replay": report["table_replay"]["status"],
                      "metadata_replay": report["metadata_replay"]["status"]}))


if __name__ == "__main__":
    main()
