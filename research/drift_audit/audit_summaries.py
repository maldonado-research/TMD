#!/usr/bin/env python3
"""Reproduce replication and CFU measurement audits from SHA-verified small inputs.

Descriptive aggregates only. No mutation-arrival, WAM-recovery or drift fit.
Python standard library, with no network calls and no upstream code execution.
"""
import csv
import hashlib
import io
import json
import statistics
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "raw" / "inputs"
DERIVED = ROOT / "derived"
BATCHES = [("E1", "E1"), ("E23", "E3"), ("E4", "E4"), ("E5", "E5"), ("E6", "E6")]


def integer(value):
    number = Decimal(value)
    if not number.is_finite() or number != number.to_integral_value():
        raise ValueError(f"Noninteger data: {value!r}")
    return int(number)


def read_csv(relative):
    return list(csv.DictReader(io.StringIO((INPUT / relative).read_text(encoding="utf-8-sig"))))


def summarize_pairs(pairs):
    q = [(left - right) ** 2 / (left + right) for left, right in pairs]
    return {
        "paired_count": len(pairs),
        "mean_pair_Q": statistics.mean(q) if q else None,
        "median_pair_Q": statistics.median(q) if q else None,
        "pairs_Q_above_4": sum(value > 4 for value in q),
        "median_absolute_relative_pair_difference": statistics.median(2 * abs(left - right) / (left + right) for left, right in pairs) if pairs else None,
    }


def write_csv(name, rows):
    with (DERIVED / name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    manifest = json.loads((ROOT / "INPUT_MANIFEST.json").read_text())
    for entry in manifest["inputs"]:
        path = ROOT / entry["local_file"]
        data = path.read_bytes()
        if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise ValueError(f"Input hash mismatch: {entry['path']}")
    for entry in manifest.get("reused_previous_round_evidence", []):
        data = (ROOT / entry["file"]).read_bytes()
        if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise ValueError("Reused methods/license evidence hash mismatch")
    experiments = read_csv("experiments.csv")
    cultures = {}
    strains = {}
    for row in experiments:
        name, replicate = row["Name"], integer(row["Replicate"])
        key = name, replicate
        if key in cultures:
            raise ValueError("Duplicate culture in experiments ledger")
        cultures[key] = row
        attributes = {field: row[field] for field in ["Strain", "Name", "Line", "Time point", "Clone"]}
        if name in strains and strains[name] != attributes:
            raise ValueError("Clone attributes disagree across replicates")
        strains[name] = attributes
    by_culture_meta = defaultdict(list)
    by_culture_cfu = defaultdict(list)
    pairs_all = []
    by_line = defaultdict(lambda: {"cfu_rows": 0, "pairs": [], "second_plate_missing_rows": 0})
    batch_summaries = []
    batch_day_summaries = []
    blank_rows = 0
    zero_counts = 0
    for directory, prefix in BATCHES:
        exp_name = "E3" if directory == "E23" else directory
        expected_cultures = {key for key, row in cultures.items() if row["Experiment"] == exp_name}
        listed_cultures = {(row["Experiment"], integer(row["Replicate"])) for row in read_csv(f"{directory}/{prefix}_exps.csv")}
        if expected_cultures != listed_cultures:
            raise ValueError(f"Batch experiment list disagrees with master ledger: {directory}")
        meta = read_csv(f"{directory}/{prefix}_meta.csv")
        if len({integer(row["Primer"]) for row in meta}) != len(meta):
            raise ValueError(f"Duplicate sequencing index within batch: {directory}")
        for row in meta:
            key = row["Strain"], integer(row["Replicate"])
            if key not in expected_cultures:
                raise ValueError("Unknown culture in sequencing metadata")
            by_culture_meta[key].append(integer(row["Day"]))
        cfu = read_csv(f"{directory}/{prefix}_cfus.csv")
        local_pairs = []
        by_day = defaultdict(lambda: {"rows": 0, "pairs": [], "second_missing": 0})
        local_blank = 0
        second_missing = 0
        first_missing = 0
        for row in cfu:
            if not any(value.strip() for value in row.values() if value is not None):
                local_blank += 1
                continue
            key = row["Strain"], integer(row["Replicate"])
            if key not in expected_cultures:
                raise ValueError("Unknown culture in CFU data")
            dilution = Decimal(row["Dilution"])
            if not dilution.is_finite() or dilution <= 0:
                raise ValueError("Invalid dilution")
            by_culture_cfu[key].append(integer(row["Day"]))
            values = [integer(row[field]) if row[field].strip() else None for field in ["CFU1", "CFU2"]]
            if any(value is not None and value < 0 for value in values):
                raise ValueError("Negative colony count")
            zero_counts += sum(value == 0 for value in values if value is not None)
            first_missing += values[0] is None
            second_missing += values[1] is None
            day_values = by_day[integer(row["Day"])]
            day_values["rows"] += 1
            day_values["second_missing"] += values[1] is None
            line = cultures[key]["Line"]
            by_line[line]["cfu_rows"] += 1
            by_line[line]["second_plate_missing_rows"] += values[1] is None
            if None not in values and sum(values) > 0:
                pair = tuple(values)
                local_pairs.append(pair)
                pairs_all.append(pair)
                by_line[line]["pairs"].append(pair)
                day_values["pairs"].append(pair)
        blank_rows += local_blank
        batch_summaries.append({
            "batch_directory": directory,
            "culture_timecourses": len(expected_cultures),
            "clone_names": len({key[0] for key in expected_cultures}),
            "sequencing_metadata_rows": len(meta),
            "cfu_csv_rows_including_blank": len(cfu),
            "blank_formatting_rows_excluded": local_blank,
            "nonblank_cfu_timepoint_rows": len(cfu) - local_blank,
            "first_plate_missing_rows": first_missing,
            "second_plate_missing_rows": second_missing,
            **summarize_pairs(local_pairs),
        })
        for day, values in sorted(by_day.items()):
            batch_day_summaries.append({"batch_directory": directory, "day": day,
                "cfu_timepoint_rows": values["rows"], "second_plate_missing_rows": values["second_missing"],
                **summarize_pairs(values["pairs"]),
            })
    for key in cultures:
        if sorted(by_culture_cfu[key]) != [0, 1, 2, 3]:
            raise ValueError(f"Incomplete or duplicate CFU days: {key}")
        expected_days = [-1, 0, 1, 2, 3, 4] if key == ("R", 1) else [0, 1, 2, 3, 4]
        if sorted(by_culture_meta[key]) != expected_days:
            raise ValueError(f"Unexpected or duplicate sequencing-metadata days: {key}")
    replicate_distribution = Counter(Counter(key[0] for key in cultures).values())
    line_aggregates = []
    for line in sorted(by_line):
        values = by_line[line]
        line_aggregates.append({
            "line_label": line,
            "clone_names": sum(row["Line"] == line for row in strains.values()),
            "culture_timecourses": sum(row["Line"] == line for row in cultures.values()),
            "cfu_timepoint_rows": values["cfu_rows"],
            "second_plate_missing_rows": values["second_plate_missing_rows"],
            **summarize_pairs(values["pairs"]),
        })
    result = {
        "source_commit": manifest["source_commit"],
        "scope": "Small release metadata and raw CFU summary audit; no trajectories, posterior samples, raw reads, or inference pipeline analyzed.",
        "clone_names": len(strains),
        "evolved_clone_names": sum(row["Line"] != "all" for row in strains.values()),
        "ancestor_clone_names": sum(row["Line"] == "all" for row in strains.values()),
        "evolutionary_population_labels_excluding_ancestor": sorted({row["Line"] for row in strains.values()} - {"all"}),
        "evolutionary_population_count": len({row["Line"] for row in strains.values()} - {"all"}),
        "culture_timecourses": len(cultures),
        "clone_replicate_distribution": {str(replicates): clones for replicates, clones in sorted(replicate_distribution.items())},
        "sequencing_metadata_rows": sum(map(len, by_culture_meta.values())),
        "sequencing_metadata_rows_days_0_through_4": sum(day >= 0 for days in by_culture_meta.values() for day in days),
        "preassay_sequencing_metadata_rows": sum(day < 0 for days in by_culture_meta.values() for day in days),
        "cfu_timepoint_rows": sum(map(len, by_culture_cfu.values())),
        "blank_formatting_rows_excluded": blank_rows,
        "observed_zero_plate_counts": zero_counts,
        "measured_plate_counts": sum(row["nonblank_cfu_timepoint_rows"] * 2 - row["first_plate_missing_rows"] - row["second_plate_missing_rows"] for row in batch_summaries),
        "first_plate_missing_rows": sum(row["first_plate_missing_rows"] for row in batch_summaries),
        "second_plate_missing_rows": sum(row["second_plate_missing_rows"] for row in batch_summaries),
        "paired_CFU_diagnostic": {
            "measurement_name": "Model-conditional technical census residual index",
            "definition": "Q=(CFU1-CFU2)^2/(CFU1+CFU2), only rows with both counts and positive total",
            "units_and_nominal_exposure": "Raw integer colony counts. Preprint BarSeq experiments P40 describes identical nominal dilution/plating procedure, including 100 microliters plated, repeated for technical replicates. Bayesian inference P67-P68 and pinned inference code use a common Nb*D mean for both raw counts. Actual realized equal exposures are not independently verified from per-plate lab records.",
            "reference": "Under independent equal-mean Poisson plates, E[Q|CFU1+CFU2=n]=1 for n>0, because CFU1|n is Binomial(n,1/2).",
            "interpretation": "Descriptive discrepancy from the ideal equal-exposure Poisson reference; it can reflect handling, dilution/plating noise, contamination or unequal realized exposures. Not a fitted CFU overdispersion parameter, drift estimate, establishment effect, posterior validation, or independence claim across cultures/days. No inferential p-values or confidence intervals computed.",
            **summarize_pairs(pairs_all),
        },
        "structural_checks_passed": [
            "All selected input SHA256 digests match manifest",
            "Master culture ledger exactly matches each batch experiment list",
            "Clone attributes agree across replicates",
            "No duplicated sequencing index within batch",
            "Each culture has distinct CFU days 0,1,2,3",
            "Each culture has sequencing metadata days 0,1,2,3,4, plus one documented R/1 day -1",
            "No negative CFU counts or nonpositive dilution factors",
        ],
        "matched_WAM_ledgers_admitted": 0,
        "eligibility": {
            "independent_clone_or_barcode_WAM_trials": False,
            "route_specific_mutation_supply": False,
            "known_single_cell_route_recovery_denominators": False,
            "observed_successful_mutant_establishment": False,
            "matched_Wsp_Aws_Mws_selected_outcomes": False,
        },
    }
    DERIVED.mkdir(exist_ok=True)
    (DERIVED / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    write_csv("batch_measurement_audit.csv", batch_summaries)
    write_csv("batch_day_measurement_audit.csv", batch_day_summaries)
    write_csv("population_measurement_audit.csv", line_aggregates)
    print(json.dumps({"clone_names": result["clone_names"], "cultures": result["culture_timecourses"], "paired_CFU": len(pairs_all), "mean_Q": result["paired_CFU_diagnostic"]["mean_pair_Q"], "checks": len(result["structural_checks_passed"])}))


if __name__ == "__main__":
    main()
