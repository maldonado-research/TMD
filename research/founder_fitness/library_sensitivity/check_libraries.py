"""Rescore fixed founder forecasts over complete endpoint-library choices."""
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from score import GENERATIONS, assay_ratio, combine_counts, decision, hit, project, share, sign, table

PREVIOUS = HERE.parents[1] / "lineage_forecasts" / "fasanello"
LIBRARIES = ("original", "rerun")
METRICS = ("baseline_hits", "assay_hits", "combined_hits", "assay_gain_hits",
           "combined_minus_baseline_hits", "combined_minus_baseline_mean_absolute_error")


def checked_table(path, digest):
    if sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError(f"Unexpected source table {path.name}")
    return table(path)


def reads(row, library):
    counts = [row[f"{library}_{side}"] for side in ("A", "B")]
    if counts == ["", ""]:
        return None
    a, b = map(int, counts)
    assert min(a, b) >= 0
    return (a, b) if a + b > 0 else None


def score_endpoint(initial, observed, ratios, horizon):
    a, b = observed
    start = Fraction(*initial)
    baseline = decision(start)
    assay = decision(math.prod(ratios))
    combined, projection = project(start, ratios, horizon)
    initial_share, final_share = share(*initial), share(a, b)
    winner = sign(a - b)
    base_hit, combined_hit = hit(baseline, winner), hit(combined, winner)
    error_difference = abs(projection - float(final_share)) - float(abs(initial_share - final_share))
    return (base_hit, hit(assay, winner), combined_hit, hit(assay, sign(final_share - initial_share)),
            combined_hit - base_hit, error_difference)


def collapse(values):
    # The error field remains a sum until all pool contributions are combined.
    return tuple(map(sum, zip(*values, strict=True)))


def present(values, denominator):
    return dict(zip(METRICS, (*values[:-1], round(values[-1] / denominator, 10))))


def ranges(results):
    return {key: [min(r[key] for r in results), max(r[key] for r in results)] for key in METRICS}


def evaluate():
    start_table = checked_table(PREVIOUS / "fasanello_counts.tsv",
                                "80845b53a4b82ffa739fd337e712a15269e56220be255b399fdffdf0b5d46ae9")
    all_counts = combine_counts(start_table)
    well_count = len(all_counts)
    technical = checked_table(PREVIOUS / "technical_counts.tsv",
                              "619c7d99a261304a5117fa24530573a2dabc2f7deca0aea812a1c2ce00a522bb")
    membership = checked_table(PREVIOUS / "endpoint_pools.tsv",
                               "e41d56ca0389257d7da00acfe5bb68f4da79b27902e7eb1e43bcfa0af7cc692a")
    founders = checked_table(HERE.parent / "founder_assays.tsv",
                             "c33ed0deac17cd8d2952e54f8e2a45eee4d3333327e608e7e3b92f19827b0c92")
    pools = defaultdict(list)
    repeats = defaultdict(list)
    visits = defaultdict(dict)
    for r in membership:
        pools[r["pool_id"]].append(r["population_id"])
    for r in founders:
        repeats[r["population_id"]].append(r)
    for r in technical:
        well, day = r["population_id"], int(r["day"])
        assert day not in visits[well] and reads(r, r["selected"]) == all_counts[well][day]
        visits[well][day] = r
    assert well_count == len(membership) == 76
    assert set(all_counts) == set(repeats) == set(visits) == {r["population_id"] for r in membership}
    endpoint_options = {}
    assay_options = defaultdict(lambda: defaultdict(list))
    composition = {}
    for pool, wells in sorted(pools.items()):
        days = (0, 10, 25)
        complete = [all(reads(visits[w][d], "rerun") is not None for d in days) for w in wells]
        assert len(set(complete)) == 1
        allowed = LIBRARIES if complete[0] else ("original",)
        selected = {visits[w][25]["selected"] for w in wells}
        assert selected == {allowed[-1]}
        positive = sum(reads(visits[w][25], "rerun") is not None for w in wells)
        composition[pool] = dict(wells=len(wells), positive_depth_repeat_endpoints=positive,
                                 complete_repeated_trajectories=sum(complete), libraries=list(allowed))
        contributions = defaultdict(list)
        for w in wells:
            r = sorted(repeats[w], key=lambda v: int(v["replicate"]))
            assert [int(v["replicate"]) for v in r] == [1, 2, 3, 4]
            assert len({(v["condition_id"], v["assay_pool_id"]) for v in r}) == 1
            horizon = GENERATIONS[int(r[0]["condition_id"])]
            ratios = [assay_ratio(v) for v in r]
            initial = all_counts[w][0]
            for library in allowed:
                observed = reads(visits[w][25], library)
                contributions[library].append(score_endpoint(initial, observed, ratios, horizon))
            # This second sensitivity fixes the endpoint to the author's selected reading.
            for rep, ratio in enumerate(ratios):
                assay_options[r[0]["assay_pool_id"]][rep].append(
                    score_endpoint(initial, all_counts[w][25], [ratio], horizon))
        endpoint_options[pool] = {k: collapse(v) for k, v in contributions.items()}

    scores = []
    for choice in product(*(options.keys() for options in endpoint_options.values())):
        vector = collapse(options[library] for options, library in zip(endpoint_options.values(), choice))
        scores.append(present(vector, well_count))
    assert len(scores) == 128
    source_selected = scores[-1]
    all_original = scores[0]
    distribution = Counter(item["combined_minus_baseline_hits"] for item in scores)
    assert len(assay_options) == 12
    by_pool = [[collapse(data[i]) for i in range(4)] for data in assay_options.values()]
    # Disjoint membership makes each additive metric independently optimizable pool by pool.
    minima = collapse([tuple(map(min, zip(*choices))) for choices in by_pool])
    maxima = collapse([tuple(map(max, zip(*choices))) for choices in by_pool])
    return {
        "wells": well_count,
        "endpoint_library_choices": {
            "pool_composition": composition, "assignments": len(scores),
            "source_selected": source_selected, "all_original_endpoints": all_original,
            "attainable_ranges": ranges(scores),
            "combined_minus_baseline_hits_assignment_counts": dict(sorted(distribution.items())),
        },
        "single_founder_repeat_per_pool_selected_endpoint": {
            "pools": len(by_pool), "assignments": 4 ** len(by_pool),
            "attainable_ranges": ranges([present(minima, well_count), present(maxima, well_count)]),
        },
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
