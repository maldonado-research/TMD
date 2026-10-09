#!/usr/bin/env python3
"""Verify R25 cached official catalogues and replay only summary arithmetic.

Original verification code by Ricardo Maldonado with AI assistance. MIT.
This script performs no network requests and does not infer biological truth.
"""
import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 50
RECORD_ID = "R000025"
ROOTS = ("PMCAHH1-WT", "PMCAHH1-FANCCKO", "PMCAHH1-MSH2KO")
INVENTORIES = (
    ("mendeley_wt_callable_files_firecrawl.json", "PMCAHH1-WT/CallableLoci"),
    ("mendeley_wt_ptato_callable_files_firecrawl.json", "PMCAHH1-WT/PTATO/snvs_callable"),
    ("mendeley_wt_smurf_files_firecrawl.json", "PMCAHH1-WT/PTATO/intermediate/short_variants/SMuRF/PMCAHH1"),
    ("mendeley_fancc_callable_files_firecrawl.json", "PMCAHH1-FANCCKO/CallableLoci"),
    ("msh2_callable_manifest.json", "PMCAHH1-MSH2KO/CallableLoci"),
    ("msh2_snvs_callable_manifest.json", "PMCAHH1-MSH2KO/PTATO/snvs_callable"),
    ("fancc_snvs_callable_manifest.json", "PMCAHH1-FANCCKO/PTATO/snvs_callable"),
)
SUMMARIES = (
    ("mendeley_wt_pta1_callable_summary_firecrawl.json", "66bb4799-66d0-4f7f-8ba9-b7420b5b16b6", "PMCAHH1-WT-C19SC1"),
    ("mendeley_wt_pta2_callable_summary_firecrawl.json", "11a3f9d6-4254-46d4-9018-4c23e62c49c4", "PMCAHH1-WT-C6SC1"),
    ("msh2_pta_callable_summary.json", "10e2ede8-0e3f-49f1-9080-bd43002178fe", "PMCAHH1-MSH2KO-C27E06SC51B06-PTAP1E7"),
)
ROOT_CAPTURES = {"msh2_callable_manifest.json", "msh2_snvs_callable_manifest.json", "fancc_snvs_callable_manifest.json", "msh2_pta_callable_summary.json"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source(cache, filename):
    obj = json.loads((cache / filename).read_bytes())
    if "result" in obj:
        obj = obj["result"]
    assert obj.get("isError") is False, filename
    data = obj["structuredContent"]
    assert data["metadata"]["statusCode"] == 200, filename
    assert data["metadata"]["proxyUsed"] == "basic", filename
    return data["rawHtml"]


def catalogue(cache, filename):
    data = json.loads(source(cache, filename))
    assert isinstance(data, list), filename
    return data


def pin(path):
    data = path.read_bytes()
    return {"cache_filename": path.name, "bytes": len(data), "sha256": sha(data), "redistributed": False}


def check_pin(path, expected):
    data = path.read_bytes()
    assert len(data) == expected["bytes"], str(path) + ": size"
    assert sha(data) == expected["sha256"], str(path) + ": SHA256"


def compute(cache, prior_cache, figure_code, root_cache):
    rows = catalogue(cache, "mendeley_folders_v1_firecrawl.json")
    by_id = {r["id"]: r for r in rows}
    assert len(by_id) == len(rows), "Duplicate folder identifiers"
    paths = {}

    def folder_path(folder_id, ancestors=()):
        assert folder_id not in ancestors, "Folder cycle"
        row = by_id[folder_id]
        parent_id = row.get("parent_id")
        if parent_id:
            assert parent_id in by_id, "Missing folder parent"
            result = folder_path(parent_id, ancestors + (folder_id,)) + "/" + row["name"]
        else:
            result = row["name"]
        paths[folder_id] = result
        return result

    for folder_id in by_id:
        folder_path(folder_id)
    assert len(set(paths.values())) == len(paths), "Duplicate folder paths"
    counts = Counter(path.split("/")[0] for path in paths.values())
    inventory_summaries, file_records, all_files = [], [], {}
    for filename, expected_path in INVENTORIES:
        files = catalogue(root_cache if filename in ROOT_CAPTURES else cache, filename)
        assert 0 < len(files) < 1000, "Requires additional pagination or empty inventory"
        assert len({r["id"] for r in files}) == len(files)
        assert {paths[r["folder_id"]] for r in files} == {expected_path}
        inventory_summaries.append({
            "path": expected_path,
            "folder_id": files[0]["folder_id"],
            "response_cache": filename,
            "direct_file_records": len(files),
            "catalogued_file_bytes": sum(r["content_details"]["size"] for r in files),
            "recursive_file_coverage_claimed": False,
        })
        for row in files:
            assert row["id"] not in all_files, "Duplicate file across scopes"
            all_files[row["id"]] = row
            details = row["content_details"]
            file_records.append({
                "directory": expected_path,
                "filename": row["filename"],
                "id": row["id"],
                "bytes": details["size"],
                "sha256": details["sha256_hash"],
                "view_url": details["view_url"],
                "content_acquired": row["id"] in {item[1] for item in SUMMARIES},
            })
    manifest = {
        "record_id": RECORD_ID,
        "kind": "Observed official directory topology and seven scoped direct-file catalogues",
        "folder_records": len(rows),
        "root_folder_records": sum(not r.get("parent_id") for r in rows),
        "unique_folder_ids": len(by_id),
        "unique_folder_paths": len(set(paths.values())),
        "missing_parents": 0,
        "cycles": 0,
        "scoped_subtree_folder_counts_including_root": {root: counts[root] for root in ROOTS},
        "scoped_file_inventories": inventory_summaries,
        "direct_file_records_total": len(all_files),
        "catalogued_file_bytes_total": sum(r["bytes"] for r in file_records),
        "file_records": file_records,
        "complete_recursive_file_manifest_obtained": False,
        "large_variant_or_locus_inputs_acquired": False,
        "scope_limit": "Folder topology does not enumerate the files inside every folder. Only the seven listed direct-file scopes were fetched by the delegate and root. An inventory is not acquisition or authentication of the listed file content.",
        "fancc_snvs_callable_observation": "The scoped PMCAHH1-FANCCKO/PTATO/snvs_callable inventory returned three summary text files and no VCF. This does not establish absence elsewhere in the dataset.",
    }

    metadata = list(csv.DictReader(io.StringIO((prior_cache / "Table_S2.txt").read_text()), delimiter="\t"))
    figure = figure_code.read_text()
    audit_rows = []
    for filename, file_id, sample in SUMMARIES:
        summary_cache = root_cache if filename in ROOT_CAPTURES else cache
        text = source(summary_cache, filename)
        raw = text.encode("utf-8")
        manifest_row = all_files[file_id]
        official = manifest_row["content_details"]
        assert len(raw) == official["size"]
        assert sha(raw) == official["sha256_hash"]
        if (cache / manifest_row["filename"]).exists():
            assert (cache / manifest_row["filename"]).read_bytes() == raw
        if filename == "msh2_pta_callable_summary.json":
            assert (root_cache / "MSH2_PTA_CallableLoci.txt").read_bytes() == raw
        summary = list(csv.DictReader(io.StringIO(text), delimiter="\t"))
        assert len(summary) == 6
        states = {r["State"]: r for r in summary}
        assert set(states) == {"CALLABLE", "EXCESSIVE_COVERAGE", "LOW_COVERAGE", "NO_COVERAGE", "POOR_MAPPING_QUALITY", "REF_N"}
        total = sum(int(r["nBases"]) for r in summary)
        ref_n = int(states["REF_N"]["nBases"])
        denominator = total - ref_n
        residual = max(abs(Decimal(r["nBases"]) / denominator - Decimal(r["Freq"])) for r in summary)
        assert residual < Decimal("1e-14")
        metadata_row, = [r for r in metadata if r["Sample"] == sample]
        assert metadata_row["Type"] == "PTA"
        pattern = r'Overview_CloneVariants\$ID\[Overview_CloneVariants\$Sample == "' + re.escape(sample) + r'"\] <- "([^"]+)"'
        figure_label, = re.findall(pattern, figure)
        figure_label = figure_label.replace("\\n", "")
        callable_fraction = Decimal(states["CALLABLE"]["Freq"])
        table_fraction = Decimal(metadata_row["CallableLoci"])
        assert callable_fraction.quantize(Decimal("0.0000001")) == table_fraction
        audit_rows.append({
            "metadata_label": metadata_row["Label"],
            "figure_recovery_label": figure_label,
            "labels_agree": figure_label == metadata_row["Label"],
            "table_s2_data_row": metadata.index(metadata_row) + 1,
            "training_flag": metadata_row["Training"],
            "source_file_id": file_id,
            "source_bytes": len(raw),
            "source_sha256": sha(raw),
            "source_summary_rows": len(summary),
            "sum_reported_state_bases": total,
            "ref_n_bases": ref_n,
            "non_ref_n_denominator": denominator,
            "callable_bases": int(states["CALLABLE"]["nBases"]),
            "reported_callable_frequency": str(callable_fraction),
            "computed_callable_frequency": str(Decimal(states["CALLABLE"]["nBases"]) / denominator),
            "table_s2_callable_fraction": metadata_row["CallableLoci"],
            "table_s2_matches_after_rounding_7_decimal_places": True,
            "sum_reported_frequencies": str(sum(Decimal(r["Freq"]) for r in summary)),
            "max_absolute_frequency_residual": str(residual),
        })
    arithmetic = {
        "record_id": RECORD_ID,
        "kind": "Authenticated source-summary arithmetic replay; no genotype or locus-level benchmark",
        "samples": audit_rows,
        "denominator_interpretation": "All six published frequencies, including REF_N, use the sum of the five non-REF_N state counts as denominator. The six frequencies therefore sum to approximately 1.047288195, while the five non-REF_N frequencies sum to approximately one. This arithmetic convention alone is not evidence of a published error.",
        "limits": ["No BED content acquired; interval coverage, coordinate semantics and locus eligibility remain unverified.", "No PTA/SMuRF variant content acquired; genotype recovery, QC denominators and caller comparison remain uncomputed.", "The aggregate denominator was derived from supplied summary counts; it is not independently validated against the reference genome or the locus files.", "Training=No does not establish untouched evaluation or donor-level holdout.", "Native ancestry, inherited/pre-existing origin negatives, mutation events and completeness remain unknown."],
        "genotype_stage_numerical_benchmark_admitted": False,
        "native_origin_benchmark_admitted": False,
        "qualified_external_review_obtained": False,
    }
    return manifest, arithmetic


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", required=True, type=Path)
    parser.add_argument("--prior-cache", required=True, type=Path)
    parser.add_argument("--root-cache", required=True, type=Path)
    parser.add_argument("--figure-code", required=True, type=Path)
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    provenance = json.loads((package / "PROVENANCE.json").read_text())
    for expected in provenance["source_pins"]:
        check_pin(args.cache / expected["cache_filename"], expected)
    for expected in provenance["prior_source_pins"]:
        check_pin(args.prior_cache / expected["cache_filename"], expected)
    for expected in provenance["root_source_pins"]:
        check_pin(args.root_cache / expected["cache_filename"], expected)
    check_pin(args.figure_code, provenance["figure_code_pin"])
    page = json.loads((args.prior_cache / "mendeley_v1_firecrawl.json").read_text())["structuredContent"]["rawHtml"]
    assert provenance["route_derivation"]["bundle_url"] in page
    state = json.JSONDecoder().raw_decode(page.split("window.INITIAL_STATE = ", 1)[1])[0]
    assert state["configClient"]["publicApiBaseUrl"] == "/public-api"
    bundle = source(args.cache, "mendeley_frontend_bundle_firecrawl.json")
    assert "/datasets/${t}/folders/${n}" in bundle
    assert "/datasets/${t}/files?folder_id=${i}&version=${n}&$start=${c}&$limit=1000" in bundle
    manifest, arithmetic = compute(args.cache, args.prior_cache, args.figure_code, args.root_cache)
    assert manifest == json.loads((package / "MANIFEST_AUDIT.json").read_text())
    assert arithmetic == json.loads((package / "CALLABILITY_AUDIT.json").read_text())
    print(json.dumps({"record_id": RECORD_ID, "result": "PASS", "checks": ["Pinned exact cache bytes and SHA256", "Official frontend route derivation", "Acyclic observed folder topology and seven scoped catalogues", "Three source summaries match official size and SHA256", "All summary-frequency denominators replayed", "Rounded Table S2 callability and WT label mismatch retained"], "source_summary_arithmetic_replayed": True, "genotype_stage_numerical_benchmark_admitted": False, "native_origin_benchmark_admitted": False, "qualified_external_review_obtained": False}, indent=2))


if __name__ == "__main__":
    main()
