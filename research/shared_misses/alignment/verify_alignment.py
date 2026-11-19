"""Verify split-profile alignment counts by a subset dynamic program and independent mean formula."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import json
from pathlib import Path

from replay_alignment import read_pairs, read_table


def distribution(blocks):
    """Count distinct assignations by used B indices, intersection score, and fixed points."""
    combined = Counter({(0, 0): 1})
    mean = Fraction()
    observed = 0
    for block in blocks.values():
        n = len(block)
        matrix = [[len(a.intersection(b)) for _, b in block] for a, _ in block]
        observed += sum(matrix[i][i] for i in range(n))
        mean += Fraction(sum(sum(row) for row in matrix), n)
        states = Counter({(0, 0, 0): 1})
        for i, row in enumerate(matrix):
            choices = Counter()
            for (mask, score, fixed), count in states.items():
                for j, weight in enumerate(row):
                    bit = 1 << j
                    if not mask & bit:
                        choices[mask | bit, score + weight, fixed + (i == j)] += count
            states = choices
        updated = Counter()
        for (_, score, fixed), count in states.items():
            for (base, original), multiplicity in combined.items():
                updated[base + score, original + fixed] += count * multiplicity
        combined = updated
    scores = Counter()
    for (score, fixed), count in combined.items():
        scores[score] += count
    maximum = max(scores)
    fixed = {f: n for (score, f), n in combined.items() if score == maximum}
    return observed, scores, fixed, mean


def check(rows, data):
    all_wide = set.intersection(*(a | b for _, _, a, b in rows))
    for name, exclude in [("all_sites", set()), ("excluding_two_widely_detected_sites", all_wide)]:
        for grouping in ("organ_type", "organ_type_and_unit"):
            cells = defaultdict(list)
            for organ, unit, a, b in rows:
                label = organ if grouping == "organ_type" else (organ, unit)
                cells[label].append((a - exclude, b - exclude))
            observed, hist, fixed, mean = distribution(cells)
            ref = data[name][grouping]
            assert observed == ref["recorded_pairing_double_positives"]
            assert dict(hist) == {int(k): v for k, v in ref["score_counts"].items()}
            assert fixed == {int(k): v for k, v in ref["correct_pair_counts_among_maximizers"].items()}
            assert mean == Fraction(ref["mean"])
            assert sum(hist.values()) == ref["labeled_reassignments"]
            assert sum(hist[i] for i in hist if i >= observed) == ref["at_least_observed"]
            assert Fraction(ref["reference_fraction"]) == Fraction(ref["at_least_observed"], sum(hist.values()))
    # Directly verify that the widest sites contribute a constant offset to every permutation.
    groups = defaultdict(list)
    for organ, unit, a, b in rows:
        groups[organ].append((a & all_wide, b & all_wide))
    _, wide_scores, _, _ = distribution(groups)
    assert len(all_wide) == 2 and wide_scores == {37: 3483648000}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("s1", "s2", "s5", "receipt"):
        parser.add_argument(key, type=Path)
    args = parser.parse_args()
    rows = read_pairs(*(read_table(getattr(args, k.lower()), k) for k in ("S1", "S2", "S5")))
    check(rows, json.loads(args.receipt.read_bytes()))
    print("All four alignment distributions, means and identity-count spectra agree with subset enumeration.")
