#!/usr/bin/env python3
"""Exact shared-curvature test using matched independent baseline counts.

Conditions away an unknown positive context-specific offset using pooled route
counts. The baseline and selected sampling arms must share that offset in their
observed multinomial laws. No recovery adjustment or transfer claim is inferred.
"""
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
import argparse
import json
from math import comb, prod
from pathlib import Path

from conditional_homogeneity import (
    MAX_CONTEXTS, MAX_CONTEXT_N, MAX_TOTAL_N, MAX_CARTESIAN_CANDIDATES,
    _rational, _summarize, _guard_storage, load_input,
)


@dataclass(frozen=True)
class _PairedContext:
    name: str
    baseline: tuple[int, int, int]
    counts: tuple[int, int, int]

    @property
    def n(self):
        return sum(self.counts)

    @property
    def d(self):
        return self.counts[0] - self.counts[2]

    @property
    def pooled(self):
        return tuple(k + x for k, x in zip(self.baseline, self.counts))

    def support(self):
        result = []
        for a in range((self.n - self.d) % 2, self.n - abs(self.d) + 1, 2):
            x = ((self.n - a + self.d) // 2, a, (self.n - a - self.d) // 2)
            if all(value <= total for value, total in zip(x, self.pooled)):
                result.append(a)
        return tuple(result)


def _parse(document):
    expected = {"observation_contract", "sampling_contract", "alpha", "contexts"}
    if not isinstance(document, dict) or set(document) != expected:
        raise ValueError(f"Input must have exactly these keys: {sorted(expected)}")
    if document["observation_contract"] != "shared_positive_offset_within_context":
        raise ValueError("Requires the same positive observed offset in both arms of each context")
    if document["sampling_contract"] != "independent_baseline_selected_multinomials":
        raise ValueError("Requires the joint product multinomial law across all arms and contexts")
    alpha = _rational(document["alpha"], "alpha")
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie strictly between zero and one")
    rows = document["contexts"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_CONTEXTS:
        raise ValueError(f"Requires 1..{MAX_CONTEXTS} contexts")
    contexts, seen = [], set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"id", "baseline", "selected"}:
            raise ValueError("Each context requires exactly id, baseline, selected")
        name = row["id"]
        if not isinstance(name, str) or not name.strip() or name in seen:
            raise ValueError("Context IDs must be unique nonempty strings")
        seen.add(name)
        arms = []
        for arm in ("baseline", "selected"):
            counts = row[arm]
            if not isinstance(counts, list) or len(counts) != 3 or any(type(x) is not int or x < 0 for x in counts):
                raise ValueError(f"{arm}: requires three nonnegative integers in W,A,M order")
            if sum(counts) > MAX_CONTEXT_N:
                raise ValueError(f"Per-arm total exceeds {MAX_CONTEXT_N}")
            arms.append(tuple(counts))
        contexts.append(_PairedContext(name, *arms))
    if sum(c.n + sum(c.baseline) for c in contexts) > MAX_TOTAL_N:
        raise ValueError(f"Total N+M exceeds {MAX_TOTAL_N}")
    return tuple(contexts), alpha


def _fiber_weights(contexts):
    supports = [c.support() for c in contexts]
    candidate_count = prod(map(len, supports))
    if candidate_count > MAX_CARTESIAN_CANDIDATES:
        raise ValueError(f"Cartesian support {candidate_count} exceeds {MAX_CARTESIAN_CANDIDATES}; no approximation substituted")
    # Each product of binomial coefficients is at most 2**sum(pooled totals).
    _guard_storage(candidate_count, 1 + sum(sum(c.pooled) for c in contexts))
    total_a = sum(c.counts[1] for c in contexts)
    local = []
    for c, support in zip(contexts, supports):
        row = {}
        for a in support:
            x = ((c.n - a + c.d) // 2, a, (c.n - a - c.d) // 2)
            row[a] = prod(comb(total, value) for total, value in zip(c.pooled, x))
        local.append(row)
    weights = {}
    for allocation in product(*supports):
        if sum(allocation) == total_a:
            weights[allocation] = Fraction(prod(row[a] for row, a in zip(local, allocation)))
    assert weights and tuple(c.counts[1] for c in contexts) in weights
    return weights, candidate_count


def baseline_conditional_test(document, *, include_fiber=False):
    contexts, alpha = _parse(document)
    weights, candidates = _fiber_weights(contexts)
    result = _summarize(contexts, alpha, weights, candidates, include_fiber)
    result.update({
        "scope": "shared observed-offset conditional curvature restriction; no mechanism or forecast superiority claim",
        "observation_contract": document["observation_contract"],
        "sampling_contract": document["sampling_contract"],
        "conditioned_baseline_M": [sum(c.baseline) for c in contexts],
        "conditioned_pooled_routes": [list(c.pooled) for c in contexts],
    })
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--include-fiber", action="store_true")
    args = parser.parse_args()
    result = baseline_conditional_test(load_input(args.input), include_fiber=args.include_fiber)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
