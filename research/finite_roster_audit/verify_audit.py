"""Verify the synthetic finite-roster audit by enumerating labeled samples and tables."""

import json
import sys
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, combinations_with_replacement, product

sys.dont_write_bytecode = True
import audit

ROWS = ("W", "A", "M", "U_pass", "U_fail")
CLASSES = ("W", "A", "M", "Other")
TAILS = (Fraction(1, 800), Fraction(1, 20), Fraction(1, 6), Fraction(1, 4))


def check(actual, expected, case):
    if actual != expected:
        raise AssertionError(f"{case}: expected {expected!r}, got {actual!r}")


@lru_cache(None)
def draw_counts(N, n, true_count):
    """Count equally likely labeled subsets without a hypergeometric formula."""
    return Counter(
        sum(i < true_count for i in selected)
        for selected in combinations(range(N), n)
    )


@lru_cache(None)
def complete_acceptance(N, n, x, tail):
    accepted = []
    for true_count in range(N + 1):
        draws = draw_counts(N, n, true_count)
        size = sum(draws.values())
        below = sum(freq for value, freq in draws.items() if value <= x)
        above = sum(freq for value, freq in draws.items() if value >= x)
        if min(below, above) >= tail * size:
            accepted.append(true_count)
    return frozenset(accepted)


@lru_cache(None)
def incomplete_acceptance(N, n, y, r, tail):
    return frozenset().union(
        *(complete_acceptance(N, n, x, tail) for x in range(y, y + r + 1))
    )


def verify_cells(receipt):
    for N in range(9):
        for n in range(N + 1):
            for y in range(n + 1):
                for r in range(n - y + 1):
                    for tail in TAILS:
                        accepted = incomplete_acceptance(N, n, y, r, tail)
                        lo, hi = audit.cell_interval(N, n, y, r, tail)
                        check(frozenset(range(lo, hi + 1)), accepted,
                              ("cell", N, n, y, r, str(tail)))
                        receipt["small_cell_interval_cases"] += 1

    # With N=4, a singleton observation has tail mass exactly 1/4 for
    # one of four successes (or one of four failures).
    for offset, expected in [
        (Fraction(-1, 10000), ((1, 4), (0, 3))),
        (Fraction(0), ((1, 4), (0, 3))),
        (Fraction(1, 10000), ((2, 4), (0, 2))),
    ]:
        tail = Fraction(1, 4) + offset
        for observed, bounds in zip((1, 0), expected):
            check(tuple(audit.cell_interval(4, 1, observed, 0, tail)), bounds,
                  ("exact threshold", str(tail), observed))
            receipt["boundary_cases"] += 1


def verify_coverage(receipt):
    """Adversary may choose which positives and negatives to mask after each draw."""
    worst = Fraction(1)
    witness = None
    for N in range(9):
        for n in range(N + 1):
            for truth in range(N + 1):
                draws = draw_counts(N, n, truth)
                size = sum(draws.values())
                for tail in TAILS:
                    lose_lower = lose_upper = lose_either = 0
                    for x, freq in draws.items():
                        any_lower = any_upper = False
                        for hide_positive in range(x + 1):
                            for hide_negative in range(n - x + 1):
                                y = x - hide_positive
                                r = hide_positive + hide_negative
                                lo, hi = audit.cell_interval(N, n, y, r, tail)
                                any_lower |= truth < lo
                                any_upper |= truth > hi
                                receipt["coverage_mask_count_cases"] += 1
                        lose_lower += freq * any_lower
                        lose_upper += freq * any_upper
                        lose_either += freq * (any_lower or any_upper)
                    case = ("coverage", N, n, truth, str(tail))
                    check(lose_lower <= size * tail, True, (*case, "lower"))
                    check(lose_upper <= size * tail, True, (*case, "upper"))
                    check(lose_either <= size * 2 * tail, True, (*case, "either"))
                    coverage = Fraction(size - lose_either, size)
                    if coverage < worst:
                        worst = coverage
                        witness = dict(N=N, n=n, truth=truth, tail=str(tail),
                                       covered_draws=size - lose_either, total_draws=size)
                    receipt["coverage_design_truth_tail_cases"] += 1
    receipt["minimum_observed_cell_coverage"] = str(worst)
    receipt["minimum_coverage_example"] = witness


@lru_cache(None)
def histograms(size):
    """All possible four-class histograms at a fixed total."""
    return tuple(
        tuple(labels.count(j) for j in range(len(CLASSES)))
        for labels in combinations_with_replacement(range(len(CLASSES)), size)
    )


def possible_rows(N, n, known, tail, random_sample):
    if random_sample:
        missing = n - sum(known)
        accepts = [incomplete_acceptance(N, n, v, missing, tail) for v in known]
        return [h for h in histograms(N) if all(h[j] in a for j, a in enumerate(accepts))]
    return [h for h in histograms(N) if all(v >= k for v, k in zip(h, known))]


def extrema(values):
    return min(values), max(values)


def verify_rows(receipt):
    for N in range(6):
        for n in range(N + 1):
            for verified in range(n + 1):
                for known in histograms(verified):
                    for mode, tail in [(False, TAILS[0]), (True, TAILS[0]), (True, TAILS[-1])]:
                        valid = possible_rows(N, n, known, tail, mode)
                        expected = dict(zip(CLASSES, map(extrema, zip(*valid))))
                        reported = audit.row_bounds(N, n, dict(zip(CLASSES, known)), tail, mode)
                        check({key: tuple(v) for key, v in reported.items()}, expected,
                              ("row", N, n, known, str(tail), mode))
                        receipt["row_projection_cases"] += 1
    # At a deliberately high test tail the individual M interval is [1,2].
    # Both other positive classes require three members, leaving exactly one M.
    known = (2, 2, 1, 0)
    tail = Fraction(49, 100)
    check(extrema(incomplete_acceptance(7, 5, 1, 0, tail)), (1, 2), "raw M range")
    check(possible_rows(7, 5, known, tail, True), [(3, 3, 1, 0)], "unique table")
    answer = audit.row_bounds(7, 5, dict(zip(CLASSES, known)), tail, True)
    check(tuple(answer["M"]), (1, 1), "active row-sum tightening")


def share_record(values, possible_empty):
    return {"lower": str(min(values)) if values else None,
            "upper": str(max(values)) if values else None,
            "possible_empty": possible_empty}


def check_share(actual, expected, case):
    check({k: actual[k] for k in expected}, expected, case)


def verify_shares(receipt):
    intervals = list(combinations_with_replacement(range(6), 2))
    for (al, ah), (bl, bh) in product(intervals, repeat=2):
        values = set()
        empty = False
        for a, b in product(range(al, ah + 1), range(bl, bh + 1)):
            if a + b:
                values.add(Fraction(a, a + b))
            else:
                empty = True
        check_share(audit.share_interval((al, ah), (bl, bh)), share_record(values, empty),
                    ("share", (al, ah), (bl, bh)))
        receipt["share_rectangle_cases"] += 1


def payload(design, mode):
    rows = {}
    for s, (N, n, known) in zip(ROWS, design):
        rows[s] = {"N": N, "n": n, "verified": dict(zip(CLASSES, known))}
    return {"schema": "finite-roster-audit-v1", "alpha": "1/20",
            "selection": mode, "rows": rows}


def verify_joint_case(design, mode, receipt):
    p = payload(design, mode)
    result = audit.analyze(p)
    random_sample = mode == "stratified_srswor"
    check(result["coverage"], "19/20" if random_sample else "deterministic", "reported coverage")
    check(result["tail_per_cell_side"], "1/800" if random_sample else None, "Bonferroni tail")
    options = [possible_rows(N, n, known, TAILS[0], random_sample) for N, n, known in design]
    actual_rows = result["row_truth_bounds"]
    for s, opts in zip(ROWS, options):
        expected = dict(zip(CLASSES, map(extrema, zip(*opts))))
        check({k: tuple(v) for k, v in actual_rows[s].items()}, expected, ("integrated row", s))
    totals = [set() for _ in CLASSES]
    shares = [set() for _ in CLASSES]
    pairs = [(0, 1), (0, 2), (1, 2)]
    differences = {f"{CLASSES[i]}-{CLASSES[j]}": set() for i, j in pairs}
    strict_leaders = set(CLASSES[:3])
    for table in product(*options):
        counts = [sum(row[j] for row in table) for j in range(4)]
        for i, j in pairs:
            differences[f"{CLASSES[i]}-{CLASSES[j]}"].add(counts[i] - counts[j])
        strict_leaders.intersection_update(
            CLASSES[i] for i in range(3) if all(counts[i] > counts[j] for j in range(3) if j != i)
        )
        for j in range(4):
            total = counts[j]
            totals[j].add(total)
            correct = table[j][j] if j < 3 else sum(row[j] for row in table[:4])
            if total:
                shares[j].add(Fraction(correct, total))
        receipt["joint_tables_enumerated"] += 1
    expected = {key: extrema(values) for key, values in differences.items()}
    check({k: tuple(v) for k, v in result["route_count_differences"].items()}, expected,
          "integrated pairwise route differences")
    check(result["certified_strict_leader"], next(iter(strict_leaders), None),
          "strict leader in every feasible table")
    for j, cls in enumerate(CLASSES):
        check(tuple(result["truth_totals"][cls]), extrema(totals[j]), ("integrated total", cls))
        actual = (result["correct_call_given_truth"][cls] if j < 3
                  else result["gate_pass_given_other"])
        check_share(actual, share_record(shares[j], 0 in totals[j]), ("integrated share", cls))
    receipt["joint_design_cases"] += 1


def verify_integration(receipt):
    z = (0, 0, 0, 0)
    # On the census the Other gate numerator includes the residual pass row.
    census = [(2, 2, (1, 0, 0, 1)), (1, 1, (1, 0, 0, 0)), (0, 0, z),
              (1, 1, (0, 0, 0, 1)), (1, 1, (0, 0, 0, 1))]
    mixed = [(2, 1, (1, 0, 0, 0)), (2, 2, (0, 0, 0, 1)), (1, 0, z),
             (2, 2, (0, 1, 0, 0)), (2, 1, z)]
    empty = [(0, 0, z)] * 5
    separated = [(14, 7, (7, 0, 0, 0)), *empty[1:4], (1, 1, (0, 0, 0, 1))]
    for mode in ("stratified_srswor", "unspecified"):
        for design in [census, mixed, empty, separated]:
            verify_joint_case(design, mode, receipt)
        # All seven W: one of 3,432 draws if there are seven W, eight draws
        # if there are eight W. Only the latter reaches the 1/800 threshold.
        expected_low = 8 if mode == "stratified_srswor" else 7
        different = audit.analyze(payload(separated, mode))
        check(tuple(different["truth_totals"]["W"]), (expected_low, 14),
              ("inference depends on selection", mode))
        found = audit.analyze(payload(census, mode))
        check_share(found["gate_pass_given_other"], share_record([Fraction(2, 3)], False),
                    "census gate share")
        check_share(found["correct_call_given_truth"]["W"], share_record([Fraction(1, 2)], False),
                    "census correct W share")
        for name in ("A", "M"):
            check_share(found["correct_call_given_truth"][name], share_record([], True),
                        ("absent truth", name))
    # A convenience sample concentrated in W can leave nine unseen Other items.
    adversarial = [(10, 1, (1, 0, 0, 0)), *empty[1:]]
    reported = audit.analyze(payload(adversarial, "unspecified"))
    check(tuple(reported["truth_totals"]["Other"]), (0, 9), "convenience sample")
    called = [(10, 10, (10, 0, 0, 0)), (8, 8, (0, 8, 0, 0)),
              (2, 2, (0, 0, 2, 0)), (0, 0, z)]
    for n, known, bounds, leader in [(0, z, (-3, 7), None), (4, (0, 4, 0, 0), (-3, -1), "A")]:
        example = [*called, (5, n, known)]
        verify_joint_case(example, "unspecified", receipt)
        reported = audit.analyze(payload(example, "unspecified"))
        check(tuple(reported["route_count_differences"]["W-A"]), bounds, "W/A reversal")
        check(reported["certified_strict_leader"], leader, "leader after verifying failed calls")


def verify_joint_coverage(receipt):
    """Count simultaneous coverage with independent within-row draws in one example."""
    populations = [(0,) * 7 + (3,) * 7, (1, 1, 2, 3)]
    all_ways = covered_ways = 1
    for labels, n in zip(populations, (7, 2)):
        truth = tuple(labels.count(j) for j in range(4))
        samples = Counter(
            tuple(sample.count(j) for j in range(4))
            for sample in combinations(labels, n)
        )
        # Distinct positions, including repeated labels, are sampled uniformly.
        covered = 0
        for sample, ways in samples.items():
            every_mask_covers = True
            for mask in product(*(range(count + 1) for count in sample)):
                bounds = audit.row_bounds(len(labels), n, dict(zip(CLASSES, mask)),
                                          TAILS[0], True)
                every_mask_covers &= all(
                    bounds[c][0] <= v <= bounds[c][1] for c, v in zip(CLASSES, truth)
                )
                receipt["joint_coverage_mask_cases"] += 1
            if every_mask_covers:
                covered += ways
        all_ways *= sum(samples.values())
        covered_ways *= covered
    # The other three rows are empty. Either monochromatic size-seven draw
    # misses at least one true cell; all other outcomes cover for every mask.
    check((covered_ways, all_ways), (20580, 20592), "simultaneous table coverage")
    check(Fraction(covered_ways, all_ways) >= Fraction(19, 20), True, "familywise coverage")
    receipt["example_joint_coverage"] = {"covered_draws": covered_ways, "total_draws": all_ways,
                                        "coverage": str(Fraction(covered_ways, all_ways))}


def verify_rejections(receipt):
    base = payload([(1, 0, (0, 0, 0, 0))] * 5, "unspecified")
    for path, value in [
        (("schema",), "unknown"),
        (("selection",), "replacement"),
        (("alpha",), "0"),
        (("alpha",), "1"),
        (("rows", "W", "N"), -1),
        (("rows", "W", "N"), True),
        (("rows", "W", "n"), 2),
        (("rows", "W", "verified", "A"), 1),
        (("rows", "W", "verified", "Other"), -1),
        (("rows", "W", "verified", "Other"), 0.5),
    ]:
        malformed = deepcopy(base)
        d = malformed
        for key in path[:-1]:
            d = d[key]
        d[path[-1]] = value
        try:
            audit.analyze(malformed)
        except ValueError:
            receipt["invalid_fixture_rejections"] += 1
        else:
            raise AssertionError(f"invalid fixture accepted: {path!r} = {value!r}")


def main():
    receipt = Counter()
    verify_cells(receipt)
    verify_coverage(receipt)
    verify_rows(receipt)
    verify_shares(receipt)
    verify_integration(receipt)
    verify_joint_coverage(receipt)
    verify_rejections(receipt)
    print(json.dumps({"status": "pass", **receipt}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
