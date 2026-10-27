#!/usr/bin/env python3
"""Exhaustively verify anchored binary-overlap bounds for n <= 6 by default.

The left rows have c score-positive labels; the right rows have a
annotation-positive labels.  A full permutation maps each left row to a
right row.  Every subset of its pairs is an injective partial matching,
representing authenticated anchors.  All full permutations extending that
partial matching contribute their overlap to its independently observed
attainable set.

The bounds under test are:
    lower = max(k11, a + c - n + k00)
    upper = min(a - k01, c - k10)
where the first cell index is score status and the second is annotation
status.  The test compares the whole attainable set, not only endpoints.

A case means one (n, a, c, exact partial matching) combination.  At fixed n,
there are (n+1)^2 * sum_m binom(n,m)^2 * m! cases.  Binary label locations
are canonical without loss of generality: independent permutations of
the left and right row names transport any label arrangement to these
canonical positions and preserve the attainable overlaps.

This is a finite combinatorial check, not an empirical biological result
or evidence authenticating any row correspondence, marginal, or label.
Only the Python standard library is required.  Runtime grows factorially.
"""

import argparse
import json
from itertools import permutations
from math import comb, factorial


def verify(max_n):
    """Return counts after checking every attainable set through max_n."""
    checked = 0
    per_n = []
    for n in range(max_n + 1):
        all_permutations = list(permutations(range(n)))
        subsets = [
            tuple(i for i in range(n) if (mask >> i) & 1)
            for mask in range(1 << n)
        ]
        n_checked = 0
        for a in range(n + 1):
            for c in range(n + 1):
                attainable = {}
                for permutation in all_permutations:
                    overlap = sum(j < a for j in permutation[:c])
                    for selected in subsets:
                        anchor = tuple((i, permutation[i]) for i in selected)
                        attainable.setdefault(anchor, set()).add(overlap)

                for anchor, actual in attainable.items():
                    k11 = sum(i < c and j < a for i, j in anchor)
                    k10 = sum(i < c and j >= a for i, j in anchor)
                    k01 = sum(i >= c and j < a for i, j in anchor)
                    k00 = sum(i >= c and j >= a for i, j in anchor)
                    lower = max(k11, a + c - n + k00)
                    upper = min(a - k01, c - k10)
                    expected = set(range(lower, upper + 1))
                    if actual != expected:
                        raise AssertionError(
                            dict(n=n, a=a, c=c, anchor=anchor,
                                 actual=sorted(actual), expected=sorted(expected))
                        )
                    n_checked += 1

        partial_matchings = sum(
            comb(n, m) ** 2 * factorial(m) for m in range(n + 1)
        )
        expected_cases = (n + 1) ** 2 * partial_matchings
        if n_checked != expected_cases:
            raise AssertionError((n, n_checked, expected_cases))
        checked += n_checked
        per_n.append(dict(n=n, partial_matchings=partial_matchings,
                          marginal_pairs=(n + 1) ** 2, cases=n_checked))
    return dict(status="PASS", max_n=max_n, total_cases=checked, per_n=per_n,
                criterion="entire attainable overlap set equals every integer in the bounds")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-n", type=int, default=6,
                        help="largest finite universe to enumerate (default: 6)")
    args = parser.parse_args()
    if args.max_n < 0:
        parser.error("--max-n must be nonnegative")
    print(json.dumps(verify(args.max_n), indent=2))


if __name__ == "__main__":
    main()
