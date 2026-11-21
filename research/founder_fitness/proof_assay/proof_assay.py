"""Reconstruct the separate 10-repeat assay and compare it to founder predictions."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from fractions import Fraction
from math import exp, fsum, isclose, log, prod
from pathlib import Path

import rdata

from verify_native_fitness import native_table, paired_rates, projected_leader, sign


def check(path, digest):
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError(f"Unexpected input file: {path.name}")


def proof_assay(poc_path, raw_path, meta_path):
    check(poc_path, "90b43ee601d269ccc8d03344ae92d6692c74723af609b55353508029333574da")
    check(raw_path, "c6186f5710f24a8d2081f70dda299bf97a10cef6849ebc84f9d6f7850e59c3c3")
    check(meta_path, "7678ddbd1bb47f89510844de6efc6a793db4e31678c4afcac5a84306e691e335")
    poc = rdata.read_rda(poc_path)["poc92"]
    raw = rdata.read_rda(raw_path)["counts.expected"].to_pandas()
    with meta_path.open(newline="") as stream:
        metadata = [row for row in csv.DictReader(stream) if row["bcpwell"] == "92"]
    stages = {stage: [row["exp"] for row in metadata if row["atp"] == code]
              for stage, code in (("i", "0"), ("f", "2"))}
    assert len(stages["i"]) == len(stages["f"]) == 10
    indexed = {}
    for row in poc.itertuples():
        replicate = int(row.exp)
        key = (row.bcid, replicate)
        assert key not in indexed
        for stage, samples in stages.items():
            for label, field in ((row.bcid, "bccts"), (row.refid, "refcts")):
                assert raw.at[label, samples[replicate-1]] + 1 == getattr(row, f"{field}_{stage}")
        focal = Fraction(int(row.bccts_f), int(row.bccts_i))
        reference = Fraction(int(row.refcts_f), int(row.refcts_i))
        relative = focal/reference
        assert isclose(float(relative)**0.05, row.rw, abs_tol=1e-12)
        indexed[key] = relative
    assert len(indexed) == 910
    return indexed, poc.set_index(["bcid", "exp"], verify_integrity=True)


def compare(args):
    native = native_table(args.myfa, "myfa")
    native = native.drop_duplicates(["treatment", "bc1", "bc2"]).set_index(["treatment", "bc1", "bc2"])
    evo = native_table(args.myevo, "myevo")
    poc, poc_rows = proof_assay(args.poc, args.raw, args.metadata)
    group = "CMdiploid0.001"
    profiles = []
    pairs = []
    labels = set()
    summaries = []
    pair_counts = {}
    for ix, (_, row) in enumerate(evo.iterrows(), 1):
        if row["treatment"] != group:
            continue
        source_names = [row["bc1"], row["bc2"]]
        assay_names = [x.removesuffix("B") if row["set"] == "S14" else x for x in source_names]
        if assay_names[1] < assay_names[0]:
            source_names.reverse()
            assay_names.reverse()
        key = tuple(assay_names)
        pairs.append(key)
        labels.update(assay_names)
        rates = [poc[(assay_names[0], r)] / poc[(assay_names[1], r)] for r in range(1, 11)]
        a, b = (native.loc[(group, x, y)] for x, y in (source_names, source_names[::-1]))
        full = prod(rates)
        main_rate = prod(paired_rates(a, b))
        order = [1, 2] if source_names[0] == row["bc1"] else [2, 1]
        start_counts = [int(row[f"bc{i}cts_0"]) - 1 for i in order]
        end_counts = [int(row[f"bc{i}cts_25"]) - 1 for i in order]
        summaries.append((f"W{ix:03}", key, *start_counts, *end_counts, main_rate.numerator, main_rate.denominator))
        if key not in pair_counts:
            pair_counts[key] = []
            for rep in range(1, 11):
                u, v = (poc_rows.loc[(name, str(rep))] for name in key)
                assert u.refcts_i == v.refcts_i and u.refcts_f == v.refcts_f
                pair_counts[key].append((rep, int(u.bccts_i), int(u.bccts_f), int(v.bccts_i), int(v.bccts_f),
                                         int(u.refcts_i), int(u.refcts_f)))
        odds = Fraction(*start_counts)
        start = odds/(1 + odds)
        finish = Fraction(end_counts[0], sum(end_counts))
        base = sign(odds - 1)
        winner = sign(2*finish - 1)
        gain = sign(finish - start)
        result = dict(baseline=(base == winner), base_error=float(abs(start - finish)))
        leaders = []
        for label, ratio, duration in (("proof", full, 200), ("main", main_rate, 80)):
            fit = sign(ratio - 1)
            combined = projected_leader(odds, ratio, 250, duration)
            pred = 1/(1 + exp(-log(float(odds)) - 250*log(float(ratio))/duration))
            assert 0 not in (fit, combined, winner, base, gain)
            result[label] = dict(assay=fit == winner, combined=combined == winner,
                                 gain=fit == gain, error=abs(float(finish) - pred))
            leaders.append(fit)
        result["assay_agreement"] = leaders[0] == leaders[1]
        profiles.append(result)
    assert len(profiles) == 21
    n = len(profiles)
    result = {
        "wells": n, "distinct_focal_labels": len(labels), "distinct_pairs": len(set(pairs)),
        "pair_multiplicity": dict(sorted(Counter(Counter(pairs).values()).items())),
        "poc_native_counts_checked_in_raw_matrix": len(poc)*4,
        "baseline_hits": sum(r["baseline"] for r in profiles),
        "baseline_mae": fsum(r["base_error"] for r in profiles)/n,
        "assays_agree_on_higher_fitness": sum(r["assay_agreement"] for r in profiles),
        "unresolved_or_tied": 0,
    }
    for k in ("proof", "main"):
        result[k] = {p: sum(r[k][p] for r in profiles) for p in ("assay", "combined", "gain")}
        result[k]["combined_mae"] = fsum(r[k]["error"] for r in profiles)/n
        result[k]["combined_only_vs_baseline"] = sum(r[k]["combined"] and not r["baseline"] for r in profiles)
        result[k]["baseline_only_vs_combined"] = sum(r["baseline"] and not r[k]["combined"] for r in profiles)
    if args.export is not None:
        args.export.mkdir(exist_ok=True, parents=True)
        pair_ids = {key: f"Q{i:03}" for i, key in enumerate(sorted(pair_counts), 1)}
        def write(name, columns, rows):
            with (args.export / name).open("w", newline="", encoding="utf-8") as stream:
                writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
                writer.writerow(columns)
                writer.writerows(rows)
        write("proof_pairs.tsv", ["pair_id", "replicate", "initial_A", "final_A", "initial_B",
                                  "final_B", "initial_ref", "final_ref"],
              ((pair_ids[key], *record) for key in sorted(pair_counts) for record in pair_counts[key]))
        write("proof_wells.tsv", ["population_id", "pair_id", "day0_A", "day0_B", "day25_A", "day25_B",
                                  "four_repeat_ratio_numerator", "four_repeat_ratio_denominator"],
              ((well, pair_ids[key], *values) for well, key, *values in summaries))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("poc", "raw", "metadata", "myfa", "myevo"):
        parser.add_argument(name, type=Path)
    parser.add_argument("--export", type=Path, help="Directory for anonymous portable benchmark inputs")
    print(json.dumps(compare(parser.parse_args()), indent=2))
