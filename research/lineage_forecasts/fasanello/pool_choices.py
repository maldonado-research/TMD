"""Vary the endpoint measurement for a whole source pool while keeping forecasts fixed."""
import argparse
import csv
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

from technical import calls, read_counts

HERE = Path(__file__).resolve().parent


def evaluate(pools_path, counts_path):
    visits = read_counts(counts_path)
    with pools_path.open(newline="") as stream:
        roster = list(csv.DictReader(stream, delimiter="\t"))
    assert len(roster) == len(visits) and {row["population_id"] for row in roster} == visits.keys()
    by_pool = defaultdict(list)
    for row in roster:
        by_pool[row["pool_id"]].append(row["population_id"])
    contributions = {}
    for pool, wells in sorted(by_pool.items()):
        original, repeated = 0, 0
        complete = [calls(visits[w], "rerun") is not None for w in wells]
        assert len(set(complete)) == 1  # One source pool supplies all six incomplete series.
        for w in wells:
            fixed = calls(visits[w], "selected")
            for library in (("original", "rerun") if complete[0] else ("original",)):
                a, b = visits[w][25][library]
                assert a+b > 0
                if a == b:
                    continue
                outcome = 0 if a > b else 1
                margin = int(fixed["change"] == outcome) - int(fixed["early"] == outcome)
                if library == "original":
                    original += margin
                else:
                    repeated += margin
        contributions[pool] = {"n": len(wells), "original": original, "rerun": repeated if complete[0] else None}

    swappable = [k for k, v in contributions.items() if v["rerun"] is not None]
    choices = []
    for size in range(len(swappable)+1):
        for use_original in itertools.combinations(swappable, size):
            delta = sum(v["original"] if k in use_original or v["rerun"] is None else v["rerun"]
                        for k, v in contributions.items())
            choices.append((size, delta))
    totals = [delta for _, delta in choices]
    return {"per_pool_change_minus_early": contributions,
            "n_distinct_library_assignments": len(choices),
            "archived_total": totals[0], "all_original_endpoints_total": totals[-1],
            "attainable_totals_and_number_of_assignments": dict(sorted(Counter(totals).items())),
            "fewest_whole_pool_changes_to_tie": min((n for n, d in choices if d == 0), default=None),
            "fewest_whole_pool_changes_to_favor_early": min((n for n, d in choices if d < 0), default=None)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pools", type=Path, default=HERE/"endpoint_pools.tsv")
    parser.add_argument("--counts", type=Path, default=HERE/"technical_counts.tsv")
    args = parser.parse_args()
    print(json.dumps(evaluate(args.pools, args.counts), indent=2))
