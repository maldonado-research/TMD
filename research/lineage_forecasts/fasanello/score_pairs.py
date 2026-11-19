"""Compare the frozen abundance forecasts for the two tracked labels in each population."""
import csv
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DAYS = (0, 10, 15, 20, 22, 24, 25)
RULES = ("baseline", "early", "change")
GROUPS = ("condition_id", "pair_id", "label_pair_id", "strain_pair_id")


def leader(margin):
    if margin == 0:
        return None
    return "A" if margin > 0 else "B"


def load_panel(path):
    panel = {}
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            sample = row["population_id"]
            metadata = {name: row[name] for name in GROUPS}
            group = panel.setdefault(sample, {"meta": metadata, "counts": {}})
            if group["meta"] != metadata:
                raise ValueError(f"Inconsistent attributes for {sample}")
            day = int(row["day"])
            reads = (int(row["reads_A"]), int(row["reads_B"]))
            if min(reads) < 0 or day not in DAYS or day in group["counts"]:
                raise ValueError(f"Invalid counts or visit for {sample}")
            group["counts"][day] = reads
    return panel


def score(group):
    counts = group["counts"]
    if any(t not in counts or sum(counts[t]) == 0 for t in (0, 10, 25)):
        return None
    shares = {t: Fraction(a, a+b) for t, (a, b) in counts.items() if a+b}
    half = Fraction(1, 2)
    observed = {t: leader(p-half) for t, p in shares.items()}
    predicted = dict(baseline=observed[0], early=observed[10], change=leader(2*shares[10]-shares[0]-half))
    outcome = observed[25]
    hits = {k: pred is not None and pred == outcome for k, pred in predicted.items()}
    return {**group["meta"], "predictions": predicted, "endpoint": outcome, "hits": hits,
            "endpoint_transfers_to_erase_unique_lead": (abs(counts[25][0]-counts[25][1])+1)//2,
            "observed_leaders": observed}


def totals(rows):
    return {name: sum(row["hits"][name] for row in rows) for name in RULES}


def stratify(rows, key):
    groups = defaultdict(list)
    for row in rows:
        groups[row[key]].append(row)
    return groups


def dependence(rows, key):
    groups = stratify(rows, key)
    full_gain = sum(r["hits"]["change"]-r["hits"]["early"] for r in rows)
    group_hits = {g: totals(group) for g, group in groups.items()}
    omitted = [full_gain-hits["change"]+hits["early"] for hits in group_hits.values()]
    repeated = [group for group in groups.values() if len(group)>1]
    errors = sum(min(sum(r["endpoint"] == lab for r in group) for lab in ("A", "B"))
                 for group in groups.values())
    macro = {name: str(sum(Fraction(hits[name], len(groups[g])) for g, hits in group_hits.items())/len(groups))
             for name in RULES}
    return {"groups": len(groups), "groups_by_size": dict(sorted(Counter(map(len, groups.values())).items())),
            "repeated_groups": len(repeated),
            "repeated_groups_with_both_endpoint_leaders": sum(len({r["endpoint"] for r in g if r["endpoint"]}) == 2
                                                             for g in repeated),
            "fewest_errors_for_one_fixed_label_per_group": errors,
            "equal_group_weighted_hit_fractions": macro,
            "leave_one_group_out_change_minus_early_hit_count_range": [min(omitted), max(omitted)]}


def summarize(panel):
    observed = {pid: score(well) for pid, well in sorted(panel.items())}
    rows = [r for r in observed.values() if r is not None]
    comparison = Counter((r["hits"]["early"], r["hits"]["change"]) for r in rows)
    complete = [r for r in rows if all(r["observed_leaders"].get(t) is not None for t in DAYS)]
    retained = sum(len(set(r["observed_leaders"].values())) == 1 for r in complete)
    return {"total_populations": len(panel), "scorable": len(rows), "hits": totals(rows),
            "prediction_abstentions": {name: sum(r["predictions"][name] is None for r in rows) for name in RULES},
            "endpoint_ties": sum(r["endpoint"] is None for r in rows),
            "unique_prediction_joint_first_at_tied_endpoint": {
                name: sum(r["endpoint"] is None and r["predictions"][name] is not None for r in rows) for name in RULES},
            "paired": {"both": comparison[True, True], "early_only": comparison[True, False],
                       "change_only": comparison[False, True], "neither": comparison[False, False]},
            "by_source_condition": {g: {"n": len(group), **totals(group)}
                                    for g, group in sorted(stratify(rows, "condition_id").items())},
            "complete_unique_seven_visit_histories": len(complete), "uninterrupted_baseline_leaders": retained,
            "baseline_winner_recovered_by_endpoint_after_losing_observed_lead":
                sum(r["observed_leaders"][0] == r["endpoint"] for r in complete) - retained,
            "dependence_sensitivities": {k: dependence(rows, k) for k in ("label_pair_id", "strain_pair_id")},
            "per_population": observed}


if __name__ == "__main__":
    print(json.dumps(summarize(load_panel(ROOT/"fasanello_counts.tsv")), indent=2))
