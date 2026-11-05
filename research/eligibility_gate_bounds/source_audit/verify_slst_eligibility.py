#!/usr/bin/env python3
"""Replay cached SLST gate thresholds and retained-sample aggregates offline.

Standard library only. Reads data, performs no network requests, and executes no
author code. Raw source files and individual clinical codes are not emitted.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

JATS_SHA256 = "8e86d14d30a55fa672ec950379d03a7d3b57df2ece2ea297f2b5720fb09c7cb4"
METADATA_HASHES = {
    "biosample_first_six.xml": "579211c1d1870b8a0f794a2a64d2e36d22bb4323f3a76174fe1363f3d248a884",
    "biosample_remaining_100.xml": "d8334a4abf605a14aaea1e5da11242f3e619e8fe19d7e69305460c7161e95bee",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pinned(path, digest):
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == digest, f"Hash mismatch: {path.name}")
    return data


def normalized(node):
    require(node is not None, "Missing source node")
    return " ".join("".join(node.itertext()).split())


def fraction(a, b):
    return {"numerator": a, "denominator": b, "exact_fraction": str(Fraction(a, b))}


def article_replay(path):
    raw = pinned(path, JATS_SHA256)
    require(len(raw) == 126193, "JATS byte length differs")
    root = ET.fromstring(raw)
    def para(section, number):
        node = root.find(f".//sec[@id='{section}']")
        require(node is not None, f"Missing section {section}")
        return normalized(node.findall("p")[number - 1])

    blank = para("s2_3", 3)
    m = re.search(r"In the (twelve) negative controls .* maximum number of full-length SLST sequences detected was (\d+)", blank)
    require(m is not None, "Negative-control statement differs")
    n_negative, maximum = {"twelve": 12}[m[1]], int(m[2])
    m = re.search(r"samples yielding fewer than (\d+) sequences .* excluded", blank)
    require(m is not None, "Exclusion comparator differs")
    threshold = int(m[1])
    require(maximum == threshold == 50, "Published maximum and threshold differ")
    require("nuclease-free water processed through the entire workflow" in para("s4_7", 2),
            "Blank-control definition differs")

    # These are endpoint witnesses consistent with the reported maximum, not
    # recovered individual measurements. They establish the identified range.
    low_witness = [maximum] + [0] * (n_negative - 1)
    high_witness = [maximum] * n_negative
    positives = [sum(v >= threshold for v in values) for values in [low_witness, high_witness]]
    require(positives == [1, n_negative], "Boundary witness failed")
    require(all(sum(v > threshold for v in values) == 0 for values in [low_witness, high_witness]),
            "Strict comparator check failed")

    upstream = para("s4_6", 2)
    m = re.search(r"Families supported by ≥(\d+) reads were assembled", upstream)
    require(m is not None and int(m[1]) == 50, "UMI-family filter differs")
    mock = para("s4_7", 1)
    require("positive control" in mock and "2:98 mass ratio" in mock, "Mock definition differs")
    spike = para("s4_2", 3)
    require("50% (SpikeMix-50), 10% (SpikeMix-10), 5% (SpikeMix-5) and 0.5% (SpikeMix-0.5)" in spike,
            "SpikeMix fractions differ")
    require("ten technical replicates" in para("s4_2", 5), "SpikeMix replication differs")

    clinical = para("s2_5", 1)
    m = re.search(r"Overall, (\d+) of (\d+) samples \((\d+)%\) passed", clinical)
    require(m is not None, "Clinical inclusion count missing")
    passed, total, percent = map(int, m.groups())
    require((passed, total, percent) == (48, 60, 80), "Clinical counts differ")
    require("30 healthy volunteers (face and back)" in clinical, "Original sampling frame differs")
    m = re.search(r"final dataset comprised (\d+) face and (\d+) back samples, including (\d+) paired donors, three donors with face samples only, and one donor with a back sample only", clinical)
    require(m is not None, "Retained site or pair counts differ")
    face, back, paired = map(int, m.groups())
    face_only, back_only = 3, 1
    require(face == paired + face_only and back == paired + back_only and face + back == passed,
            "Retained roster arithmetic failed")
    require("In four donors, both face and back samples were excluded" in clinical and
            "An additional four excluded samples came from the back only" in clinical,
            "Exclusion narrative differs")
    narrative_face, narrative_back = 30 - 4, 30 - 4 - 4
    require((narrative_face, narrative_back) != (face, back), "Site discrepancy no longer present")

    run_main = para("s2_3", 2)
    run_caption = normalized(root.find(".//supplementary-material[@id='SF2']"))
    require("Across twelve independent sequencing runs" in run_main and
            "eleven independent sequencing runs" in run_caption,
            "Mock run-count discrepancy differs")
    st3 = normalized(root.find(".//supplementary-material[@id='ST3']"))
    require("each of the twelve sequencing runs" in st3 and "nuclease-free water" in st3,
            "Supplementary Table 3 caption differs")

    return {
        "status": "PASS", "doi": "10.3389/fcimb.2026.1807759", "pmcid": "PMC13231282",
        "source_sha256": JATS_SHA256, "source_bytes": len(raw),
        "negative_controls": {
            "truth_material": "nuclease-free water; workflow blanks",
            "reported_controls": n_negative,
            "reported_maximum_full_length_sequences_per_control": maximum,
            "literal_sample_exclusion": "full_length_sequence_count < 50",
            "literal_complementary_count_gate": "full_length_sequence_count >= 50",
            "blank_counts_meeting_literal_gate_identified_range": [positives[0], positives[1]],
            "blank_fraction_meeting_literal_gate_identified_range": [fraction(positives[0], n_negative), fraction(positives[1], n_negative)],
            "hypothetical_strict_gt_50_gate_blank_positives": 0,
            "per_control_counts_obtained": False,
            "actual_downstream_inclusion_of_blanks_reported": False,
            "threshold_selected_using_these_controls": True,
            "independent_fixed_gate_validation": False,
            "known_other_biological_trial_denominator": False,
            "anchors": ["s2_3 paragraph 3", "s4_7 paragraph 2", "ST3"],
        },
        "upstream_umi_family_filter": {
            "minimum_reads_per_umi_family": 50,
            "unit": "reads per UMI family, before assembly and full-length locus screening",
            "distinct_from_sample_count_gate": True, "anchor": "s4_6 paragraph 2",
        },
        "background_dna_controls": {
            "mock_target_to_E_coli_DNA_mass_ratio": "2:98",
            "spike_target_DNA_percentages": ["50", "10", "5", "0.5"],
            "spike_technical_replicates_per_condition": 10,
            "all_listed_conditions_contain_target_DNA": True,
            "pure_E_coli_negative_condition_identified_in_this_design": False,
            "known_other_unit_gate_outcome_table_obtained": False,
            "observed_Others_label": "assigned SLST types outside the intended target-type set",
            "DNA_mass_fraction_is_unit_level_gate_false_positive_probability": False,
            "anchors": ["s2_3 paragraphs 1-2", "s4_2 paragraphs 3,5", "s4_7 paragraph 1"],
        },
        "clinical_counts": {
            "original_donors": 30, "original_site_samples": total,
            "retained_site_samples": passed, "excluded_site_samples": total - passed,
            "retained_fraction": fraction(passed, total), "excluded_fraction": fraction(total - passed, total),
            "reported_retained_sites": {"face": face, "back": back},
            "reported_retained_pairing": {"paired": paired, "face_only": face_only, "back_only": back_only},
            "sites_implied_by_preceding_exclusion_narrative": {"face": narrative_face, "back": narrative_back},
            "narrative_and_retained_sites_reconcile": False,
            "total_inclusion_count_reconciles": True,
            "true_target_fraction_or_PPV_identified": False,
            "samples_are_independent_donors": False,
            "anchor": "s2_5 paragraph 1",
        },
        "mock_run_count_wording": {"main_text": 12, "SF2_caption": 11, "reconciled": False},
    }


def metadata_replay(directory, expected_clinical):
    sites, pairing, accessions = Counter(), defaultdict(set), set()
    clinical_records = 0
    for name, digest in METADATA_HASHES.items():
        root = ET.fromstring(pinned(directory / name, digest))
        for node in root.iter("BioSample"):
            accession = node.get("accession")
            require(accession not in accessions, "Duplicate BioSample")
            accessions.add(accession)
            attrs = {a.get("attribute_name"): a.text for a in node.iter("Attribute")}
            isolate = attrs.get("isolate") or ""
            if not isolate.startswith("Patient_"):
                continue
            names = [x.text for x in node.iter("Id") if x.get("db_label") == "Sample name"]
            require(len(names) == 1, "Clinical sample has ambiguous sample name")
            by_name = re.fullmatch(r"(\d+)-(Back|Face)", names[0])
            by_isolate = re.fullmatch(r"Patient_(\d+)_(back|face)", isolate)
            require(by_name is not None and by_isolate is not None, "Clinical site token format differs")
            require(by_name[1] == by_isolate[1] and by_name[2].lower() == by_isolate[2],
                    "Clinical sample name and isolate tokens disagree")
            token, site = by_isolate.groups()
            require(site not in pairing[token], "Duplicate coded subject/site record")
            pairing[token].add(site)
            sites[site] += 1
            clinical_records += 1
    pattern_counts = {
        "paired": sum(s == {"face", "back"} for s in pairing.values()),
        "face_only": sum(s == {"face"} for s in pairing.values()),
        "back_only": sum(s == {"back"} for s in pairing.values()),
    }
    require(len(accessions) == 106, "Cached metadata count differs")
    require(clinical_records == expected_clinical["retained_site_samples"] and
            dict(sites) == expected_clinical["reported_retained_sites"] and
            pattern_counts == expected_clinical["reported_retained_pairing"],
            "Cached clinical roster disagrees with reported retained roster")
    return {
        "status": "PASS", "metadata_records_checked": len(accessions),
        "clinical_samples": clinical_records, "clinical_sites": dict(sorted(sites.items())),
        "unique_coded_subject_tokens": len(pairing), "clinical_pairing": pattern_counts,
        "site_and_subject_tokens_agree_across_sample_name_and_isolate_fields": True,
        "individual_clinical_tokens_or_identities_emitted": False,
        "source_sha256": METADATA_HASHES,
        "scope": "Aggregate of the previously acquired 106 master-linked BioSample records; no new network inventory.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--metadata-dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    article = article_replay(args.source)
    result = {
        "schema_version": 1, "mode": "offline_source_replay",
        "article": article,
        "metadata": metadata_replay(args.metadata_dir, article["clinical_counts"]) if args.metadata_dir else {"status": "UNRUN_METADATA_NOT_SUPPLIED"},
        "admission": {"native_eligibility_false_entry_bound": None,
                      "empirical_target_prevalence_bound": None,
                      "independent_known_other_calibration_trials_admitted": 0,
                      "network_requests": 0, "author_code_executed": False},
    }
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
