"""Synthetic calibration and power experiment, not biological measurements. MIT."""
import argparse
import csv
import json
import math
import random
from pathlib import Path
from tmd_time_diagnostic import analyze


def simulate(kind, n, seed):
    rng, rows = random.Random(seed), []
    for i in range(n):
        context = "fast" if i < n // 2 else "slow"
        rate = 1.5 if context == "fast" else .3
        pa = .85 if context == "fast" else .15
        if kind == "switching":
            rate, pa = 1, .90
            t = rng.expovariate(rate)
            if t > 1:
                t, pa = 1 + rng.expovariate(rate), .10
        elif kind == "gamma_null":
            frailty = rng.gammavariate(2, .5)
            t = rng.expovariate(rate * frailty)
        else:
            t = rng.expovariate(rate)
        route = "A" if rng.random() < pa else "B"
        censor = rng.uniform(2, 5)
        event = int(t <= censor)
        rows.append(dict(replicate_id=str(i), context=context, time=str(min(t, censor)),
                         event=str(event), route=route if event else "", provenance="synthetic"))
    return rows


def wilson(k, n):
    z, p = 1.959963984540054, k / n
    den = 1 + z * z / n
    center = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [center - half, center + half]


def run(repetitions=200, permutations=399, n=240):
    result = dict(evidence_kind="synthetic_only", repetitions=repetitions,
                  permutations_per_test=permutations, replicates_per_dataset=n,
                  cuts=[1, 2], alpha=.05, fixed_design=True, scenarios={})
    for index, kind in enumerate(["exponential_null", "gamma_null", "switching"]):
        rejected, pooled = 0, 0
        for k in range(repetitions):
            rows = simulate(kind, n, 20260930 + 100000 * index + k)
            r = analyze(rows, ["A", "B"], [1, 2], permutations, 991 + k)
            rejected += r["conditional_permutation_p"] is not None and r["conditional_permutation_p"] <= .05
            if kind == "exponential_null":
                all_rows = [dict(row, context="pooled") for row in rows]
                p = analyze(all_rows, ["A", "B"], [1, 2], permutations, 991 + k)["conditional_permutation_p"]
                pooled += p is not None and p <= .05
        result["scenarios"][kind] = dict(rejections=rejected, proportion=rejected / repetitions,
                                         wilson_95_interval=wilson(rejected, repetitions))
        if kind == "exponential_null":
            result["scenarios"][kind]["unstratified_rejections"] = pooled
            result["scenarios"][kind]["unstratified_proportion"] = pooled / repetitions
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--outdir", default="results")
    p.add_argument("--repetitions", type=int, default=200)
    p.add_argument("--permutations", type=int, default=399)
    p.add_argument("--n", type=int, default=240)
    args = p.parse_args()
    if args.repetitions < 1 or args.permutations < 1 or args.n < 4:
        p.error("repetitions/permutations must be positive; n >= 4")
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    r = run(args.repetitions, args.permutations, args.n)
    (out / "synthetic_calibration.json").write_text(json.dumps(r, indent=2) + "\n")
    example = simulate("switching", args.n, 20260930)
    with (out / "synthetic_switching_example.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(example[0]))
        writer.writeheader()
        writer.writerows(example)
    print(json.dumps(r, indent=2))
