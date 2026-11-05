#!/usr/bin/env python3
"""Independent exact finite-binomial audit for eligibility-gate allocations."""
import sys
sys.dont_write_bytecode = True

import argparse
from fractions import Fraction as F
from importlib.util import spec_from_file_location, module_from_spec
from math import comb
from pathlib import Path
import hashlib
import json

ENGINE_SHA256 = '66996adfd4f90bccf7315a82022d6b96d390378f4be781f992e7229058bfb368'
CP_SHA256 = '23feb7547d481fc4d361b25da28fe9d46d79be2f9fe66376f9c9ca85c069c79d'


def default_repository():
    """Find the enclosing installed repository, if any."""
    for parent in Path(__file__).resolve().parents:
        if (parent / 'research/classification_bounds/classification_bounds.py').is_file():
            return parent
    return None


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repository', type=Path, default=default_repository(),
                    help='TMD repository root; default: enclosing repository, when available')
parser.add_argument('--output', type=Path, help='Write JSON receipt to this file; default: stdout')
args = parser.parse_args()
if args.repository is None:
    parser.error('--repository required outside a TMD checkout')
ROOT = args.repository.resolve() / 'research/classification_bounds'
for source, expected in ((ROOT / 'classification_bounds.py', ENGINE_SHA256),
                         (ROOT / 'sources/boundary_confidence.py', CP_SHA256)):
    actual = hashlib.sha256(source.read_bytes()).hexdigest()
    if actual != expected:
        parser.error(f'Pinned source hash mismatch: {source}')

spec = spec_from_file_location('classification_engine', ROOT / 'classification_bounds.py')
engine = module_from_spec(spec)
spec.loader.exec_module(engine)
cp = engine.load_cp()
tail = F(1, 320)  # alpha=1/20, C=1, 16 one-sided endpoints.

checks = 0
endpoint_checks = 0
max_lower_error = max_upper_error = F(0)
for n in range(13):
    limits = []
    for k in range(n + 1):
        lo, _ = engine.certified_one_sided(cp, k, n, tail, lower=True)
        hi, _ = engine.certified_one_sided(cp, k, n, tail, lower=False)
        assert F(0) <= lo <= hi <= F(1)
        # Check the output against an independent exact rational binomial sum,
        # bypassing the source implementation's recurrence and root proposal.
        if n and k:
            upper_tail = sum(F(comb(n, j)) * lo**j * (1-lo)**(n-j)
                             for j in range(k, n+1))
            assert upper_tail <= tail
        if n and k < n:
            lower_tail = sum(F(comb(n, j)) * hi**j * (1-hi)**(n-j)
                             for j in range(k+1))
            assert lower_tail <= tail
        limits.append((lo, hi))
        endpoint_checks += 2
    for j in range(41):
        p = F(j, 40)
        lower_error = sum(F(comb(n, k)) * p**k * (1-p)**(n-k)
                          for k, (lo, hi) in enumerate(limits) if lo > p)
        upper_error = sum(F(comb(n, k)) * p**k * (1-p)**(n-k)
                          for k, (lo, hi) in enumerate(limits) if hi < p)
        assert lower_error <= tail and upper_error <= tail
        max_lower_error = max(max_lower_error, lower_error)
        max_upper_error = max(max_upper_error, upper_error)
        checks += 2

# Dependence check: one Bernoulli observation is simultaneously the gate
# indicator and observed W indicator. Its two CP bounds are complements in
# direction and are checked on the same two outcomes, not independent samples.
dependent_cases = 0
for n in range(1, 13):
    bounds = [(engine.certified_one_sided(cp, k, n, tail, lower=True)[0],
               engine.certified_one_sided(cp, k, n, tail, lower=False)[0])
              for k in range(n+1)]
    for j in range(41):
        p = F(j, 40)
        failure = sum(F(comb(n, k)) * p**k * (1-p)**(n-k)
                      for k, (lo, hi) in enumerate(bounds) if lo > p or hi < p)
        assert failure <= 2*tail
        dependent_cases += 1

g_lower, _ = engine.certified_one_sided(cp, 1, 1, tail, lower=True)
f_upper, _ = engine.certified_one_sided(cp, 0, 1, tail, lower=False)
beta = max(F(0), (g_lower-f_upper)/(1-f_upper)) if f_upper < 1 else F(0)
assert beta == 0

receipt = {
    'status': 'passed',
    'endpoint_tail_checks': endpoint_checks,
    'one_sided_coverage_checks': checks,
    'same_unit_gate_label_dependent_cases': dependent_cases,
    'tail_error_exact': str(tail),
    'max_grid_lower_noncoverage_exact': str(max_lower_error),
    'max_grid_upper_noncoverage_exact': str(max_upper_error),
    'plugin_counterexample': {
        'T': '1/2', 'a': '1', 'f': '1/2', 'g': '3/4',
        'native_gate_counts': [1, 1], 'known_other_false_gate_counts': [0, 1],
        'event_probability_exact': '3/8', 'plugin_beta': '1',
        'certified_beta': str(beta),
    },
    'preserved_CP_sha256': CP_SHA256,
    'classification_engine_sha256': ENGINE_SHA256,
}
rendered = json.dumps(receipt, indent=2, sort_keys=True) + '\n'
if args.output:
    args.output.write_text(rendered)
else:
    print(rendered, end='')
