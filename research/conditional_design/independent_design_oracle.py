#!/usr/bin/env python3
"""Independent finite-design cross-check; standard library and synthetic laws.

Computes conditional weights from binomial coefficients, rather than grouping
raw null table masses as in the producer. Reads the producer only for comparison.
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import product
from math import comb, factorial
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent


def triads(n):
    return [(w, a, n-w-a) for w in range(n+1) for a in range(n-w+1)]


def coefficient(v):
    return factorial(sum(v)) // (factorial(v[0])*factorial(v[1])*factorial(v[2]))


def local_choices(k, x):
    t = tuple(a+b for a, b in zip(k, x))
    n, d = sum(x), x[0]-x[2]
    out = []
    for y in triads(n):
        if y[0]-y[2] == d and all(a <= b for a, b in zip(y, t)):
            out.append((y[1], comb(t[0], y[0])*comb(t[1], y[1])*comb(t[2], y[2])))
    return tuple(out)


def affine_rank(points):
    if len(points) < 2:
        return 0
    matrix = [[Q(b-a) for a, b in zip(points[0], p)] for p in points[1:]]
    rank = 0
    for j in range(len(points[0])):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][j]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        scale = matrix[rank][j]
        matrix[rank] = [x/scale for x in matrix[rank]]
        for i in range(rank+1, len(matrix)):
            scale = matrix[i][j]
            matrix[i] = [x-scale*y for x, y in zip(matrix[i], matrix[rank])]
        rank += 1
    return rank


def geometry_checks(producer):
    patterns = {}
    cases = [v for n in range(6) for v in triads(n)]
    for k, x in product(cases, repeat=2):
        choices = sorted(a for a, w in local_choices(k, x))
        lo = min(k[0], k[2], x[1]//2)
        hi = min(x[0], x[2], k[1]//2)
        assert choices == list(range(x[1]-2*lo, x[1]+2*hi+1, 2))
        patterns[(lo, hi)] = (k, x)
    checks = 0
    for c in range(1, 5):
        for keys in product(patterns, repeat=c):
            k, x = zip(*(patterns[key] for key in keys))
            points = [z for z in product(*(range(-lo, hi+1) for lo, hi in keys)) if sum(z) == 0]
            actual = producer.support_geometry(k, x)
            assert actual['fiber_size'] == len(points)
            assert actual['conditional_covariance_rank'] == affine_rank(points)
            movable = any(keys[i][1] > 0 and keys[j][0] > 0 for i in range(c) for j in range(c) if i != j)
            assert movable == (len(points) > 1)
            checks += 1
    return {'local_table_checks': len(cases)**2, 'distinct_capacity_patterns': len(patterns), 'global_size_and_rank_checks': checks}


def independent_design(b, n):
    taus = [Q(1), Q(3, 2), Q(4)]
    selected_bases = [(t.denominator, t.numerator, t.denominator) for t in taus]
    denominators = [3**(2*b+n)*sum(v)**n for v in selected_bases]
    totals = [0]*3
    singles = [0]*3
    attainable = [0]*3
    reject = [0]*3
    cells = []
    for k, x in product(triads(b), triads(n)):
        raw = coefficient(k)*coefficient(x)
        masses = [raw*v[0]**x[0]*v[1]**x[1]*v[2]**x[2] for v in selected_bases]
        cells.append((k, x, local_choices(k, x), masses))
    cached = {}
    fiber_null_mass = Counter()
    for left, right in product(cells, repeat=2):
        k, x, ls, lm = left
        kk, xx, rs, rm = right
        key = (tuple(a+b for a, b in zip(k, x)), x[0]-x[2], tuple(a+b for a, b in zip(kk, xx)), xx[0]-xx[2], x[1]+xx[1])
        if key not in cached:
            fiber = {aa: w*ww for a, w in ls for aa, ww in rs if a+aa == key[-1]}
            z = sum(fiber.values())
            pvalues = {a: Q(sum(v for v in fiber.values() if v <= w), z) for a, w in fiber.items()}
            mean = Q(sum(a*w for a, w in fiber.items()), z)
            variance = Q(sum(a*a*w for a, w in fiber.items()), z)-mean*mean
            cached[key] = (pvalues, variance)
        ps, variance = cached[key]
        for j in range(3):
            mass = lm[0]*rm[j]
            totals[j] += mass
            singles[j] += mass*(len(ps) == 1)
            attainable[j] += mass*(min(ps.values()) <= Q(1, 20))
            reject[j] += mass*(ps[xx[1]] <= Q(1, 20))
        fiber_null_mass[key] += lm[0]*rm[0]
    assert totals == denominators
    information = sum((mass*cached[key][1] for key, mass in fiber_null_mass.items()), Q()) / denominators[0]
    return {'fiber_count': len(cached), 'histogram': Counter(len(p[0]) for p in cached.values()), 'information': information, 'laws': [(Q(s, d), Q(a, d), Q(r, d)) for s, a, r, d in zip(singles, attainable, reject, denominators)]}


def main():
    if not __debug__:
        raise SystemExit('Run without -O or -OO; this oracle requires assertions.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=HERE, help='Directory containing producer code and DESIGN_BUDGET_8.json; defaults to this script directory')
    args = parser.parse_args()
    package = args.package.resolve()
    source = package / 'design_diagnostics.py'
    spec = importlib.util.spec_from_file_location('producer', source)
    producer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(producer)
    geometry = geometry_checks(producer)
    expected_path = package / 'DESIGN_BUDGET_8.json'
    expected = json.loads(expected_path.read_text())
    replay = []
    for row in expected['splits']:
        b, n = row['baseline_per_context'], row['selected_per_context']
        actual = independent_design(b, n)
        target = row['baseline_conditioned']
        assert actual['fiber_count'] == target['fiber_count']
        assert actual['histogram'] == {int(k):v for k,v in target['fiber_size_histogram'].items()}
        assert actual['information'] == Q(target['expected_null_conditional_information_for_theta_difference']['exact'])
        for found, law in zip(actual['laws'], target['laws']):
            values = tuple(Q(law[key]['exact']) for key in ('probability_singleton', 'probability_rejection_attainable_fiber', 'unconditional_rejection_probability'))
            assert found == values
        replay.append({'B': b, 'N': n, 'conditional_information': str(actual['information']), 'rejection_probabilities': [str(x[2]) for x in actual['laws']]})
    for row, reversed_row in zip(expected['splits'], reversed(expected['splits'])):
        a, b = row['baseline_conditioned'], reversed_row['baseline_conditioned']
        assert a['laws'][0] == b['laws'][0]
        assert a['expected_null_conditional_information_for_theta_difference'] == b['expected_null_conditional_information_for_theta_difference']
    result = {'scope': 'Independent internal synthetic matched-baseline replay and support geometry checks; known-offset comparison is outside this oracle; no biological data or external peer review', 'geometry': geometry, 'matched_baseline_budget8_splits_independently_reproduced': replay, 'all_null_arm_swap_invariances': True}
    receipt = HERE / 'ORACLE_RECEIPT.json'
    receipt.write_text(json.dumps(result, indent=2)+'\n')
    sources = {'independent_design_oracle.py': Path(__file__).resolve(), 'design_diagnostics.py': source, 'DESIGN_BUDGET_8.json': expected_path, 'ORACLE_RECEIPT.json': receipt}
    hashes = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in sources.items()}
    (HERE / 'ORACLE_HASHES.json').write_text(json.dumps(hashes, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'geometry': geometry, 'design_splits': len(replay), 'status': 'pass'}))


if __name__ == '__main__':
    main()
