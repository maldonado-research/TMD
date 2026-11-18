"""Exact count bounds for one fully enumerated validation roster."""

import argparse
import json
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path

ROWS = ("W", "A", "M", "U_pass", "U_fail")
TRUTHS = ("W", "A", "M", "Other")
MODES = ("stratified_srswor", "unspecified")


def count(value):
    if type(value) is not int or value < 0:
        raise ValueError("counts must be nonnegative integers")
    return value


def require_keys(obj, keys, label):
    if not isinstance(obj, dict) or set(obj) != set(keys):
        raise ValueError(f"{label} must contain exactly {', '.join(keys)}")


def lower_total(N, n, x, tail):
    """Smallest population total with P(X >= x) >= tail."""
    if x == 0 or n == N:
        return x
    denominator = comb(N, n)
    threshold = (denominator * tail.numerator + tail.denominator - 1) // tail.denominator
    low, high = x, N - n + x
    while low < high:
        k = (low + high) // 2
        # Here x is in the support because x <= k <= N-n+x.
        ways = comb(k, x) * comb(N - k, n - x)
        total = ways
        j = x
        while total < threshold and j < min(n, k):
            ways = ways * (k - j) * (n - j) // ((j + 1) * (N - k - n + j + 1))
            total += ways
            j += 1
        if total >= threshold:
            high = k
        else:
            low = k + 1
    return low


def cell_interval(N, n, y, r, tail):
    """y verified members, r sampled records with unknown membership."""
    for value in (N, n, y, r):
        count(value)
    if n > N or y + r > n or not 0 < tail < Fraction(1, 2):
        raise ValueError("inconsistent sample counts or tail allocation")
    # The upper bound is N minus the lower bound for verified nonmembers.
    return lower_total(N, n, y, tail), N - lower_total(N, n, n - y - r, tail)


def row_bounds(N, n, known, tail, random_sample):
    """Bound each reference count and impose the fixed row total."""
    count(N)
    count(n)
    resolved = sum(count(v) for v in known.values())
    if not (resolved <= n <= N):
        raise ValueError("require sum(verified) <= n <= N")
    if random_sample:
        bounds = {t: cell_interval(N, n, y, n - resolved, tail) for t, y in known.items()}
    else:
        bounds = {t: (y, N - resolved + y) for t, y in known.items()}
    low_sum = sum(lo for lo, _ in bounds.values())
    high_sum = sum(hi for _, hi in bounds.values())
    if not low_sum <= N <= high_sum:
        raise ValueError("empty row confidence set")
    return {
        t: (max(lo, N - (high_sum - hi)), min(hi, N - (low_sum - lo)))
        for t, (lo, hi) in bounds.items()
    }


def share_interval(a, b):
    """Range of a/(a+b) conditional on a+b>0, for two disjoint row groups."""
    a_lo, a_hi = a
    b_lo, b_hi = b
    if a_hi + b_hi == 0:
        return {"lower": None, "upper": None, "possible_empty": True}
    lower = Fraction(a_lo, a_lo + b_hi) if a_lo + b_hi else Fraction(1)
    upper = Fraction(a_hi, a_hi + b_lo) if a_hi + b_lo else Fraction(0)
    return {"lower": str(lower), "upper": str(upper), "possible_empty": a_lo + b_lo == 0}


def analyze(payload):
    require_keys(payload, ("schema", "alpha", "selection", "rows"), "input")
    if payload["schema"] != "finite-roster-audit-v1" or payload["selection"] not in MODES:
        raise ValueError("unsupported schema or selection")
    if not isinstance(payload["alpha"], str):
        raise ValueError("alpha must be an exact probability string")
    alpha = Fraction(payload["alpha"])
    if not 0 < alpha < 1:
        raise ValueError("require 0 < alpha < 1")
    random_sample = payload["selection"] == "stratified_srswor"
    tail = alpha / (2 * len(ROWS) * len(TRUTHS))
    require_keys(payload["rows"], ROWS, "rows")
    bounds = {}
    for name in ROWS:
        row = payload["rows"][name]
        require_keys(row, ("N", "n", "verified"), name)
        require_keys(row["verified"], TRUTHS, f"{name}.verified")
        bounds[name] = row_bounds(row["N"], row["n"], row["verified"], tail, random_sample)

    def subtotal(t, names):
        return tuple(sum(bounds[name][t][side] for name in names) for side in (0, 1))

    def share(t, names):
        return share_interval(subtotal(t, names), subtotal(t, [h for h in ROWS if h not in names]))

    routes = ("W", "A", "M")
    truth_totals = {t: subtotal(t, ROWS) for t in TRUTHS}
    differences = {}
    certified_leaders = set(routes)
    for first, second in combinations(routes, 2):
        low = truth_totals[first][0] - truth_totals[second][1]
        high = truth_totals[first][1] - truth_totals[second][0]
        differences[f"{first}-{second}"] = (low, high)
        # Certify a leader only if it strictly wins every pair in the set.
        if low <= 0:
            certified_leaders.discard(first)
        if high >= 0:
            certified_leaders.discard(second)
    return {
        "estimand": "fixed roster, relative to the declared reference standard",
        "selection": payload["selection"],
        "coverage": str(1 - alpha) if random_sample else "deterministic",
        "tail_per_cell_side": str(tail) if random_sample else None,
        "roster_size": sum(row["N"] for row in payload["rows"].values()),
        "sampled": sum(row["n"] for row in payload["rows"].values()),
        "sampled_unresolved": sum(row["n"] - sum(row["verified"].values()) for row in payload["rows"].values()),
        "row_truth_bounds": bounds,
        "truth_totals": truth_totals,
        "route_count_differences": differences,
        "certified_strict_leader": next(iter(certified_leaders), None),
        "gate_pass_given_other": share("Other", [h for h in ROWS if h != "U_fail"]),
        "correct_call_given_truth": {t: share(t, [t]) for t in ("W", "A", "M")},
    }


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key}")
        result[key] = value
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        with args.input.open(encoding="utf-8") as handle:
            result = analyze(json.load(handle, object_pairs_hook=unique_keys))
    except (ValueError, OSError, ZeroDivisionError) as exc:
        parser.exit(2, f"invalid audit input: {exc}\n")
    print(json.dumps(result, indent=2))
