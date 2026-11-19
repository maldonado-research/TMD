"""Minimum parent-label edits for retrospective count comparisons.

Run from any directory. The default receipt location is the sibling research
directory layout of the TMD repository. Use --research to point to another copy.
"""

import argparse
import json
from dataclasses import dataclass
from itertools import permutations, product
from pathlib import Path

LABELS = "WAMO"


@dataclass(frozen=True)
class Parent:
    support: str
    pair: str = "unpaired"


def load_cohorts(research):
    ranks = research / "archived_route_ranks"
    history = json.loads((ranks / "historical_receipt.json").read_text())
    matela = json.loads((ranks / "matela_receipt.json").read_text())
    paired = research / "archived_rank_robustness" / "howells_receipt.json"
    arms = json.loads(paired.read_text())["arms"]
    supports = {
        "historical": history["allowed_classes"],
        "matela": matela["focal_class_union_across_archived_wrinkly_clones_in_each_parent"],
    }
    cohorts = {
        name: [Parent(labels) for labels, n in counts.items() for _ in range(n)]
        for name, counts in supports.items()
    }
    for name, arm in arms.items():
        counts = arm["clones_by_phenotype_and_recorded_family"]["wrinkly"]
        shared = arm["paired_clones_with_same_recorded_family"]
        pairs = arm["pairs_with_any_recorded_family"]
        # The aggregate reconstruction relies on every doubly marked pair
        # having the same family and every unmatched wrinkly endpoint being in
        # a doubly unmatched pair.
        assert sum(shared.values()) == pairs["both"] and pairs["smooth_only"] == 0
        assert counts["unmatched"] == pairs["neither"]
        rows = []
        for label in "WAM":
            assert 0 <= shared[label] <= counts[label]
            rows.extend([Parent(label, "both_positive")] * shared[label])
            rows.extend([Parent(label, "wrinkly_only")] * (counts[label] - shared[label]))
        rows.extend([Parent(LABELS, "neither")] * counts["unmatched"])
        assert len(rows) == arm["parents"]
        cohorts[name] = rows
    cohorts["pooled"] = cohorts["monoculture"] + cohorts["coculture"]
    return cohorts


def label_costs(parent, eligibility, model):
    """A supported baseline label is always free, even for an ineligible parent."""
    eligible = (eligibility == "all" or eligibility == parent.pair
                or (eligibility == "singleton" and len(parent.support) == 1))
    allowed_edits = LABELS if model == "correction" else "O"
    costs = {label: 1 for label in allowed_edits} if eligible else {}
    costs.update(dict.fromkeys(parent.support, 0))
    return costs


def budget_for(margin, gains, target):
    if margin <= target:
        return 0
    for edits, gain in enumerate(sorted(gains, reverse=True), start=1):
        margin -= gain
        if margin <= target:
            return edits
    return None


def pair_frontier(choices, leader, challenger):
    score = {label: int(label == leader) - int(label == challenger) for label in LABELS}
    low = high = 0
    gains = []
    # A negative baseline margin may need upward edits to reach an exact tie.
    # Track minimum cost by signed difference, including gaps in score support.
    exact_cost = {0: 0}
    for costs in choices:
        free = [score[label] for label, cost in costs.items() if cost == 0]
        low += min(free)
        high += max(free)
        gains.append(min(free) - min(score[label] for label in costs))
        updated = {}
        for label, cost in costs.items():
            delta = score[label]
            for difference, spent in exact_cost.items():
                total = difference + delta
                candidate = spent + cost
                if total not in updated or candidate < updated[total]:
                    updated[total] = candidate
        exact_cost = updated
    return {"baseline_range": [low, high],
            "nonpositive": budget_for(low, gains, 0),
            "tie": exact_cost.get(0),
            "reversal": budget_for(low, gains, -1)}


def witness(parents, choices, after):
    before = [new if new in p.support else p.support[0] for p, new in zip(parents, after)]
    edits = [{"pair": p.pair, "from": old, "to": new}
             for p, old, new in zip(parents, before, after) if old != new]
    assert len(edits) == sum(costs[new] for costs, new in zip(choices, after))
    return {"minimum_edits": len(edits), "before": {c: before.count(c) for c in LABELS},
            "after": {c: after.count(c) for c in LABELS}, "edits": edits,
            "unmatched_completion": [new for p, new in zip(parents, before) if p.pair == "neither"]}


def coculture_witnesses(parents, choices):
    best = {}
    for after in product(*choices):
        w, a, m = (after.count(label) for label in "WAM")
        conditions = {"nonpositive": m <= a, "tie": m == a,
                      "reversal": m < a, "W>A>M": w > a > m}
        if not any(conditions.values()):
            continue
        result = witness(parents, choices, after)
        # Break cost ties by completing the unmatched parent as A when possible
        # and favoring simple deletions. Only the minimum cost bears inference.
        priority = (result["minimum_edits"], -result["unmatched_completion"].count("A"),
                    -sum(edit["to"] == "O" for edit in result["edits"]), after)
        for event, holds in conditions.items():
            if holds and (event not in best or priority < best[event][0]):
                best[event] = priority, result
    return {event: best[event][1] if event in best else {"minimum_edits": None}
            for event in ["nonpositive", "tie", "reversal", "W>A>M"]}


def analyze(cohorts):
    results = {}
    for name, parents in cohorts.items():
        eligibility = ["all", "singleton"]
        if name in {"monoculture", "coculture", "pooled"}:
            eligibility += ["both_positive", "wrinkly_only"]
        results[name] = {}
        for eligible in eligibility:
            cells = {}
            for model in ("loss", "correction"):
                choices = [label_costs(p, eligible, model) for p in parents]
                pairs = {f"{i}-{j}": pair_frontier(choices, i, j)
                         for i, j in permutations("WAM", 2)}
                cell = {"pairs": pairs}
                if name == "coculture":
                    examples = coculture_witnesses(parents, choices)
                    cell["W>A>M"] = examples.pop("W>A>M")
                    assert all(examples[event]["minimum_edits"] == pairs["M-A"][event]
                               for event in examples)
                    cell["witnesses"] = examples
                cells[model] = cell
            results[name][eligible] = cells
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(json.dumps(analyze(load_cohorts(args.research)), indent=2))
