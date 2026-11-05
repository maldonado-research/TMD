#!/usr/bin/env python3
"""Finite design diagnostics for the established conditional curvature test.

Standard-library, exact rational arithmetic. Synthetic laws, not biological
power or a chosen study allocation. No source-author code is executed.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
from itertools import product
import json
from math import factorial, lcm, prod
from pathlib import Path

MAX_BUDGET = 12
MAX_JOINT_TABLES = 1_000_000
ALPHA = Fraction(1, 20)


def rational_record(x):
    x = Fraction(x)
    return {"exact": str(x), "approx": float(x)}


def _strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError(f"nonstandard JSON constant: {value}")


def count_vectors(n):
    return [(w, a, n-w-a) for w in range(n+1) for a in range(n-w+1)]


def _count_rows(rows, name):
    if not isinstance(rows, (list, tuple)) or not 1 <= len(rows) <= 8:
        raise ValueError(f"{name}: requires 1..8 contexts")
    result = []
    for row in rows:
        if not isinstance(row, (list, tuple)) or len(row) != 3:
            raise ValueError(f"{name}: each row requires W,A,M")
        if any(type(x) is not int or x < 0 for x in row) or sum(row) > 200:
            raise ValueError(f"{name}: nonnegative integer counts, total <=200")
        result.append(tuple(row))
    return tuple(result)


def support_geometry(baseline, selected):
    """Exact geometry, independent of alpha or a stipulated probability law.

    X'_c=X_c+(-k_c,2k_c,-k_c), K'_c=K_c+(k_c,-2k_c,k_c).
    Feasible k lie in [-L_c,U_c] and sum to zero.
    """
    baseline = _count_rows(baseline, "baseline")
    selected = _count_rows(selected, "selected")
    if len(baseline) != len(selected):
        raise ValueError("baseline and selected context counts must agree")
    if sum(map(sum, baseline+selected)) > 800:
        raise ValueError("combined total exceeds 800")
    lower = [min(k[0], k[2], x[1]//2) for k, x in zip(baseline, selected)]
    upper = [min(x[0], x[2], k[1]//2) for k, x in zip(baseline, selected)]
    widths = [lo+up for lo, up in zip(lower, upper)]
    active = [c for c, width in enumerate(widths) if width > 0]
    s = sum(lower)
    nonsingleton = len(active) >= 2 and 0 < s < sum(widths)
    # Coefficients of product (1+z+...+z^width), evaluated at z^s.
    coefficient = [1]
    for width in widths:
        nxt = [0]*(min(s, len(coefficient)-1+width)+1)
        for j, value in enumerate(coefficient):
            for step in range(min(width, s-j)+1):
                nxt[j+step] += value
        coefficient = nxt
    size = coefficient[s]
    assert nonsingleton == (size > 1)
    return {
        "lower_move_capacities": lower,
        "upper_move_capacities": upper,
        "active_context_indices": active,
        "fiber_size": size,
        "singleton_fiber": not nonsingleton,
        "conditional_covariance_rank": len(active)-1 if nonsingleton else 0,
        "identifiable_contrasts": "contrasts varying among active contexts" if nonsingleton else "none",
    }


def _integer_law(n, probabilities):
    if len(probabilities) != 3 or any(type(p) is not Fraction for p in probabilities):
        raise ValueError("probabilities must be three exact Fractions")
    if min(probabilities) <= 0 or sum(probabilities) != 1:
        raise ValueError("probabilities must be positive and sum to one")
    denominator = lcm(*(p.denominator for p in probabilities))
    numerators = [p.numerator*(denominator//p.denominator) for p in probabilities]
    rows = {}
    for counts in count_vectors(n):
        coefficient = factorial(n)//prod(factorial(v) for v in counts)
        rows[counts] = coefficient*prod(v**k for v, k in zip(numerators, counts))
    assert sum(rows.values()) == denominator**n
    return rows, denominator**n


def _selected_law(tau):
    if type(tau) is not Fraction or tau <= 0:
        raise ValueError("exp(theta) must be a positive Fraction")
    return (1/(2+tau), tau/(2+tau), 1/(2+tau))


def _summarize_fibers(fibers, denominators, alpha):
    """Rows contain (A2, null integer mass, alternative integer masses...)."""
    totals = [0]*len(denominators)
    singleton = [0]*len(denominators)
    attainable = [0]*len(denominators)
    rejection = [0]*len(denominators)
    conditional_variance_numerators = defaultdict(int)
    size_counts = defaultdict(int)
    for rows in fibers.values():
        size_counts[len(rows)] += 1
        null_total = sum(r[1] for r in rows)
        null_buckets = defaultdict(int)
        for row in rows:
            null_buckets[row[1]] += row[1]
        tail = 0
        rejecting_weights = set()
        for weight in sorted(null_buckets):
            tail += null_buckets[weight]
            if tail*alpha.denominator <= null_total*alpha.numerator:
                rejecting_weights.add(weight)
        for row in rows:
            for j, mass in enumerate(row[1:]):
                totals[j] += mass
                if len(rows) == 1:
                    singleton[j] += mass
                if rejecting_weights:
                    attainable[j] += mass
                if row[1] in rejecting_weights:
                    rejection[j] += mass
        s1 = sum(row[0]*row[1] for row in rows)
        s2 = sum(row[0]**2*row[1] for row in rows)
        # E Var(A2|F): sum_F [s2 - s1^2/null_total] / null denominator.
        # Group denominators before rational addition to reduce arithmetic.
        if s2*null_total != s1*s1:
            conditional_variance_numerators[null_total] += s2*null_total-s1*s1
    assert totals == denominators
    info = sum((Fraction(num, den) for den, num in conditional_variance_numerators.items()), Fraction())/denominators[0]
    rows = []
    for j, den in enumerate(denominators):
        assert 0 <= rejection[j] <= attainable[j] <= den-singleton[j] <= den
        rows.append({
            "probability_singleton": rational_record(Fraction(singleton[j], den)),
            "probability_rejection_attainable_fiber": rational_record(Fraction(attainable[j], den)),
            "unconditional_rejection_probability": rational_record(Fraction(rejection[j], den)),
        })
    assert Fraction(rejection[0], denominators[0]) <= alpha
    return {
        "fiber_count": len(fibers),
        "fiber_size_histogram": dict(sorted(size_counts.items())),
        "expected_null_conditional_information_for_theta_difference": rational_record(info),
        "laws": rows,
    }


def _build_selected(n, taus):
    laws = [_integer_law(n, _selected_law(t)) for t in taus]
    return laws


def exact_design(b, n, taus=(Fraction(1), Fraction(3, 2), Fraction(4)), alpha=ALPHA):
    """Two independent contexts, uniform baselines, theta1=eta1=eta2=0.

    theta2 varies over the declared taus. First tau must be one for the null
    probability-ordering law. Complete raw table enumeration, no simulation.
    """
    if type(b) is not int or type(n) is not int or min(b, n) < 0 or b+n > MAX_BUDGET:
        raise ValueError(f"nonnegative integer B,N with B+N<={MAX_BUDGET} required")
    if not isinstance(taus, (list, tuple)) or not 1 <= len(taus) <= 4 or taus[0] != Fraction(1):
        raise ValueError("requires 1..4 tau laws with the first equal to one")
    if any(type(t) is not Fraction or t <= 0 or max(t.numerator.bit_length(), t.denominator.bit_length()) > 32 for t in taus):
        raise ValueError("tau must be a positive <=32-bit Fraction")
    if type(alpha) is not Fraction or not 0 < alpha < 1 or max(alpha.numerator.bit_length(), alpha.denominator.bit_length()) > 256:
        raise ValueError("alpha must be a <=256-bit Fraction strictly between zero and one")
    table_count = (len(count_vectors(b))*len(count_vectors(n)))**2
    if table_count > MAX_JOINT_TABLES:
        raise ValueError("joint table bound exceeded; no approximation substituted")
    q = (Fraction(1, 3),)*3
    baseline, bden = _integer_law(b, q)
    slaws = _build_selected(n, taus)
    nullselected, sden = slaws[0]
    denominators = [bden*bden*sden*den for law, den in slaws]
    local = []
    for k, x in product(baseline, nullselected):
        pooled = tuple(a+c for a, c in zip(k, x))
        d = x[0]-x[2]
        masses = [baseline[k]*law[x] for law, den in slaws]
        local.append((pooled, d, x[1], masses))
    fibers = defaultdict(list)
    for left, right in product(local, repeat=2):
        key = (left[0], left[1], right[0], right[1], left[2]+right[2])
        masses = [left[3][0]*m for m in right[3]]
        fibers[key].append((right[2], *masses))
    summary = _summarize_fibers(fibers, denominators, alpha)
    known_fibers = defaultdict(list)
    known_denominators = [sden*den for law, den in slaws]
    for x, y in product(nullselected, repeat=2):
        key = (x[0]-x[2], y[0]-y[2], x[1]+y[1])
        known_fibers[key].append((y[1], *(nullselected[x]*law[y] for law, den in slaws)))
    known = _summarize_fibers(known_fibers, known_denominators, alpha)
    information = Fraction(summary["expected_null_conditional_information_for_theta_difference"]["exact"])
    known_information = Fraction(known["expected_null_conditional_information_for_theta_difference"]["exact"])
    assert information <= known_information
    return {
        "baseline_per_context": b, "selected_per_context": n,
        "complete_joint_tables": table_count,
        "baseline_conditioned": summary,
        "known_offset_same_selected_N": known,
        "null_information_retained_relative_to_known_offset": rational_record(information/known_information) if known_information else None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--budget", type=int, default=8)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--geometry", type=Path, help="JSON object with baseline and selected arrays, in context order")
    args = parser.parse_args()
    if args.geometry:
        document = json.loads(args.geometry.read_text(), object_pairs_hook=_strict_object, parse_constant=_reject_constant)
        if not isinstance(document, dict) or set(document) != {"baseline", "selected"}:
            raise ValueError("geometry JSON requires exactly baseline and selected")
        result = support_geometry(**document)
    else:
        if not 0 <= args.budget <= MAX_BUDGET:
            raise ValueError(f"budget must be 0..{MAX_BUDGET}")
        taus = (Fraction(1), Fraction(3, 2), Fraction(4))
        result = {
            "scope": "exact synthetic design calculations; no biological power or study recommendation",
            "calculation": "complete joint multinomial enumeration with integer masses and rational summaries",
            "alpha": str(ALPHA), "contexts": 2,
            "per_context_total_budget": args.budget,
            "q_each_context": ["1/3"]*3,
            "exp_theta1": "1", "exp_eta_each_context": "1",
            "laws_in_order": [{"exp_theta2": str(t), "selected_context2": list(map(str, _selected_law(t)))} for t in taus],
            "splits": [exact_design(b, args.budget-b, taus) for b in range(args.budget+1)],
        }
    encoded = json.dumps(result, indent=2, sort_keys=True)+"\n"
    if args.output:
        args.output.write_text(encoded)
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
