"""Rescore fixed ten-repeat founder forecasts under every whole-pool endpoint-library choice."""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import product
import json
from math import exp, fsum, log, prod
from pathlib import Path

from verify_proof import read_rates, sign, table

HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parents[1] / "lineage_forecasts" / "fasanello"
LIBRARIES = ("original", "rerun")
DIGESTS = {
    "technical_counts.tsv": "619c7d99a261304a5117fa24530573a2dabc2f7deca0aea812a1c2ce00a522bb",
    "endpoint_pools.tsv": "e41d56ca0389257d7da00acfe5bb68f4da79b27902e7eb1e43bcfa0af7cc692a",
    "proof_pairs.tsv": "f6045214bfbc50bb01eaee64331ea90f6590c10d0d057be45e2dbeb1dac27fa0",
    "proof_wells.tsv": "0167f55bca65ebfcdf57ecfec45586fcd306230609af98b63c7ce0073e73dd55",
}


def checked_path(directory, name):
    path = directory / name
    if hashlib.sha256(path.read_bytes()).hexdigest() != DIGESTS[name]:
        raise ValueError(f"Input does not match the archived file {name}")
    return path


def counts(row, library):
    a, b = (int(row[f"{library}_{side}"]) for side in ("A", "B"))
    if min(a, b) < 0 or a + b == 0:
        raise ValueError("Incomplete measurement in a selected endpoint pool")
    return a, b


def compile_forecasts(proof_dir, earlier_dir):
    rates = read_rates(checked_path(proof_dir, "proof_pairs.tsv"))
    wells = table(checked_path(proof_dir, "proof_wells.tsv"))
    membership = {r["population_id"]: r["pool_id"]
                  for r in table(checked_path(earlier_dir, "endpoint_pools.tsv"))}
    technical = {(r["population_id"], int(r["day"])): r
                 for r in table(checked_path(earlier_dir, "technical_counts.tsv"))}
    frozen = []
    for row in wells:
        well = row["population_id"]
        initial, endpoint = technical[well, 0], technical[well, 25]
        a, b = counts(initial, initial["selected"])
        assert (a, b) == (int(row["day0_A"]), int(row["day0_B"]))
        assert counts(endpoint, endpoint["selected"]) == (int(row["day25_A"]), int(row["day25_B"]))
        # All repeat measurements needed for the original common-denominator restriction exist.
        for day in (0, 10, 25):
            for library in LIBRARIES:
                counts(technical[well, day], library)
        odds = Fraction(a, b)
        ratio = prod(rates[row["pair_id"]])
        # The exponent on the ten-repeat product is 250 /(10 * 20) = 5/4.
        combined = sign(odds**4 * ratio**5 - 1)
        share = 1/(1 + exp(-log(float(odds)) - 1.25*log(float(ratio))))
        choices = {lib: Fraction(x, x+y) for lib in LIBRARIES for x, y in [counts(endpoint, lib)]}
        frozen.append(dict(pool=membership[well], source=endpoint["selected"], endpoint=choices,
                           start=Fraction(a, a+b), baseline=sign(a-b), assay=sign(ratio-1),
                           combined=combined, projected_share=share))
    assert len(frozen) == len({row["population_id"] for row in wells}) == 21
    assert len({row["pool"] for row in frozen}) == 2
    return frozen


def evaluate(wells, assignment):
    rows = []
    for row in wells:
        observed = row["endpoint"][assignment[row["pool"]]]
        winner = sign(2*observed - 1)
        gain = sign(observed - row["start"])
        selected = row["endpoint"][row["source"]]
        assert 0 not in (winner, gain, row["baseline"], row["assay"], row["combined"])
        rows.append(dict(baseline=row["baseline"] == winner, assay=row["assay"] == winner,
                         combined=row["combined"] == winner, gain=row["assay"] == gain,
                         changed=winner != sign(2*selected - 1),
                         base_error=float(abs(observed-row["start"])),
                         combined_error=abs(float(observed)-row["projected_share"])))
    totals = {key: sum(r[key] for r in rows) for key in ("baseline", "assay", "combined", "gain")}
    baseline_mae = fsum(r["base_error"] for r in rows) / len(rows)
    combined_mae = fsum(r["combined_error"] for r in rows) / len(rows)
    return {"libraries": assignment, "strict_hits": totals,
            "endpoint_leaders_changed_from_selected": sum(r["changed"] for r in rows),
            "assay_minus_baseline_hits": totals["assay"] - totals["baseline"],
            "combined_minus_baseline_hits": totals["combined"] - totals["baseline"],
            "baseline_share_mae": baseline_mae, "combined_share_mae": combined_mae,
            "combined_minus_baseline_share_mae": combined_mae - baseline_mae}


def run(proof_dir, earlier_dir):
    wells = compile_forecasts(proof_dir, earlier_dir)
    groups = sorted({r["pool"] for r in wells})
    chosen = {g: {r["source"] for r in wells if r["pool"] == g} for g in groups}
    assert all(len(choices) == 1 for choices in chosen.values())
    return {"wells": len(wells), "wells_per_endpoint_pool": dict(sorted(Counter(r["pool"] for r in wells).items())),
            "source_selected_libraries": {g: next(iter(v)) for g, v in chosen.items()},
            "all_assignments": [evaluate(wells, dict(zip(groups, libs)))
                                for libs in product(LIBRARIES, repeat=len(groups))]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proof-dir", type=Path, default=HERE)
    parser.add_argument("--earlier-dir", type=Path, default=PREVIOUS)
    args = parser.parse_args()
    print(json.dumps(run(args.proof_dir, args.earlier_dir), indent=2))
