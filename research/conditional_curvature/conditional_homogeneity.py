#!/usr/bin/env python3
"""Bounded exact conditional shared-curvature test with known rational offsets.

Original project implementation of standard conditional exponential-family
inference. Synthetic/design use only; declarations do not authenticate a count
law, known offsets, measurement transfer, or a prospective study.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
import json
from math import factorial, prod
from pathlib import Path
import re

MAX_CONTEXTS = 8
MAX_CONTEXT_N = 200
MAX_TOTAL_N = 800
MAX_CARTESIAN_CANDIDATES = 100_000
MAX_RATIONAL_BITS = 256
MAX_WEIGHT_STORAGE_BITS = 64 * 1024 * 1024
_RATIONAL = re.compile(r"[+-]?[0-9]+(?:/[1-9][0-9]*)?\Z")


def _rational(value, name):
    if type(value) is int or isinstance(value, Fraction):
        result = Fraction(value)
    elif isinstance(value, str) and _RATIONAL.fullmatch(value):
        if len(value) > 160:
            raise ValueError(f"{name}: rational text exceeds bounded domain")
        result = Fraction(value)
    else:
        raise ValueError(f"{name}: use an integer or integer/fraction string; no floats")
    if max(abs(result.numerator).bit_length(), result.denominator.bit_length()) > MAX_RATIONAL_BITS:
        raise ValueError(f"{name}: rational exceeds {MAX_RATIONAL_BITS}-bit domain")
    return result


@dataclass(frozen=True)
class _Context:
    name: str
    counts: tuple[int, int, int]
    q: tuple[Fraction, Fraction, Fraction]

    @property
    def n(self):
        return sum(self.counts)

    @property
    def d(self):
        return self.counts[0] - self.counts[2]

    def support(self):
        # This parity is essential: W=(N-A+D)/2 and M=(N-A-D)/2.
        return range((self.n - self.d) % 2, self.n - abs(self.d) + 1, 2)


def _parse(document):
    expected = {"offset_contract", "sampling_contract", "alpha", "contexts"}
    if not isinstance(document, dict) or set(document) != expected:
        raise ValueError(f"Input must have exactly these keys: {sorted(expected)}")
    if document["offset_contract"] != "fixed_known_positive_rational":
        raise ValueError("Estimated or uncertain offsets are outside the exact known-offset contract")
    if document["sampling_contract"] != "independent_multinomial_given_totals":
        raise ValueError("Requires the joint product multinomial law conditional on the totals")
    alpha = _rational(document["alpha"], "alpha")
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie strictly between zero and one")
    rows = document["contexts"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_CONTEXTS:
        raise ValueError(f"Requires 1..{MAX_CONTEXTS} contexts")
    contexts, seen = [], set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"id", "counts", "q"}:
            raise ValueError("Each context requires exactly id, counts, q")
        name = row["id"]
        if not isinstance(name, str) or not name.strip() or name in seen:
            raise ValueError("Context IDs must be unique nonempty strings")
        seen.add(name)
        counts = row["counts"]
        if not isinstance(counts, list) or len(counts) != 3 or any(type(x) is not int or x < 0 for x in counts):
            raise ValueError("Counts must be three nonnegative integers in W,A,M order")
        if sum(counts) > MAX_CONTEXT_N:
            raise ValueError(f"Per-context N exceeds {MAX_CONTEXT_N}")
        q = row["q"]
        if not isinstance(q, list) or len(q) != 3:
            raise ValueError("q must contain three probabilities in W,A,M order")
        q = tuple(_rational(x, "q") for x in q)
        if min(q) <= 0 or sum(q) != 1:
            raise ValueError("q must be strictly positive and sum exactly to one")
        contexts.append(_Context(name, tuple(counts), q))
    if sum(c.n for c in contexts) > MAX_TOTAL_N:
        raise ValueError(f"Total N exceeds {MAX_TOTAL_N}")
    return tuple(contexts), alpha


def _fiber_weights(contexts):
    """Unnormalized masses with all nuisance terms constant on the fiber."""
    supports = [tuple(c.support()) for c in contexts]
    candidate_count = prod(map(len, supports))
    if candidate_count > MAX_CARTESIAN_CANDIDATES:
        raise ValueError(f"Cartesian support {candidate_count} exceeds {MAX_CARTESIAN_CANDIDATES}; no approximation substituted")
    # Before constructing large rational powers, bound the total retained
    # numerator/denominator bits plus a conservative per-entry bookkeeping
    # allowance. This is a refusal guard, not a complete runtime/memory promise.
    rational_bits = 2 * sum(c.n * max(max(abs(q.numerator).bit_length(), q.denominator.bit_length()) for q in c.q) for c in contexts)
    factorial_bits = sum(factorial(c.n).bit_length() for c in contexts)
    _guard_storage(candidate_count, rational_bits + factorial_bits)
    total_a = sum(c.counts[1] for c in contexts)
    local = []
    for c, support in zip(contexts, supports):
        row = {}
        for a in support:
            w, m = (c.n - a + c.d) // 2, (c.n - a - c.d) // 2
            row[a] = prod(q ** k for q, k in zip(c.q, (w, a, m))) / (factorial(w) * factorial(a) * factorial(m))
        local.append(row)
    weights = {}
    for allocation in product(*supports):
        if sum(allocation) == total_a:
            weights[allocation] = prod(row[a] for row, a in zip(local, allocation))
    # Every admitted count vector is a member of its own nonempty fiber.
    assert weights and tuple(c.counts[1] for c in contexts) in weights
    return weights, candidate_count


def _guard_storage(candidate_count, bits_per_weight):
    estimated_bits = candidate_count * (bits_per_weight + 1024)
    if estimated_bits > MAX_WEIGHT_STORAGE_BITS:
        raise ValueError(f"Bounded weight-storage estimate {estimated_bits} bits exceeds {MAX_WEIGHT_STORAGE_BITS}; result uncomputed")


def _strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError(f"Nonstandard JSON numeric constant: {value}")


def load_input(path):
    return json.loads(path.read_text(), object_pairs_hook=_strict_object, parse_constant=_reject_constant)


def conditional_test(document, *, include_fiber=False):
    """Return an exact inclusive probability-ordering P value.

    Reject iff P <= supplied alpha. Nonrejection is not equality/equivalence.
    One-context and singleton fibers give P=1 and are explicitly uninformative.
    """
    contexts, alpha = _parse(document)
    weights, candidates = _fiber_weights(contexts)
    result = _summarize(contexts, alpha, weights, candidates, include_fiber)
    result.update({
        "scope": "known-offset conditional shared-curvature restriction; no mechanism or forecast superiority claim",
        "offset_contract": document["offset_contract"],
        "sampling_contract": document["sampling_contract"],
    })
    return result


def _summarize(contexts, alpha, weights, candidates, include_fiber):
    """Common exact probability ordering after a mode supplies its fiber law."""
    observed = tuple(c.counts[1] for c in contexts)
    normalizer = sum(weights.values(), Fraction(0))
    threshold = weights[observed]
    p = sum((mass for mass in weights.values() if mass <= threshold), Fraction(0)) / normalizer
    min_mass = min(weights.values())
    minimum_p = sum((mass for mass in weights.values() if mass == min_mass), Fraction(0)) / normalizer
    degenerate = len(weights) == 1
    result = {
        "context_order": [c.name for c in contexts],
        "conditioned_N": [c.n for c in contexts],
        "conditioned_D": [c.d for c in contexts],
        "conditioned_total_A": sum(observed),
        "observed_A_allocation": list(observed),
        "cartesian_candidate_count": candidates,
        "fiber_size": len(weights),
        "singleton_fiber": degenerate,
        "minimum_attainable_p": str(minimum_p),
        "rejection_attainable_at_alpha": minimum_p <= alpha,
        "p_value": str(p),
        "observed_conditional_probability": str(threshold / normalizer),
        "alpha": str(alpha),
        "decision": "uninformative_singleton_fiber" if degenerate else ("reject_shared_curvature" if p <= alpha else "not_rejected"),
    }
    if include_fiber:
        result["fiber"] = [{"A": list(a), "probability": str(mass / normalizer)} for a, mass in weights.items()]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--include-fiber", action="store_true")
    args = parser.parse_args()
    result = conditional_test(load_input(args.input), include_fiber=args.include_fiber)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
