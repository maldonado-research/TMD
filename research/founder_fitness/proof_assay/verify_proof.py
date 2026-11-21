"""Replay the separate founding assay from anonymous tables with the Python standard library."""
import argparse
import csv
from collections import Counter, defaultdict
from fractions import Fraction
import json
from math import exp, fsum, log, prod
from pathlib import Path


def table(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def sign(value):
    return int(value > 0) - int(value < 0)


def read_rates(path):
    rates = defaultdict(dict)
    references = defaultdict(set)
    for row in table(path):
        group = rates[row["pair_id"]]
        rep = int(row["replicate"])
        if rep in group:
            raise ValueError("Duplicate pair and repeat")
        ai, af, bi, bf, ri, rf = (int(row[name]) for name in
                                   ("initial_A", "final_A", "initial_B", "final_B", "initial_ref", "final_ref"))
        assert min(ai, af, bi, bf, ri, rf) > 0
        a = Fraction(af*ri, ai*rf)
        b = Fraction(bf*ri, bi*rf)
        group[rep] = a/b
        references[rep].add((ri, rf))
    assert len(rates) == 16 and all(set(v) == set(range(1, 11)) for v in rates.values())
    assert all(len(v) == 1 for v in references.values())
    return {k: [r[i] for i in range(1, 11)] for k, r in rates.items()}


def run(wells_path, pairs_path):
    rates = read_rates(pairs_path)
    wells = table(wells_path)
    records = []
    for row in wells:
        values = rates[row["pair_id"]]
        proof = prod(values)
        main = Fraction(int(row["four_repeat_ratio_numerator"]), int(row["four_repeat_ratio_denominator"]))
        ai, bi, af, bf = (int(row[name]) for name in ("day0_A", "day0_B", "day25_A", "day25_B"))
        odds = Fraction(ai, bi)
        start, finish = Fraction(ai, ai+bi), Fraction(af, af+bf)
        win = sign(af - bf)
        gain = sign(finish - start)
        baseline = sign(ai - bi)
        record = dict(pair_id=row["pair_id"], baseline=baseline == win, err_base=float(abs(start-finish)))
        record["assays_agree"] = sign(main-1) == sign(proof-1)
        for key, growth, days in (("proof", proof, 200), ("main", main, 80)):
            exponent = Fraction(250, days)
            combined = sign(odds ** exponent.denominator * growth ** exponent.numerator - 1)
            fit = sign(growth - 1)
            assert 0 not in (win, gain, baseline, fit, combined)
            share = 1/(1+exp(-log(float(odds)) - float(exponent)*log(float(growth))))
            record[key] = dict(assay=fit == win, combined=combined == win, gain=fit == gain,
                               error=abs(float(finish)-share))
        record["replicate_hits"] = [sign(r-1) == win for r in values]
        record["leave_one_repeat_hits"] = [sign(proof/r-1) == win for r in values]
        records.append(record)
    assert len(records) == len({r["population_id"] for r in wells}) == 21
    assert set(r["pair_id"] for r in records) == set(rates)
    n = len(records)
    result = {
        "wells": n, "distinct_focal_labels": 32, "distinct_pairs": len(rates),
        "pair_multiplicity": dict(sorted(Counter(Counter(r["pair_id"] for r in records).values()).items())),
        "baseline_hits": sum(r["baseline"] for r in records),
        "baseline_mae": fsum(r["err_base"] for r in records)/n,
        "assays_agree_on_higher_fitness": sum(r["assays_agree"] for r in records),
        "unresolved_or_tied": 0,
    }
    for key in ("proof", "main"):
        result[key] = {p: sum(r[key][p] for r in records) for p in ("assay", "combined", "gain")}
        result[key]["combined_mae"] = fsum(r[key]["error"] for r in records)/n
        result[key]["combined_only_vs_baseline"] = sum(r[key]["combined"] and not r["baseline"] for r in records)
        result[key]["baseline_only_vs_combined"] = sum(r["baseline"] and not r[key]["combined"] for r in records)
    by_pair = defaultdict(list)
    for r in records:
        by_pair[r["pair_id"]].append(r)
    pair_rates = [Fraction(sum(r["proof"]["assay"] for r in group), len(group)) for group in by_pair.values()]
    result["exploratory"] = {
        "stock_endpoint_and_gain_correct": sum(r["proof"]["assay"] and r["proof"]["gain"] for r in records),
        "stock_endpoint_correct_but_lost_share": sum(r["proof"]["assay"] and not r["proof"]["gain"] for r in records),
        "equal_pair_weighted_assay_accuracy": str(sum(pair_rates)/len(pair_rates)),
        "assay_hits_by_single_proof_repeat": [sum(r["replicate_hits"][i] for r in records) for i in range(10)],
        "assay_hits_omitting_each_proof_repeat": [sum(r["leave_one_repeat_hits"][i] for r in records) for i in range(10)],
        "proof_absolute_share_error_smaller_than_baseline": sum(r["proof"]["error"] < r["err_base"] for r in records),
    }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=Path(__file__).resolve().parent)
    directory = parser.parse_args().directory
    print(json.dumps(run(directory/"proof_wells.tsv", directory/"proof_pairs.tsv"), indent=2))
