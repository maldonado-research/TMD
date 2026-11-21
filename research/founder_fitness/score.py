"""Score the frozen founder-assay forecasts from anonymous read counts."""
import csv
import json
import math
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from statistics import fmean

HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parent / "lineage_forecasts" / "fasanello"
GENERATIONS = {1: 250, 2: 250, 3: 250, 4: 250, 5: 200, 6: 300}
DAYS = (0, 10, 15, 20, 22, 24, 25)
RULES = ("baseline", "assay", "combined")


def table(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def sign(x):
    return (x > 0) - (x < 0)


def decision(odds):
    return sign(odds.numerator - odds.denominator)


def share(a, b):
    return Fraction(a, a+b)


def assay_ratio(row):
    # Both focal labels shared one reference in each pooled measurement.
    return Fraction(int(row["final_A"]) * int(row["initial_B"]),
                    int(row["initial_A"]) * int(row["final_B"]))


def project(start, ratios, generations):
    # The generations may be fractional for intermediate source visits.
    horizon = Fraction(generations, 20*len(ratios))
    product = math.prod(ratios)
    reduced_odds = start**horizon.denominator * product**horizon.numerator
    contrast = math.log(start) + float(horizon) * math.log(product)
    if contrast >= 0:
        prediction = 1/(1+math.exp(-contrast))
    else:
        exp_value = math.exp(contrast)
        prediction = exp_value/(1+exp_value)
    return decision(reduced_odds), prediction


def hit(pred, outcome):
    return int(pred != 0 and pred == outcome)


def combine_counts(rows):
    result = defaultdict(dict)
    for row in rows:
        well, day = row["population_id"], int(row["day"])
        assert day not in result[well]
        result[well][day] = tuple(int(row[col]) for col in ("reads_A", "reads_B"))
    return result


def score_well(rows, counts):
    r = sorted(rows, key=lambda v: int(v["replicate"]))
    assert [int(v["replicate"]) for v in r] == [1, 2, 3, 4]
    assert len({(v["assay_pool_id"], v["condition_id"]) for v in r}) == 1
    condition = int(r[0]["condition_id"])
    horizon = GENERATIONS[condition]
    ratios = [assay_ratio(row) for row in r]
    assert len(set(counts)) == len(DAYS) and set(counts) == set(DAYS)
    a0, b0 = counts[0]
    a, b = counts[25]
    assert min(a0, b0) > 0 and all(min(pair) >= 0 and sum(pair) > 0 for pair in counts.values())
    start = Fraction(a0, b0)
    baseline = decision(start)
    actual_share, baseline_share = share(a, b), share(a0, b0)
    endpoint, gain = sign(a-b), sign(actual_share-baseline_share)
    assay = decision(math.prod(ratios))
    combined, predicted_share = project(start, ratios, horizon)
    predictions = dict(baseline=baseline, assay=assay, combined=combined)
    rep_assay = [decision(v) for v in ratios]
    rep_combined = [project(start, [v], horizon)[0] for v in ratios]
    author_A, author_B = (float(r[0][k]) for k in ("fit0_A", "fit0_B"))
    weighted_log_ratio = math.log(start) + horizon*math.log(author_A/author_B)
    out = {"condition": condition, "pool": r[0]["assay_pool_id"], "endpoint": endpoint, "gain": gain,
           "predictions": predictions, "hits": {k: hit(v, endpoint) for k, v in predictions.items()},
           "gain_hit": hit(assay, gain), "rep_assay": rep_assay, "rep_combined": rep_combined,
           "weighted_assay": sign(author_A-author_B), "weighted_combined": sign(weighted_log_ratio),
           "absolute_share_errors": {"baseline": abs(float(baseline_share-actual_share)),
                                     "combined": abs(predicted_share-float(actual_share))}}
    visits = {}
    for day in DAYS[1:]:
        a, b = counts[day]
        pred, p = project(start, ratios, Fraction(horizon*day, 25))
        target = sign(a-b)
        visits[day] = {"combined_hit": hit(pred, target), "baseline_hit": hit(baseline, target),
                       "assay_gain_hit": hit(assay, sign(share(a,b)-baseline_share)),
                       "combined_absolute_error": abs(p-float(share(a,b)))}
    out["visits"] = visits
    return out


def summary(rows):
    correct = {k: sum(r["hits"][k] for r in rows) for k in RULES}
    paired = Counter((r["hits"]["baseline"], r["hits"]["combined"]) for r in rows)
    return {"n": len(rows), "hits": correct, "assay_gain_hits": sum(r["gain_hit"] for r in rows),
            "gain_ties": sum(r["gain"] == 0 for r in rows), "outcome_ties": sum(r["endpoint"] == 0 for r in rows),
            "forecast_ties": {k: sum(r["predictions"][k] == 0 for r in rows) for k in RULES},
            "paired_baseline_vs_combined": {"both": paired[1,1], "baseline_only": paired[1,0],
                                            "combined_only": paired[0,1], "neither": paired[0,0]},
            "mean_absolute_share_errors": {k: round(fmean(r["absolute_share_errors"][k] for r in rows), 8)
                                          for k in ("baseline", "combined")}}


def replicate_checks(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row["pool"]].append(row)
    result = {}
    for field in ("rep_assay", "rep_combined"):
        key = "assay" if field == "rep_assay" else "combined"
        per_pool = {g: [sum(hit(r[field][i], r["endpoint"]) for r in group) for i in range(4)]
                    for g, group in sorted(groups.items())}
        possible = {0}
        for vec in per_pool.values():
            possible = {x+y for x in possible for y in vec}
        consensus = [r for r in rows if len(set(r[field])) == 1 and r[field][0] != 0]
        result[key] = {"hits_using_each_repeat": [sum(x[i] for x in per_pool.values()) for i in range(4)],
                       "n_unanimous_repeats": len(consensus),
                       "hits_in_unanimous": sum(hit(r[field][0], r["endpoint"]) for r in consensus),
                       "baseline_hits_in_unanimous": sum(r["hits"]["baseline"] for r in consensus),
                       "possible_hits_one_repeat_per_pool": sorted(possible), "per_pool_hits": per_pool}
    return result


def analyze():
    grouped = defaultdict(list)
    for row in table(HERE/"founder_assays.tsv"):
        grouped[row["population_id"]].append(row)
    counts = combine_counts(table(PREVIOUS/"fasanello_counts.tsv"))
    assert grouped.keys() == counts.keys() and len(counts) == 76
    wells = {well: score_well(grouped[well], counts[well]) for well in sorted(grouped)}
    rows = list(wells.values())
    treatments = {str(c): summary([r for r in rows if r["condition"] == c]) for c in GENERATIONS}
    timing = {}
    for day in DAYS[1:]:
        by_day = [r["visits"][day] for r in rows]
        timing[day] = {k: sum(r[k] for r in by_day) for k in ("baseline_hit", "combined_hit", "assay_gain_hit")}
    compact = {well: {k:v for k,v in r.items() if k not in ("absolute_share_errors", "visits")} for well, r in wells.items()}
    return {"all": summary(rows), "by_condition": treatments, "repeat_checks": replicate_checks(rows),
            "weighted_author_assay_hits": sum(hit(r["weighted_assay"], r["endpoint"]) for r in rows),
            "weighted_author_combined_hits": sum(hit(r["weighted_combined"], r["endpoint"]) for r in rows),
            "by_visit": timing, "per_population": compact}


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2))
