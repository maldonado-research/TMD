#!/usr/bin/env python3
"""Independent, offline standard-library check of the small drift audit.

Reads pinned inputs and derived outputs; writes only REVIEW_RECEIPT.json.
Does not import or run the audit implementation or any upstream analysis code.
"""
import base64
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parent


def load_json(path):
    return json.loads(path.read_text())


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def numeric_integer(value):
    number = float(value)
    assert math.isfinite(number) and number.is_integer(), value
    return int(number)


def pair_summary(pairs):
    scores = [(a - b) ** 2 / (a + b) for a, b in pairs]
    return {
        "paired_count": len(scores),
        "mean_pair_Q": math.fsum(scores) / len(scores) if scores else None,
        "median_pair_Q": median(scores) if scores else None,
        "pairs_Q_above_4": sum(score > 4 for score in scores),
        "median_absolute_relative_pair_difference": median(2 * abs(a - b) / (a + b) for a, b in pairs) if pairs else None,
    }


def equal(actual, expected):
    if expected is None:
        assert actual is None or actual == "", (actual, expected)
    elif isinstance(expected, float):
        assert math.isclose(float(actual), expected, rel_tol=1e-13, abs_tol=1e-13), (actual, expected)
    elif isinstance(expected, int):
        assert numeric_integer(actual) == expected, (actual, expected)
    else:
        assert actual == expected, (actual, expected)


def main():
    manifest = load_json(ROOT / "INPUT_MANIFEST.json")
    raw = ROOT / "raw"
    inputs = raw / "inputs"
    tree = load_json(raw / "tree_Genetics.json")
    entries = {entry["path"]: entry for entry in tree["tree"]}
    assert tree["truncated"] is False
    assert tree["sha"] == manifest["source_tree"]
    commit = load_json(raw / "commit_Genetics.json")
    assert commit["sha"] == manifest["source_commit"]
    assert commit["commit"]["tree"]["sha"] == manifest["source_tree"]
    assert any(tag["name"] == "Genetics" and tag["commit"]["sha"] == manifest["source_commit"] for tag in load_json(raw / "tags.json"))
    assert load_json(raw / "repository.json")["private"] is False
    for record in manifest["api_responses"]:
        content = (ROOT / record["file"]).read_bytes()
        assert len(content) == record["bytes"]
        assert hashlib.sha256(content).hexdigest() == record["sha256"]
    reused_evidence = manifest.get("reused_previous_round_evidence", [])
    for record in reused_evidence:
        content = (ROOT / record["file"]).read_bytes()
        assert len(content) == record["bytes"]
        assert hashlib.sha256(content).hexdigest() == record["sha256"]
    for record in manifest["inputs"]:
        content = (ROOT / record["local_file"]).read_bytes()
        assert len(content) == record["bytes"] == entries[record["path"]]["size"]
        assert hashlib.sha256(content).hexdigest() == record["sha256"]
        assert hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest() == record["git_blob_sha1"] == entries[record["path"]]["sha"]
        blob = load_json(raw / "ghapi_blobs" / (record["git_blob_sha1"] + ".json"))
        assert blob["sha"] == record["git_blob_sha1"]
        assert blob["encoding"] == "base64"
        assert base64.b64decode(blob["content"]) == content
    ledger = rows(inputs / "experiments.csv")
    culture_keys = [(record["Name"], numeric_integer(record["Replicate"])) for record in ledger]
    assert len(culture_keys) == len(set(culture_keys))
    cultures = dict(zip(culture_keys, ledger))
    batches = {}
    pair_groups = defaultdict(list)
    line_rows = Counter()
    line_missing = Counter()
    meta_keys, cfu_keys, batch_keys = [], [], []
    blank_count = plate_count = zero_count = 0
    missing_by_day = {}
    day_groups = defaultdict(list)
    day_rows = Counter()
    for path in sorted(inputs.rglob("*_cfus.csv")):
        batch = path.parent.name
        prefix = path.name.removesuffix("_cfus.csv")
        full = rows(path)
        nonblank = [record for record in full if any((value or "").strip() for value in record.values())]
        blanks = len(full) - len(nonblank)
        blank_count += blanks
        local_pairs = []
        missing = Counter()
        first_missing = 0
        for record in nonblank:
            key = (record["Strain"], numeric_integer(record["Replicate"]))
            assert key in cultures
            cfu_keys.append((*key, numeric_integer(record["Day"])))
            batch_day = (batch, numeric_integer(record["Day"]))
            day_rows[batch_day] += 1
            assert math.isfinite(float(record["Dilution"])) and float(record["Dilution"]) > 0
            values = [numeric_integer(record[field]) if record[field].strip() else None for field in ("CFU1", "CFU2")]
            assert all(value is None or value >= 0 for value in values)
            plate_count += sum(value is not None for value in values)
            zero_count += sum(value == 0 for value in values)
            first_missing += values[0] is None
            line = cultures[key]["Line"]
            line_rows[line] += 1
            if values[1] is None:
                missing[numeric_integer(record["Day"])] += 1
                line_missing[line] += 1
            if all(value is not None for value in values) and sum(values) > 0:
                local_pairs.append(tuple(values))
                pair_groups[line].append(tuple(values))
                day_groups[batch_day].append(tuple(values))
        exp_list = rows(path.with_name(prefix + "_exps.csv"))
        keys = [(record["Experiment"], numeric_integer(record["Replicate"])) for record in exp_list]
        assert len(keys) == len(set(keys))
        batch_keys.extend(keys)
        expected_batch = "E3" if batch == "E23" else batch
        assert set(keys) == {key for key, record in cultures.items() if record["Experiment"] == expected_batch}
        metadata = rows(path.with_name(prefix + "_meta.csv"))
        assert len({record["Primer"] for record in metadata}) == len(metadata)
        meta_keys.extend((record["Strain"], numeric_integer(record["Replicate"]), numeric_integer(record["Day"])) for record in metadata)
        batches[batch] = {
            "culture_timecourses": len(keys), "clone_names": len({key[0] for key in keys}),
            "sequencing_metadata_rows": len(metadata), "cfu_csv_rows_including_blank": len(full),
            "blank_formatting_rows_excluded": blanks, "nonblank_cfu_timepoint_rows": len(nonblank),
            "first_plate_missing_rows": first_missing, "second_plate_missing_rows": sum(missing.values()),
            **pair_summary(local_pairs),
        }
        missing_by_day[batch] = dict(sorted(missing.items()))
    assert Counter(batch_keys) == Counter(culture_keys)
    assert set(meta_keys) == {(*key, day) for key in cultures for day in range(5)} | {("R", 1, -1)}
    assert len(meta_keys) == len(set(meta_keys))
    assert set(cfu_keys) == {(*key, day) for key in cultures for day in range(4)}
    assert len(cfu_keys) == len(set(cfu_keys))
    all_pairs = [pair for pairs in pair_groups.values() for pair in pairs]
    expected = {
        "clone_names": len({key[0] for key in cultures}), "culture_timecourses": len(cultures),
        "evolved_clone_names": len({key[0] for key, item in cultures.items() if item["Line"] != "all"}),
        "ancestor_clone_names": len({key[0] for key, item in cultures.items() if item["Line"] == "all"}),
        "evolutionary_population_count": len({item["Line"] for item in cultures.values()} - {"all"}),
        "sequencing_metadata_rows": len(meta_keys), "sequencing_metadata_rows_days_0_through_4": sum(key[2] >= 0 for key in meta_keys),
        "preassay_sequencing_metadata_rows": sum(key[2] < 0 for key in meta_keys),
        "cfu_timepoint_rows": len(cfu_keys), "blank_formatting_rows_excluded": blank_count,
        "measured_plate_counts": plate_count, "observed_zero_plate_counts": zero_count,
        "first_plate_missing_rows": sum(record["first_plate_missing_rows"] for record in batches.values()),
        "second_plate_missing_rows": sum(line_missing.values()),
    }
    output = load_json(ROOT / "derived" / "summary.json")
    assert output["source_commit"] == manifest["source_commit"]
    assert output["evolutionary_population_labels_excluding_ancestor"] == sorted({item["Line"] for item in cultures.values()} - {"all"})
    assert output["clone_replicate_distribution"] == {str(reps): clones for reps, clones in sorted(Counter(Counter(key[0] for key in cultures).values()).items())}
    assert output["matched_WAM_ledgers_admitted"] == 0
    assert not any(output["eligibility"].values())
    for key, value in expected.items():
        equal(output[key], value)
    for key, value in pair_summary(all_pairs).items():
        equal(output["paired_CFU_diagnostic"][key], value)
    batch_output = rows(ROOT / "derived" / "batch_measurement_audit.csv")
    assert Counter(record["batch_directory"] for record in batch_output) == Counter(batches.keys())
    for record in batch_output:
        for key, value in batches[record["batch_directory"]].items():
            equal(record[key], value)
    day_output = rows(ROOT / "derived" / "batch_day_measurement_audit.csv")
    assert Counter((record["batch_directory"], numeric_integer(record["day"])) for record in day_output) == Counter(day_rows.keys())
    for record in day_output:
        batch_day = (record["batch_directory"], numeric_integer(record["day"]))
        equal(record["cfu_timepoint_rows"], day_rows[batch_day])
        equal(record["second_plate_missing_rows"], missing_by_day[batch_day[0]].get(batch_day[1], 0))
        for key, value in pair_summary(day_groups[batch_day]).items():
            equal(record[key], value)
    population_output = rows(ROOT / "derived" / "population_measurement_audit.csv")
    assert Counter(record["line_label"] for record in population_output) == Counter(line_rows.keys())
    for record in population_output:
        line = record["line_label"]
        equal(record["clone_names"], len({key[0] for key, item in cultures.items() if item["Line"] == line}))
        equal(record["culture_timecourses"], sum(item["Line"] == line for item in cultures.values()))
        equal(record["cfu_timepoint_rows"], line_rows[line])
        equal(record["second_plate_missing_rows"], line_missing[line])
        for key, value in pair_summary(pair_groups[line]).items():
            equal(record[key], value)
    receipt = {
        "review_kind": "Internal independent computational and source-methods review; not external peer review",
        "source_commit": manifest["source_commit"], "source_tree": manifest["source_tree"],
        "network_access_performed_by_reviewer": False, "upstream_analysis_executed": False,
        "raw_api_response_hashes_verified": len(manifest["api_responses"]), "selected_input_content_identities_verified": len(manifest["inputs"]),
        "reused_method_license_evidence_hashes_verified": len(reused_evidence),
        "aggregate_comparisons_passed": True, "independent_totals": expected,
        "paired_CFU_diagnostic": pair_summary(all_pairs), "second_plate_missing_rows_by_batch_day": missing_by_day,
        "exposure_evidence": ["Pinned HMM treats CFU1/CFU2 as integer raw counts, not counts multiplied by dilution rate", "Both plates use the same intended Nb[t]*D[t] mean in pinned HMM", "Manuscript P40 generally prescribes independently repeated twice 1:100 dilution then 100 microliter plating"],
        "interpretation_limits": ["CSV files have one dilution field per pair, without per-plate realized dilution or volume measurements", "Poisson benchmark 1 requires independent equal-mean raw counts; exposure error can elevate Q", "Complete pairs exclude 62 missing second plates and are unevenly represented by batch and day", "33 clone labels and 67 culture courses share two sampled evolutionary population histories", "Pair Q is not a drift variance, an unbiased overdispersion estimate, a route-specific establishment measurement, or a WAM/recovery trial ledger", "No p-values or confidence intervals treating 206 pairs as independent", "No raw reads, barcode trajectories, posterior samples, or full inference reproduction reviewed"],
        "license_scope": "Zenodo version record 21431098 describes Genetics as CC-BY-4.0; GitHub release lacks a license file. Archive contents were not downloaded or hash-linked. Public accessibility alone is not a blanket redistribution license.",
        "substantive_computational_failures_found": [],
    }
    audit_files = [ROOT / name for name in ("INPUT_MANIFEST.json", "fetch_public_inputs.py", "audit_summaries.py", "derived/summary.json", "derived/batch_measurement_audit.csv", "derived/batch_day_measurement_audit.csv", "derived/population_measurement_audit.csv", "verify_review.py", "DRIFT_AUDIT_2026-10-01.md", "INDEPENDENT_REVIEW.md")]
    audit_files += [ROOT.parent / "literature/raw/drift_preprint_pmc.xml", ROOT.parent / "literature/raw/drift_zenodo_21431096.json"]
    receipt["reviewed_file_sha256"] = {str(path.relative_to(ROOT.parent)): hashlib.sha256(path.read_bytes()).hexdigest() for path in audit_files}
    (ROOT / "REVIEW_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"verification": "passed", "selected_inputs": len(manifest["inputs"]), "paired_CFU": len(all_pairs), "mean_Q": pair_summary(all_pairs)["mean_pair_Q"]}))


if __name__ == "__main__":
    main()
