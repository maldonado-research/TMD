"""Check assignment costs by enumerating attainable joint W, A, and M counts."""

import argparse
import json
from collections import Counter
from itertools import permutations
from pathlib import Path


# Each row gives the recorded support, the pair status, and its multiplicity.
# Unmatched parents have all four zero-cost choices.
HISTORICAL = [
    ("W", "unpaired", 16), ("A", "unpaired", 6), ("M", "unpaired", 3),
    ("WAMO", "unpaired", 1),
]
MATELA = [
    ("W", "unpaired", 37), ("A", "unpaired", 7), ("M", "unpaired", 1),
    ("MW", "unpaired", 3), ("AM", "unpaired", 2),
]
MONOCULTURE = [("W", "wrinkly_only", 2), ("WAMO", "neither", 2)]
COCULTURE = [
    ("W", "both_positive", 2), ("M", "both_positive", 1),
    ("M", "wrinkly_only", 1), ("WAMO", "neither", 1),
]
COHORTS = {
    "historical": HISTORICAL,
    "matela": MATELA,
    "monoculture": MONOCULTURE,
    "coculture": COCULTURE,
    "pooled": MONOCULTURE + COCULTURE,
}

INCREMENT = {"W": (1, 0, 0), "A": (0, 1, 0), "M": (0, 0, 1), "O": (0, 0, 0)}


def joint_costs(rows, scope, model):
    """Keep only the least edit cost for each joint count triple after each parent."""
    costs = {(0, 0, 0): 0}
    for support, pair, multiplicity in rows:
        free = set(support)
        eligible = scope == "all" or (scope == "singleton" and len(free) == 1) or scope == pair
        choices = free.copy()
        if eligible:
            choices.update("O" if model == "loss" else "WAMO")
        moves = [(*INCREMENT[label], int(label not in free)) for label in sorted(choices)]
        for _ in range(multiplicity):
            updated = {}
            for (w, a, m), previous in costs.items():
                for dw, da, dm, edit in moves:
                    state = w + dw, a + da, m + dm
                    cost = previous + edit
                    if state not in updated or cost < updated[state]:
                        updated[state] = cost
            costs = updated
    return costs


def pair_minima(costs, left, right):
    """Project joint counts to signed differences only after completing the roster."""
    least = {}
    for counts, edits in costs.items():
        gap = counts[left] - counts[right]
        if gap not in least or edits < least[gap]:
            least[gap] = edits
    baseline = [gap for gap, edits in least.items() if edits == 0]
    return {
        "baseline_range": [min(baseline), max(baseline)],
        "nonpositive": min((edits for gap, edits in least.items() if gap <= 0), default=None),
        "tie": least.get(0),
        "reversal": min((edits for gap, edits in least.items() if gap < 0), default=None),
    }


def equal(actual, expected, location):
    if actual != expected:
        raise ValueError(f"{location}: expected {expected!r}, found {actual!r}")


def synthetic_checks():
    from attribution import Parent, analyze

    ambiguous = analyze({"synthetic": [Parent("WM")]})["synthetic"]
    negative = analyze({"monoculture": [Parent("M", "wrinkly_only")]})["monoculture"]
    # The interval [-1, 1] can skip zero. A negative starting margin can
    # already meet a one-sided target while still requiring an edit to tie.
    cases = [
        (ambiguous, "singleton", "loss", "W-M", [-1, 1], 0, None, 0),
        (ambiguous, "all", "loss", "W-M", [-1, 1], 0, 1, 0),
        (negative, "both_positive", "correction", "A-M", [-1, -1], 0, None, 0),
        (negative, "all", "loss", "A-M", [-1, -1], 0, 1, 0),
        (negative, "all", "loss", "M-A", [1, 1], 1, 1, None),
        (negative, "all", "correction", "M-A", [1, 1], 1, 1, 1),
    ]
    for i, (table, scope, model, pair, bounds, nonpositive, tie, reversal) in enumerate(cases):
        actual = table[scope][model]["pairs"][pair]
        expected = {"baseline_range": bounds, "nonpositive": nonpositive,
                    "tie": tie, "reversal": reversal}
        equal(actual, expected, f"synthetic case {i + 1}")
    return len(cases)


def check_witness(witness, scope, model, event, minimum):
    equal(witness["minimum_edits"], minimum, f"{scope}/{model}/{event} witness cost")
    if minimum is None:
        return
    free = witness["unmatched_completion"]
    equal(len(free), 1, "co-culture unmatched parent")
    equal(free[0] in INCREMENT, True, "unmatched baseline choice")
    remaining = Counter({(status, support): n for support, status, n in COCULTURE
                         if len(support) == 1})
    after = Counter({"W": 2, "M": 2})
    after.update(free)
    equal(Counter(witness["before"]), after, "co-culture baseline counts")
    equal(len(witness["edits"]), minimum, "number of distinct edited parents")
    for edit in witness["edits"]:
        status, old, new = edit["pair"], edit["from"], edit["to"]
        equal(scope in {"all", "singleton", status}, True, "eligible co-culture edit")
        equal(remaining[status, old] > 0, True, "parent available for edit")
        equal(new in INCREMENT and new != old, True, "edit destination")
        if model == "loss":
            equal(new, "O", "loss destination")
        remaining[status, old] -= 1
        after[old] -= 1
        after[new] += 1
    equal(Counter(witness["after"]), after, "edited co-culture counts")
    w, a, m = (after[label] for label in "WAM")
    satisfied = {"nonpositive": m <= a, "tie": m == a, "reversal": m < a, "W>A>M": w > a > m}
    equal(satisfied[event], True, f"witness reaches {event}")


def verify(research):
    from attribution import analyze, load_cohorts

    cohorts = load_cohorts(research)
    equal(set(cohorts), set(COHORTS), "cohort names")
    for name, rows in COHORTS.items():
        expected = Counter()
        for support, pair, count in rows:
            expected[frozenset(support), pair] += count
        actual = Counter((frozenset(unit.support), unit.pair) for unit in cohorts[name])
        equal(actual, expected, f"{name} parent inventory")

    results = analyze(cohorts)
    cells = pairs = full_orders = witnesses = 0
    for name, rows in COHORTS.items():
        scopes = ["all", "singleton"]
        if name in {"monoculture", "coculture", "pooled"}:
            scopes.extend(["both_positive", "wrinkly_only"])
        for scope in scopes:
            for model in ("loss", "correction"):
                cell = results[name][scope][model]
                costs = joint_costs(rows, scope, model)
                for left, right in permutations(range(3), 2):
                    pair = f"{'WAM'[left]}-{'WAM'[right]}"
                    expected = pair_minima(costs, left, right)
                    for field, value in expected.items():
                        equal(cell["pairs"][pair][field], value, f"{name}/{scope}/{model}/{pair}/{field}")
                    pairs += 1
                if name == "coculture":
                    minimum = min((cost for (w, a, m), cost in costs.items() if w > a > m), default=None)
                    check_witness(cell["W>A>M"], scope, model, "W>A>M", minimum)
                    ma = pair_minima(costs, 2, 1)
                    for event in ("nonpositive", "tie", "reversal"):
                        check_witness(cell["witnesses"][event], scope, model, event, ma[event])
                    full_orders += 1
                    witnesses += 4
                cells += 1
    return {
        "cohort_inventories_checked": len(COHORTS),
        "model_cells_checked": cells,
        "directional_pair_results_checked": pairs,
        "coculture_joint_order_minima_checked": full_orders,
        "coculture_witness_records_checked": witnesses,
        "synthetic_edge_cases_checked": synthetic_checks(),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research", type=Path, default=Path(__file__).resolve().parent.parent)
    print(json.dumps(verify(parser.parse_args().research), indent=2))
