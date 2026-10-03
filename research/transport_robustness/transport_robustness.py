#!/usr/bin/env python3
"""Exact conditional recovery-transport sensitivity for stored TMD 0.5 intervals.

Only the adapter for historical marginal JSON accepts binary float endpoints.
All interval, residual-bound, intersection and threshold decisions use Fraction.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path
import re

ROUTES = ('W', 'A', 'M')
MAX_CONTEXTS = 64
ASSUMPTIONS = (
    'marginal_count_laws_and_simultaneous_interval_coverage_justified',
    'positive_population_components_for_finite_log_contrast',
    'observable_control_corrected_parameter_distinguished_from_biological_parameter',
    'differential_residual_bounds_cover_actual_recovery_mismatch',
    'bounds_prespecified_independently_of_outcomes_for_confidence_claim',
    'relative_recovery_observation_model_applicable',
)


def rational(value, label='value'):
    """Parse an exact rational; reject floats, bools, decimal and exponent strings."""
    if isinstance(value, bool):
        raise ValueError(f'{label} cannot be boolean')
    if isinstance(value, (int, Fraction)):
        return Fraction(value)
    if not isinstance(value, str) or not re.fullmatch(r'-?[0-9]+(?:/[1-9][0-9]*)?', value):
        raise ValueError(f'{label} must be an integer or integer/fraction string')
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f'{label} must be a finite rational') from exc


def checked_interval(interval):
    if not isinstance(interval, (tuple, list)) or len(interval) != 2:
        raise ValueError('An interval must contain exactly lower and upper endpoints')
    lo = rational(interval[0], 'J lower')
    hi = None if interval[1] is None else rational(interval[1], 'J upper')
    if lo < 0 or (hi is not None and (hi <= 0 or lo > hi)):
        raise ValueError('Require 0 <= lower <= upper with strictly positive upper; structural zero excluded')
    return lo, hi


def parse_interval(row):
    if not isinstance(row, dict) or not {'J_lower_exact', 'J_upper_exact', 'J_upper_infinity'} <= row.keys():
        raise ValueError('Explicit exact J endpoints and infinity marker required')
    hi, marker = row['J_upper_exact'], row['J_upper_infinity']
    if (hi is None and marker != 'positive') or (hi is not None and marker is not None):
        raise ValueError('Upper infinity must use null endpoint and positive marker together')
    return checked_interval((row['J_lower_exact'], hi))


def interval_json(interval):
    lo, hi = checked_interval(interval)
    return {'J_lower_exact': str(lo), 'J_upper_exact': None if hi is None else str(hi),
            'J_upper_infinity': 'positive' if hi is None else None}


def multiplier_bounds(route_bounds):
    """Range of e_A**2/(e_W*e_M) over a positive rectangular residual box."""
    if not isinstance(route_bounds, dict) or set(route_bounds) != set(ROUTES):
        raise ValueError('Residual bounds must contain exactly W, A, M')
    parsed = {}
    for route in ROUTES:
        row = route_bounds[route]
        if not isinstance(row, dict) or set(row) != {'lower', 'upper'}:
            raise ValueError(f'{route} requires exactly lower and upper bounds')
        lo, hi = rational(row['lower'], route + ' lower'), rational(row['upper'], route + ' upper')
        if not 0 < lo <= hi:
            raise ValueError('Residual bounds must be finite, positive and ordered')
        parsed[route] = lo, hi
    W, A, M = (parsed[route] for route in ROUTES)
    return A[0] ** 2 / (W[1] * M[1]), A[1] ** 2 / (W[0] * M[0])


def widen_interval(interval, route_bounds):
    """Project Jbio=Jcorrected/multiplier; arbitrary boxes can shift an interval."""
    lo, hi = checked_interval(interval)
    mlo, mhi = multiplier_bounds(route_bounds)
    return lo / mhi, None if hi is None else hi / mlo


def symmetric_bounds(R):
    radius = rational(R, 'R')
    if radius < 1:
        raise ValueError('Symmetric differential residual factor R must be at least 1')
    return {route: {'lower': str(1 / radius), 'upper': str(radius)} for route in ROUTES}


def intersection(intervals):
    if not isinstance(intervals, (tuple, list)) or not 1 <= len(intervals) <= MAX_CONTEXTS:
        raise ValueError(f'One to {MAX_CONTEXTS} intervals required')
    parsed = [checked_interval(value) for value in intervals]
    lower = max(lo for lo, _ in parsed)
    finite = [hi for _, hi in parsed if hi is not None]
    upper = min(finite) if finite else None
    empty = upper is not None and lower > upper
    status = ('descriptive_only' if len(parsed) == 1 else 'reject' if empty else
              'compatible_unbounded' if lower == 0 or upper is None else 'compatible_finite')
    # For an empty intersection lower > upper is a witness, not an interval.
    return {'empty': empty, 'J_lower_exact': str(lower),
            'J_upper_exact': None if upper is None else str(upper),
            'J_upper_infinity': 'positive' if upper is None else None, 'status': status}


def threshold_bracket(intervals, bits=80):
    """Outward rational enclosure of the smallest common R restoring compatibility.

    This is a sensitivity frontier of the rectangular projection. It does not
    estimate the true recovery residual. At the exact frontier, touching counts
    as compatible. Rational bisection certifies each comparison by eighth powers.
    """
    if isinstance(bits, bool) or not isinstance(bits, int) or not 1 <= bits <= 512:
        raise ValueError('bits must be an integer in 1..512')
    base = intersection(intervals)
    if base['status'] == 'descriptive_only':
        return {'status': 'descriptive_only', 'R_lower_exact': None, 'R_upper_exact': None,
                'power_ratio_exact': None}
    if not base['empty']:
        return {'status': 'already_compatible', 'R_lower_exact': '1', 'R_upper_exact': '1',
                'power_ratio_exact': None}
    Q = rational(base['J_lower_exact']) / rational(base['J_upper_exact'])
    lo, hi = Fraction(1), Fraction(2)
    while hi ** 8 < Q:
        hi *= 2
    if hi ** 8 == Q:
        return {'status': 'exact', 'R_lower_exact': str(hi), 'R_upper_exact': str(hi),
                'power_ratio_exact': str(Q), 'lower_power_le_ratio': True,
                'upper_power_ge_ratio': True, 'absolute_bracket_width_exact': '0'}
    tolerance = Fraction(1, 2 ** bits)
    while hi - lo > tolerance:
        mid = (lo + hi) / 2
        power = mid ** 8
        if power == Q:
            lo = hi = mid
            break
        if power < Q:
            lo = mid
        else:
            hi = mid
    return {'status': 'exact' if lo == hi else 'certified_bracket',
            'R_lower_exact': str(lo), 'R_upper_exact': str(hi), 'power_ratio_exact': str(Q),
            'lower_power_le_ratio': lo ** 8 <= Q, 'upper_power_ge_ratio': hi ** 8 >= Q,
            'lower_strictly_rejects': lo ** 8 < Q,
            'upper_is_compatible': hi ** 8 >= Q,
            'absolute_bracket_width_exact': str(hi - lo)}


def parse_projection(projection):
    if not isinstance(projection, dict) or projection.get('schema_version') != '0.5.0':
        raise ValueError('A stored 0.5.0 probability projection is required')
    contexts = projection.get('contexts')
    if not isinstance(contexts, list) or not 1 <= len(contexts) <= MAX_CONTEXTS:
        raise ValueError(f'One to {MAX_CONTEXTS} source contexts required')
    names, intervals = [], []
    for context in contexts:
        if not isinstance(context, dict):
            raise ValueError('Each source context must be an object')
        name = context.get('context')
        if not isinstance(name, str) or not name.strip() or name != name.strip() or name in names:
            raise ValueError('Unique nonempty unpadded context names required')
        names.append(name)
        intervals.append(parse_interval(context))
    alpha = rational(projection.get('nominal_alpha'), 'nominal alpha')
    if not 0 < alpha < 1:
        raise ValueError('Source nominal alpha must lie strictly between zero and one')
    if projection.get('coordinates') != 12 * len(contexts):
        raise ValueError('Source coordinate count must equal 12 per context')
    if rational(projection.get('per_tail_error_exact')) != alpha / (24 * len(contexts)):
        raise ValueError('Source tail error inconsistent with equal Bonferroni allocation')
    if rational(projection.get('simultaneous_coverage_lower_bound_exact')) != 1 - alpha:
        raise ValueError('Source simultaneous coverage inconsistent with nominal alpha')
    return names, intervals, alpha


def validate_stored_marginal_arithmetic(projection):
    """Recompute J bounds from legacy saved binary probability endpoints exactly.

    This checks projection arithmetic, not binomial-tail certification or the
    truth of the source sampling-law declarations. No old raw-count validator is
    invoked, and its exact biological transport assertion is not adopted.
    """
    parse_projection(projection)
    exponents = {'baseline': (1, -2, 1), 'selected': (-1, 2, -1),
                 'baseline_controls': (-1, 2, -1), 'selected_controls': (1, -2, 1)}
    for context in projection['contexts']:
        groups = context.get('marginal_intervals')
        if not isinstance(groups, dict) or set(groups) != set(exponents):
            raise ValueError('Exactly four saved groups of marginal intervals required')
        lower, upper, unbounded = Fraction(1), Fraction(1), False
        for group, powers in exponents.items():
            if not isinstance(groups[group], list) or len(groups[group]) != 3:
                raise ValueError('Saved marginal groups must have W,A,M entries')
            for row, power in zip(groups[group], powers):
                if not isinstance(row, dict) or row.get('status') not in ('certified', 'no_observations'):
                    raise ValueError('Saved source marginal must be certified or explicitly have no observations')
                ends = [row.get('lower'), row.get('upper')]
                if any(isinstance(x, bool) or not isinstance(x, (int, float)) for x in ends):
                    raise ValueError('Legacy marginal endpoint must be finite JSON number')
                try:
                    lo, hi = map(Fraction, ends)
                except (ValueError, OverflowError) as exc:
                    raise ValueError('Legacy marginal endpoints must be finite') from exc
                if not 0 <= lo <= hi <= 1 or hi == 0:
                    raise ValueError('Saved probability interval outside positive-population domain')
                if row['status'] == 'no_observations' and (lo != 0 or hi != 1 or row.get('certificates', []) != []):
                    raise ValueError('No-observation marginal must span [0,1] without endpoint certificates')
                if power > 0:
                    lower *= lo ** power
                    upper *= hi ** power
                else:
                    lower /= hi ** (-power)
                    if lo == 0:
                        unbounded = True
                    else:
                        upper /= lo ** (-power)
        calculated = lower, None if unbounded else upper
        if calculated != parse_interval(context):
            raise ValueError(f'Saved J bounds disagree with marginal arithmetic in {context["context"]}')
    return True


def evaluate(document):
    """Evaluate explicitly declared bounded transport assumptions on stored output."""
    if not isinstance(document, dict) or document.get('schema_version') != 'transport-robustness-1':
        raise ValueError('Require transport-robustness-1 document')
    assumptions = document.get('assumptions')
    if not isinstance(assumptions, dict):
        raise ValueError('Explicit bounded-mismatch assumptions required')
    for key in ASSUMPTIONS:
        if assumptions.get(key) is not True:
            raise ValueError(f'assumptions.{key} must explicitly be true')
    source = document.get('source_projection')
    names, intervals, alpha = parse_projection(source)
    validate_stored_marginal_arithmetic(source)
    residuals = document.get('residual_bounds_by_context')
    if not isinstance(residuals, dict) or set(residuals) != set(names):
        raise ValueError('Residual bounds must match source context names exactly')
    corrected, rows = [], []
    for name, interval in zip(names, intervals):
        mlo, mhi = multiplier_bounds(residuals[name])
        adjusted = widen_interval(interval, residuals[name])
        corrected.append(adjusted)
        rows.append({'context': name, 'observable_J_interval': interval_json(interval),
                     'residual_bounds': {route: {end: str(rational(residuals[name][route][end]))
                                                for end in ('lower', 'upper')} for route in ROUTES},
                     'multiplier_lower_exact': str(mlo), 'multiplier_upper_exact': str(mhi),
                     'biological_J_interval': interval_json(adjusted)})
    shared = intersection(corrected)
    return {'schema_version': 'transport-robustness-1', 'contexts': rows,
            'nominal_alpha_exact': str(alpha),
            'conditional_simultaneous_coverage_lower_bound_exact': str(1 - alpha),
            'shared_biological_J_intersection': shared,
            'status': shared['status'],
            'decision': ('not_evaluable_one_context' if len(rows) == 1 else
                         'reject_shared_finite_theta' if shared['empty'] else
                         'no_shared_finite_theta_departure_established'),
            'assumptions': assumptions,
            'scope': 'Conditional on justified source marginal laws and prespecified valid differential residual bounds; compatibility is not equivalence or biological validation.',
            'source_exact_transport_assertion_adopted': False,
            'source_probability_projection_arithmetic_rechecked': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        result = evaluate(json.loads(args.input.read_text()))
        encoded = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n'
        if args.output:
            args.output.write_text(encoded)
        else:
            print(encoded, end='')
    except (ValueError, TypeError, KeyError, OSError) as exc:
        parser.exit(2, f'Unsupported input: {exc}\n')


if __name__ == '__main__':
    main()
