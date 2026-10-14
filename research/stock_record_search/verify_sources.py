#!/usr/bin/env python3
"""Read-only R31 bounded stock-record source replay. Copyright Ricardo Maldonado; MIT."""
import argparse
import hashlib
import json
from pathlib import Path


def require(ok, message):
    if not ok:
        raise SystemExit(message)


def read(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "Duplicate JSON key")
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def fingerprint(path):
    return {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def derive(cache):
    captures = {n: read(cache / (n + ".json")) for n in ["S01", "S02", "S03", "S04"]}
    responses = {n: c["response"]["structuredContent"] for n, c in captures.items()}
    searches = {n: responses[n]["data"]["web"] for n in ["S01", "S02", "S04"]}
    require([len(searches[n]) for n in ["S01", "S02", "S04"]] == [7, 4, 4], "Search result count changed")
    combined = " ".join(str(r.get(k, "")) for r in searches["S01"] for k in ["title", "description", "url"])
    require(all(x not in combined for x in ["MPB10583", "MPB10613"]), "Combined-query target hit changed")
    thesis_url = "https://mro.massey.ac.nz/bitstreams/906926b8-2806-41a6-858a-706290e9a2e9/download"
    require(searches["S02"][0]["url"] == thesis_url, "Named thesis discovery changed")
    require(searches["S04"][0]["url"] == "https://www.biorxiv.org/content/10.1101/2025.04.29.651346v2.full.pdf", "Known preprint excerpt changed")
    require("rspb20252004_si_001.pdf" in searches["S04"][2]["url"], "Known supplement excerpt changed")
    require(all("smerp.com.br" in searches["S04"][i]["url"] for i in [1, 3]), "Identifier-collision result changed")
    source = responses["S03"]
    m, meta = source["markdown"], source["metadata"]
    require(meta["numPages"] == 180 and meta["totalPages"] == 197, "Partial-source coverage changed")
    anchors = [
        "Michael Joseph McDonald", "reconstructions of the AWS, WST, MWS and WSR WS genotypes",
        "two \nmutant alleles (G3247A and T2183C) were recombined into the ancestral genome",
        "| WSR | mwsR | T2183C | V272A | This study |",
        "| WST | awsX | Δ 229-261 | ⊗YTDDLIKGTTQ | This study |",
        "| MWS | mwsR | G3247A | E1083K | This study |",
        "| WSXb | ? | ? | ? | This study |",
        "WSX vs. SM *mwsR* T2183C", "MWS vs. SM *mwsR* G3260A",
        "(LSWS) genotype (PR1200 (previously named PBR663))",
        "All bacterial strains created in this work are archived", "### 7.1.2 BACTERIAL STRAINS",
        "The thesis may not be reproduced elsewhere without",
    ]
    require(all(a in m for a in anchors), "A thesis source anchor changed")
    require(all(x not in m for x in ["MPB10583", "MPB10613"]), "Target MPB occurrence requires reassessment")
    return {
        "schema_version": 1, "round": "R31",
        "searches": {
            "S01": {"result_count": 7, "exact_target_identifier_in_returned_excerpt_or_url": False, "assessment": "off_target_inconclusive"},
            "S02": {"result_count": 4, "new_primary_lead": "McDonald2009_Massey_thesis"},
            "S04": {"result_count": 4, "known_source_excerpts": 2, "unrelated_identifier_collision_excerpts": 2, "new_stock_record_acquired": False}},
        "thesis": {
            "author": "Michael Joseph McDonald", "year": 2009,
            "source_url": thesis_url, "representation": "provider_markdown_partial_PDF",
            "reported_pages_acquired": 180, "reported_total_PDF_pages": 197,
            "chapter2_author_contribution_reconstructions": ["AWS", "WST", "MWS", "WSR"],
            "reported_ancestral_replacement_alleles": ["G3247A", "T2183C"],
            "Table2_1_WSR": "mwsR T2183C / V272A", "Table2_1_WST": "awsX Δ229–261 / YTDDLIKGTTQ",
            "Table2_1_MWS": "mwsR G3247A / E1083K", "Table2_1_WSX": "unknown",
            "Figure2_1_caption_T2183C_comparison_label": "WSX",
            "Figure2_1_caption_MWS_reconstruction_label": "G3260A",
            "reported_LSWS_alias": "PR1200 (previously named PBR663)",
            "historical_created_strains_archiving_declaration": True,
            "target_MPB_identifier_occurrences_in_acquired_text": 0,
            "current_stock_or_custody_crosswalk_authenticated": False,
            "author_correction_acquired": False,
            "provider_figure_numbers_admitted_as_data": False},
        "stock_sequences_authenticated": 0, "matched_panels_admitted": 0,
        "absence_of_records_everywhere_established": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-cache", type=Path)
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    root = package.parents[1]
    names = read(package / "PUBLIC_FILES.json")["public_files"]
    require(len(names) == len(set(names)) == 11 and all(Path(n).name == n for n in names), "Unsafe allowlist")
    require(all(f.is_file() and not f.is_symlink() for f in package.iterdir()), "Unexpected package entry")
    require(set(f.name for f in package.iterdir()) == set(names), "Package allowlist drift")
    sums = {}
    for line in (package / "SHA256SUMS.txt").read_text().splitlines():
        digest, name = line.split("  ", 1)
        require(name not in sums and Path(name).name == name, "Unsafe checksum entry")
        sums[name] = digest
    require(set(sums) == set(names) - {"SHA256SUMS.txt"}, "Checksum closure")
    require(all(fingerprint(package / n)["sha256"] == h for n, h in sums.items()), "Checksum mismatch")
    provenance = read(package / "SOURCE_PROVENANCE.json")
    require(len(provenance["calls"]) == provenance["logical_scientific_calls"] == 4, "Call accounting drift")
    require(sum(x["bytes"] for x in provenance["saved_acquisition_files"]) == provenance["saved_acquisition_bytes"] == 666984 <= 8388608, "Byte accounting drift")
    for item in provenance["inherited_dependencies"]:
        require(fingerprint(root / item["path"]) == {k: item[k] for k in ["bytes", "sha256"]}, "Inherited dependency drift")
    study = read(root / "research/prospective_design/REGISTRY_CANDIDATE.json")["study_inputs_requiring_resolution"]
    planning = read(root / "research/native_origin_controls/PROSPECTIVE_CONTROL_FIELDS.json")["actual_values"]
    require(len(study) == 26 and all(x is None for x in study.values()), "Study NULL registry drift")
    require(len(planning) == 18 and all(x is None for x in planning.values()), "Planning NULL registry drift")
    decision = read(package / "DECISION.json")
    require(decision["matched_panels_admitted"] == 0 and decision["stock_sequences_authenticated"] == 0 and not decision["new_biological_fit"], "Admission drift")
    replay = "UNRUN: no source cache supplied"
    if args.source_cache:
        for item in provenance["saved_acquisition_files"]:
            require(Path(item["filename"]).name == item["filename"], "Unsafe source path")
            require(fingerprint(args.source_cache / item["filename"]) == {k: item[k] for k in ["bytes", "sha256"]}, "Source fingerprint mismatch")
        for item in provenance["calls"]:
            capture = read(args.source_cache / item["capture_file"])
            require(all(capture[k] == item[k] for k in ["call_id", "tool", "arguments", "started_utc", "completed_utc"]), "Capture provenance differs")
        require(derive(args.source_cache) == read(package / "DERIVED_SOURCE_AUDIT.json"), "Source replay mismatch")
        replay = "PASS: saved search excerpts and partial thesis anchors"
    print(json.dumps({"status": "PASS", "source_replay": replay,
                      "private_local_scope_replay": "UNRUN: private audit excluded",
                      "study_nulls": 26, "planning_nulls": 18,
                      "matched_panels_admitted": 0, "stock_sequences_authenticated": 0,
                      "biological_validation": "NOT_PERFORMED", "new_biological_fit": False}, indent=2))


if __name__ == "__main__":
    main()
