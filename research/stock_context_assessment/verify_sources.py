#!/usr/bin/env python3
"""Read-only R30 source-context replay. Copyright Ricardo Maldonado; MIT."""
import argparse
import hashlib
import json
import re
from pathlib import Path


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def read(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "Duplicate JSON key: " + key)
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def fingerprint(path):
    return {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def markdown(value):
    if isinstance(value, dict):
        if isinstance(value.get("markdown"), str):
            return value["markdown"]
        if "structuredContent" in value:
            result = markdown(value["structuredContent"])
            if result is not None:
                return result
        for child in value.values():
            result = markdown(child)
            if result is not None:
                return result
    elif isinstance(value, list):
        for child in value:
            result = markdown(child)
            if result is not None:
                return result
    elif isinstance(value, str) and value.lstrip().startswith("{"):
        try:
            return markdown(json.loads(value))
        except json.JSONDecodeError:
            pass
    return None


def derive(cache, root):
    texts = {name: markdown(read(cache / (name + ".json")))
             for name in ["S01", "S02", "S03", "S04", "S05", "R27_supplement", "R28_2009"]}
    require(all(isinstance(s, str) for s in texts.values()), "Missing markdown representation")
    require("is blocked" in texts["S01"], "PDF-wrapper outcome changed")
    article, strains, supplement, calls = [texts[k] for k in ["S02", "S03", "S04", "S05"]]
    require("ten WSs were isolated from independent, 72-hr microcosms" in article,
            "New-isolate sampling context absent")
    require("PRJNA730882" in article and "RefSeq NC\\_012660.1" in article,
            "Reported sequencing reference absent")
    require("| _mwsR_ | _PFLU5329_ | 3 | t2183c | V728A |" in article,
            "Table 2 allele pair absent")
    strain_line = next(line for line in strains.splitlines() if line.startswith("| SBW25-WS3 |"))
    require(all(x in strain_line for x in ["Evolved SBW25", "t2183c", "V728 to A728", "This study"]),
            "Table S1 stock description changed")
    require("| mwsR | 3 | t2183c | g_tc → g_cc | V728A |" in supplement,
            "Text S1 codon context absent")
    line = next(line for line in calls.splitlines() if line.startswith("| SBW25-WS3 |"))
    row = [cell.strip() for cell in line.strip("|").split("|")]
    require(len(row) == 14 and row[6:12] == ["5856845", "mwsR", "pflu5329", "t2183c", "gtc-->gcc", "V728A"],
            "Table S3 summary row changed")
    require(row[12] == "breseq (RA), PCR and Sanger sequencing", "Reported evidence changed")
    block = calls.split("| Mutations called in SBW25-WS3 |", 1)[1].split("| Mutations called in SBW25-WS4 |", 1)[0]
    require("| 4 | 5,856,845 | mwsR (pflu5329) | transition | t-->c | V728A | RA | 100.00% |" in block,
            "Per-isolate call does not support summary row")
    require(all(not re.search(r"(?<![A-Za-z0-9])" + x + r"(?![A-Za-z0-9])", s)
                for x in ["WSR", "MPB10613", "MPB10583"] for s in [strains, supplement, calls]),
            "A target stock token is present; manually reassess alias absence")
    prior = read(root / "research/source_join_resolution/DERIVED_SOURCE_AUDIT.json")["mwsR_coordinate_join"]
    origin = int(row[6]) - int(re.search(r"\d+", row[9]).group()) + 1
    require(origin == prior["historical_implied_genomic_origin"] == 5854663, "Implied origin differs")
    require(int(row[6]) == prior["conditional_genomic_position"], "Prior coordinate differs")
    karita = texts["R27_supplement"]
    aws = next(line for line in karita.splitlines() if line.startswith("| Wrinkly spreader (WS) awsX |"))
    mws = next(line for line in karita.splitlines() if line.startswith("| Wrinkly spreader (WS) mwsR |"))
    require("MPB10583 | 17 |" in aws and "Δ32bp (229-261)" in aws, "Karita awsX literal changed")
    require("MPB10613 | 17 |" in mws and "T2183C" in mws, "Karita mwsR literal changed")
    require("The strains without references were" in karita and "**17.** McDonald" in karita,
            "Karita caption/reference scope changed")
    old = texts["R28_2009"]
    require("| WSR | _mwsR_ | T2183C | V272A |" in old and "| WSX [_b_]" in old,
            "Original Table 1 identities changed")
    require("WSX _vs_. SM _mwsR_ T2183C" in old and "MWS _vs_. SM _mwsR_ G3260A" in old,
            "Original Figure 4 disagreement changed")
    require("| MWS | _mwsR_ | G3247A | E1083K |" in old,
            "Distinct MWS allele changed")
    return {
        "schema_version": 1, "round": "R30",
        "later_primary_study": {
            "doi": "10.1111/mmi.14855", "citation_year": 2022,
            "strain": "SBW25-WS3", "source_type": "evolved isolate, This study",
            "collection_context": "Ten WS isolates from independent 72-hour SBW25-founded microcosms; separate from ten PICF7 WS isolates and ten A506 Web isolates.",
            "reference_as_reported": "NC_012660.1", "reported_read_project": "PRJNA730882",
            "gene": row[7], "locus": row[8], "gene_label": row[9],
            "genome_position_forward": int(row[6]), "codon_change": row[10], "protein_label": row[11],
            "validation_as_reported": row[12],
            "implied_forward_origin": origin,
            "annotation_release_identified_in_acquired_source": False,
            "raw_reads_acquired_or_reanalysed": False,
            "historical_or_MPB_stock_alias_authenticated": False},
        "reference_comparison": {
            "R29_projected_genome_position": prior["conditional_genomic_position"],
            "same_genome_position": True,
            "R29_current_annotation_protein_label": prior["current_protein_consequence"],
            "R29_current_CDS_start_offset_nt": prior["current_CDS_start_offset_nt"],
            "historical_stock_condition_resolved": False},
        "karita_stock_table": {
            "MPB10583_literal": "awsX (PFLU5211) Δ32bp (229-261)",
            "MPB10613_literal": "mwsR (PFLU5329) T2183C",
            "both_rows_reference": "17: McDonald et al. 2009",
            "caption_unreferenced_strain_construction_scope_applies_to_these_rows": False,
            "stock_crosswalk_authenticated": False},
        "historical_source_disagreements": {
            "Table1_WSR": "mwsR T2183C / V272A", "Table1_WSX": "unknown",
            "Figure4_literal_comparison": "WSX vs. SM mwsR T2183C",
            "Table1_MWS": "mwsR G3247A / E1083K",
            "Figure4_literal_MWS_reconstruction": "SM mwsR G3260A",
            "author_correction_acquired": False,
            "WSX_reclassified": False},
        "matched_panels_admitted": 0, "stock_sequences_authenticated": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-cache", type=Path)
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    root = package.parents[1]
    public = read(package / "PUBLIC_FILES.json")["public_files"]
    require(len(public) == len(set(public)) == 12 and all(Path(n).name == n for n in public), "Unsafe allowlist")
    require(all(p.is_file() and not p.is_symlink() for p in package.iterdir()), "Unexpected directory or symlink")
    require(set(p.name for p in package.iterdir()) == set(public), "Package allowlist drift")
    sums = {}
    for line in (package / "SHA256SUMS.txt").read_text().splitlines():
        digest, name = line.split("  ", 1)
        require(name not in sums and Path(name).name == name, "Unsafe sum path")
        sums[name] = digest
    require(set(sums) == set(public) - {"SHA256SUMS.txt"}, "Checksum closure")
    require(all(fingerprint(package / n)["sha256"] == h for n, h in sums.items()), "Checksum mismatch")
    provenance = read(package / "SOURCE_PROVENANCE.json")
    require(len(provenance["calls"]) == provenance["logical_scientific_calls"] == 5 <= 6, "Call accounting drift")
    require(sum(r["bytes"] for r in provenance["saved_acquisition_files"]) == provenance["saved_acquisition_bytes"] <= 8388608, "Byte accounting drift")
    for item in provenance["inherited_dependencies"]:
        require(fingerprint(root / item["path"]) == {k: item[k] for k in ["bytes", "sha256"]}, "Inherited dependency drift")
    study = read(root / "research/prospective_design/REGISTRY_CANDIDATE.json")["study_inputs_requiring_resolution"]
    planning = read(root / "research/native_origin_controls/PROSPECTIVE_CONTROL_FIELDS.json")["actual_values"]
    require(len(study) == 26 and all(v is None for v in study.values()), "Study NULL registry drift")
    require(len(planning) == 18 and all(v is None for v in planning.values()), "Planning NULL registry drift")
    decision = read(package / "DECISION.json")
    require(decision["matched_panels_admitted"] == 0 and not decision["new_biological_fit"], "Admission drift")
    replay = "UNRUN: no source cache supplied"
    if args.source_cache:
        for item in provenance["saved_acquisition_files"] + provenance["reused_source_files"]:
            require(Path(item["filename"]).name == item["filename"], "Unsafe source path")
            require(fingerprint(args.source_cache / item["filename"]) == {k: item[k] for k in ["bytes", "sha256"]}, "Source fingerprint mismatch: " + item["filename"])
        for item in provenance["calls"]:
            capture = read(args.source_cache / item["capture_file"])
            require(all(capture[k] == item[k] for k in ["call_id", "tool", "arguments", "started_utc", "completed_utc"]), "Capture provenance differs")
        require(derive(args.source_cache, root) == read(package / "DERIVED_SOURCE_AUDIT.json"), "Source-context replay mismatch")
        replay = "PASS: captured representations, focal source rows, conditional coordinate comparison and source disagreements"
    print(json.dumps({"status": "PASS", "source_replay": replay, "study_nulls": 26, "planning_nulls": 18,
                      "matched_panels_admitted": 0, "stock_sequences_authenticated": 0,
                      "biological_validation": "NOT_PERFORMED", "new_biological_fit": False}, indent=2))


if __name__ == "__main__":
    main()
