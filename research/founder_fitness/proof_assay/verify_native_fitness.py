"""Independent aggregate replay from the two pinned native R tables (requires rdata)."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import json
from math import exp, fsum, gcd, isclose, log, prod
from pathlib import Path

import rdata


DIGEST = {
    "myfa": "f20f592d570614b0add41d1181900570e75338f73bffdae95100e98001e03f3d",
    "myevo": "f10be28895efc07a2106f8de08e38661ccc75139826e919ffe54b170aa41d9e0",
}
CONDITIONS = (
    "CMdiploid0.001", "CMhaploid0.001", "CM+Ethanoldiploid0.001",
    "CM+Saltdiploid0.001", "CMdiploid0.004", "CMdiploid0.00025",
)


def native_table(path, name):
    if hashlib.sha256(path.read_bytes()).hexdigest() != DIGEST[name]:
        raise ValueError(f"Unexpected archived contents for {name}")
    return rdata.read_rda(path)[name]


def sign(value):
    return int(value > 0) - int(value < 0)


def projected_leader(odds, assay_ratio, horizon, duration):
    common = gcd(horizon, duration)
    return sign(odds ** (duration // common) * assay_ratio ** (horizon // common) - 1)


def paired_rates(a, b):
    ratios = []
    for rep in range(1, 5):
        def read(row, field, stage):
            value = row[f"{field}_{stage}_0r{rep}"]
            assert float(value).is_integer() and value > 0
            return int(value)

        for stage in ("i", "f"):
            assert read(a, "refcts", stage) == read(b, "refcts", stage)
            assert read(a, "bc1cts", stage) == read(b, "bc2cts", stage)
            assert read(a, "bc2cts", stage) == read(b, "bc1cts", stage)
        ratio = []
        for row in (a, b):
            focal_change = Fraction(read(row, "bc1cts", "f"), read(row, "bc1cts", "i"))
            ref_change = Fraction(read(row, "refcts", "f"), read(row, "refcts", "i"))
            rate = focal_change / ref_change
            assert isclose(float(rate)**0.05, row[f"fit0r{rep}"], abs_tol=1e-12)
            ratio.append(rate)
        ratios.append(ratio[0] / ratio[1])
    return ratios


def evaluate(assay, evo):
    keys = ["treatment", "bc1", "bc2"]
    inputs = [f"{k}_{t}_0r{r}" for k in ("refcts", "bc1cts", "bc2cts")
              for t in ("i", "f") for r in range(1, 5)]
    calibration = [f"fit0r{r}" for r in range(1, 5)] + ["fit0"]
    # Each block of generation-zero measurements appears on four evolved-assay rows.
    selected = assay[keys + ["set", "well"] + inputs + calibration].drop_duplicates()
    assert len(assay) == 608 and len(selected) == 152 and len(evo) == 76
    selected = selected.set_index(keys, verify_integrity=True)
    assert not evo.duplicated(["treatment", "well"]).any()
    scores = []
    for _, row in evo.iterrows():
        regime = CONDITIONS.index(row["treatment"]) + 1
        horizon = {5: 200, 6: 300}.get(regime, 250)
        # Only the two sets with deliberately repeated labels have a trailing B.
        def name(index):
            label = row[f"bc{index}"]
            return label.removesuffix("B") if row["set"] in ("S14", "S2") else label

        order = sorted((1, 2), key=name)
        pair = [row[f"bc{i}"] for i in order]
        a, b = (selected.loc[(row["treatment"], x, y)] for x, y in (pair, pair[::-1]))
        assert a["set"] == b["set"] and a["well"] == b["well"] == row["well"]

        def share(day):
            x, y = (int(row[f"bc{index}cts_{day}"]) - 1 for index in order)
            assert min(x, y) >= 0 and x + y > 0
            return Fraction(x, x + y)

        rates = paired_rates(a, b)
        combined_rate = prod(rates)
        start, finish = share(0), share(25)
        odds = start / (1 - start)
        baseline = sign(odds - 1)
        fit = sign(combined_rate - 1)
        forecast = projected_leader(odds, combined_rate, horizon, 80)
        predicted_share = 1 / (1 + exp(-log(float(odds)) - horizon*log(float(combined_rate))/80))
        winner = sign(2*finish - 1)
        gain = sign(finish - start)
        native = sign(float(a["fit0"]) - float(b["fit0"]))
        rep_fits = [sign(r - 1) for r in rates]
        rep_forecasts = [projected_leader(odds, r, horizon, 20) for r in rates]
        assert 0 not in [baseline, fit, forecast, winner, gain, native, *rep_fits, *rep_forecasts]
        scores.append(dict(condition=regime, baseline=baseline == winner, assay=fit == winner,
                           combined=forecast == winner, gain=fit == gain, native=native == winner,
                           native_disagrees=native != fit, baseline_error=float(abs(start - finish)),
                           combined_error=abs(predicted_share - float(finish)),
                           rep_assay=[x == winner for x in rep_fits],
                           rep_combined=[x == winner for x in rep_forecasts],
                           rep_gain=[x == gain for x in rep_fits],
                           votes=max(Counter(rep_fits).values())))
    return scores


def summarize(rows):
    n = len(rows)
    return {
        "n": n,
        "hits": {k: sum(r[k] for r in rows) for k in ("baseline", "assay", "combined", "gain", "native")},
        "paired_combined_only": sum(r["combined"] and not r["baseline"] for r in rows),
        "paired_baseline_only": sum(r["baseline"] and not r["combined"] for r in rows),
        "baseline_mae": fsum(r["baseline_error"] for r in rows)/n,
        "combined_mae": fsum(r["combined_error"] for r in rows)/n,
    }


def run(assay_path, evo_path):
    rows = evaluate(native_table(assay_path, "myfa"), native_table(evo_path, "myevo"))
    by_condition = defaultdict(list)
    for row in rows:
        by_condition[row["condition"]].append(row)
    return {
        "all": summarize(rows),
        "by_source_condition": {k: summarize(v) for k, v in sorted(by_condition.items())},
        "ties_or_unresolved_primary": 0,
        "native_disagrees_with_mean_log_rate": sum(r["native_disagrees"] for r in rows),
        "modal_sign_votes_across_four_repeats": dict(sorted(Counter(r["votes"] for r in rows).items())),
        "unanimous_repeats": summarize([r for r in rows if r["votes"] == 4]),
        "single_repeat_hits": {k: [sum(r[k][i] for r in rows) for i in range(4)]
                               for k in ("rep_assay", "rep_combined", "rep_gain")},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("myfa", type=Path, help="Pinned myfa.Rdata")
    parser.add_argument("myevo", type=Path, help="Pinned myevo.Rdata")
    args = parser.parse_args()
    print(json.dumps(run(args.myfa, args.myevo), indent=2))
