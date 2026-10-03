#!/usr/bin/env python3
"""Independent synthetic exact-arithmetic oracles; no biological observations.

Original internal review implementation; MIT, Ricardo Maldonado, 2026.
This is internal AI-assisted adversarial review, not external peer review.
"""
from copy import deepcopy
from fractions import Fraction as F
import argparse
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ("certified_score.py", "test_certified_score.py", "verify_replay.py", "README.md", "LICENSE", "example_input.json", "example_result.json", "precision_shares.json", "precision_result.json")
SOURCE_SNAPSHOT = {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in SOURCES}
SPEC = importlib.util.spec_from_file_location("reviewed_certified_score", ROOT / "certified_score.py")
SOURCE_AT_IMPORT = hashlib.sha256((ROOT / "certified_score.py").read_bytes()).hexdigest()
cs = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cs)
COUNTS = {}


def checked(label, condition=True):
    if not condition:
        raise AssertionError(label)
    COUNTS[label] = COUNTS.get(label, 0) + 1


def direct_tail(n, k, p, upper):
    # Direct polynomial summation; no integer recurrence/complement optimization.
    indices = range(k, n + 1) if upper else range(k + 1)
    return sum((F(math.comb(n, j)) * p**j * (1-p)**(n-j) for j in indices), F(0))


def independent_log(x, terms=220):
    """Exact -log(1-z) series, distinct from candidate's atanh series.

    On 1<=r<=2, z=1-1/r is in [0,1/2]. After N terms, the positive
    remainder is at most z**(N+1)/((N+1)*(1-z)). Signed powers of two
    are enclosed without calling any candidate logarithm helper.
    """
    exponent, reduced = 0, x
    while reduced >= 2:
        reduced /= 2
        exponent += 1
    while reduced < 1:
        reduced *= 2
        exponent -= 1

    def series(r):
        z = 1 - 1/r
        power, total = z, F(0)
        for j in range(1, terms + 1):
            total += power / j
            power *= z
        return total, total + power / ((terms + 1)*(1-z))

    lo, hi = series(reduced)
    two_lo, two_hi = series(F(2))
    return ((lo + exponent*two_lo, hi + exponent*two_hi) if exponent >= 0
            else (lo + exponent*two_hi, hi + exponent*two_lo))


def explicit_vertices(box):
    vertices = set()
    for free in range(3):
        fixed = [i for i in range(3) if i != free]
        for sides in itertools.product((0, 1), repeat=2):
            point = [F(0)] * 3
            for i, side in zip(fixed, sides):
                point[i] = box[i][side]
            point[free] = 1 - sum(point)
            if all(lo <= x <= hi for x, (lo, hi) in zip(point, box)):
                vertices.add(tuple(point))
    return vertices


def count_vectors(n):
    return ((w, a, n-w-a) for w in range(n+1) for a in range(n-w+1))


def multinomial_mass(k, p):
    n = sum(k)
    coefficient = math.factorial(n)
    denominator = math.prod(math.factorial(v) for v in k)
    return F(coefficient, denominator)*math.prod(pi**ki for pi, ki in zip(p, k))


def tails_and_coverage():
    for n in range(1, 16):
        for k in range(n+1):
            for p in (F(0), F(1), F(1, 97), F(1, 7), F(1, 2), F(6, 7), F(96, 97)):
                for direction in (False, True):
                    checked("direct_binomial_tail_identities",
                            cs.exact_binomial_tail(n, k, p, direction) == direct_tail(n, k, p, direction))
            for tail in (F(1, 96), F(1, 10), F(1, 2)-F(1, 2**32)):
                lo, hi, lower, upper = cs.cp_interval(n, k, tail, 19)
                checked("cp_bracket_support_and_width",
                        0 <= lo <= hi <= 1 and lower[1]-lower[0] <= F(1, 2**19)
                        and upper[1]-upper[0] <= F(1, 2**19))
                if k:
                    checked("cp_increasing_lower_root_polynomial_inequalities",
                            direct_tail(n, k, lower[0], True) <= tail <= direct_tail(n, k, lower[1], True))
                else:
                    checked("cp_exact_support_boundaries", lower == (0, 0))
                if k < n:
                    checked("cp_decreasing_upper_root_polynomial_inequalities",
                            direct_tail(n, k, upper[1], False) <= tail <= direct_tail(n, k, upper[0], False))
                else:
                    checked("cp_exact_support_boundaries", upper == (1, 1))
    for n in range(1, 11):
        for alpha in (F(1, 5), F(1, 20), F(1, 100)):
            intervals = [cs.cp_interval(n, k, alpha/2, 17)[:2] for k in range(n+1)]
            for p in [F(j, 10) for j in range(11)] + [F(1, 97), F(96, 97)]:
                coverage = sum((F(math.comb(n, k))*p**k*(1-p)**(n-k)
                                for k, (lo, hi) in enumerate(intervals) if lo <= p <= hi), F(0))
                checked("exact_small_n_binomial_coverage", coverage >= 1-alpha)


def logarithms():
    rng = random.Random(2026100205)
    arguments = {F(1), F(2), F(1, 2), F(1, 2**127), F(2**127)}
    arguments.update(F(rng.randint(1, 10000), rng.randint(1, 10000)) for _ in range(45))
    arguments.update(F(2**j+1, 2**j-1) for j in (3, 7, 20, 63, 127))
    for argument in sorted(arguments):
        independent_lo, independent_hi = independent_log(argument)
        for terms, bits in ((1, 3), (5, 20), (32, 64), (64, 96)):
            lo, hi = cs.log_enclosure(argument, terms, bits)
            checked("alternative_exact_log_series_containment",
                    lo <= independent_lo <= independent_hi <= hi)
            inv_lo, inv_hi = cs.log_enclosure(1/argument, terms, bits)
            checked("log_reciprocal_signed_containment", lo+inv_lo <= 0 <= hi+inv_hi)
    for bits in (1, 3, 19, 64, 96):
        for j in range(-41, 42):
            value = F(j, 37)
            lo = cs.dyadic_outer(value, bits, True)
            hi = cs.dyadic_outer(value, bits, False)
            checked("signed_outward_rounding", lo <= value <= hi and hi-lo <= F(1, 2**bits))


def projections():
    rng = random.Random(20300205)
    for _ in range(400):
        integers = [rng.randint(1, 20) for _ in range(3)]
        p = tuple(F(v, sum(integers)) for v in integers)
        box = tuple((max(F(0), v-F(rng.randint(0, 9), 20)),
                     min(F(1), v+F(rng.randint(0, 9), 20))) for v in p)
        vertices = explicit_vertices(box)
        checked("nonempty_explicit_vertex_oracles", bool(vertices))
        coefficients = tuple(F(rng.randint(-20, 20), rng.randint(1, 11)) for _ in range(3))
        values = [sum(pi*ai for pi, ai in zip(point, coefficients)) for point in vertices]
        for maximum in (False, True):
            value, point = cs.exact_extreme(box, coefficients, maximum)
            checked("greedy_extrema_vs_explicit_vertices",
                    value == (max(values) if maximum else min(values)) and point in vertices)
        intervals = tuple((a-F(rng.randint(0, 5), 13), a+F(rng.randint(0, 5), 13)) for a in coefficients)
        lo, hi, _, _ = cs.score_projection(box, intervals)
        for point in vertices:
            for sides in itertools.product((0, 1), repeat=3):
                value = sum(point[i]*intervals[i][sides[i]] for i in range(3))
                checked("signed_coefficient_box_vertex_containment", lo <= value <= hi)


def triad_coverage_and_conditional_total():
    alpha, n = F(1, 5), 6
    p = (F(1, 8), F(3, 8), F(1, 2))
    tail = alpha/6
    predicted = (F(1, 4), F(1, 2), F(1, 4))
    comparisons = ((F(1, 3),)*3, (F(2, 5), F(2, 5), F(1, 5)), (F(1, 8), F(3, 8), F(1, 2)))
    coarse = [tuple(cs.log_enclosure(predicted[i]/m[i], 16, 32) for i in range(3)) for m in comparisons]
    truth = [tuple(sum(p[i]*independent_log(predicted[i]/m[i])[side] for i in range(3))
                   for side in (0, 1)) for m in comparisons]
    region_coverage, score_coverage, mass_sum = F(0), F(0), F(0)
    for k in count_vectors(n):
        mass = multinomial_mass(k, p)
        mass_sum += mass
        box = tuple(cs.cp_interval(n, ki, tail, 15)[:2] for ki in k)
        covered = all(lo <= pi <= hi for pi, (lo, hi) in zip(p, box))
        all_scores_covered = True
        for coefficients, (true_lo, true_hi) in zip(coarse, truth):
            lo, hi, _, _ = cs.score_projection(box, coefficients)
            all_scores_covered &= lo <= true_lo <= true_hi <= hi
            if covered:
                checked("all_frozen_comparator_coverage_on_shared_region", lo <= true_lo <= true_hi <= hi)
        if covered:
            region_coverage += mass
        if all_scores_covered:
            score_coverage += mass
    checked("exact_multinomial_shared_region_coverage", mass_sum == 1 and region_coverage >= 1-alpha)
    checked("exact_multinomial_score_coverage", score_coverage >= region_coverage)
    # Four-category IID founder frame; summing over its random qualifying total
    # exactly preserves conditional multinomial and coverage on evaluable totals.
    frame_n, qualification_probability = 8, F(3, 5)
    evaluable_probability, coverage_mass = F(0), F(0)
    for qn in range(1, frame_n+1):
        qmass = F(math.comb(frame_n, qn))*qualification_probability**qn*(1-qualification_probability)**(frame_n-qn)
        conditional_coverage, conditional_mass = F(0), F(0)
        for k in count_vectors(qn):
            mass = multinomial_mass(k, p)
            conditional_mass += mass
            box = tuple(cs.cp_interval(qn, ki, tail, 15)[:2] for ki in k)
            if all(lo <= pi <= hi for pi, (lo, hi) in zip(p, box)):
                conditional_coverage += mass
        checked("qualifying_total_conditional_multinomial_coverage", conditional_mass == 1 and conditional_coverage >= 1-alpha)
        evaluable_probability += qmass
        coverage_mass += qmass*conditional_coverage
    checked("iid_random_qualifying_total_mixture_coverage", coverage_mass >= (1-alpha)*evaluable_probability)


def plan_base(cp_bits=4, log_terms=2, log_bits=10, report_bits=6):
    return {"alpha": "1/5", "cp_bisection_bits": cp_bits, "log_terms": log_terms,
            "log_fraction_bits": log_bits, "report_fraction_bits": report_bits,
            "comparator_names": ["m1", "m2"],
            "contexts": [{"id": "c", "weight": "1", "fixed_total_units": 30,
                          "tmd": ["1/4", "1/2", "1/4"],
                          "comparators": {"m1": ["1/3", "1/3", "1/3"],
                                          "m2": ["1/5", "2/5", "2/5"]}}],
            "gates": {"success_threshold": "0", "failure_mode": "disabled", "failure_threshold": None}}


def precision():
    for cp_bits, terms, log_bits, report_bits in itertools.product((1, 3, 7), (1, 4), (3, 17), (2, 13)):
        plan = plan_base(cp_bits, terms, log_bits, report_bits)
        parsed = cs.validate_plan(plan)
        coefficients = cs.coefficient_table(parsed)["c"]
        for target in (F(1, 2), F(1), F(2)):
            try:
                guide = cs.precision_plan(plan, str(target), {"c": "1"})
            except ValueError:
                checked("too_fine_precision_rejections")
                continue
            n = guide["qualifying_sample_requirements"]["c"]["minimum_qualifying_endpoints"]
            if n > 14:
                checked("valid_guides_outside_exhaustive_small_n_scope")
                continue
            checked("independent_precision_plans")
            for total in (n, n+1, n+3):
                cp = [cs.cp_interval(total, k, parsed["alpha"]/6, cp_bits)[:2] for k in range(total+1)]
                for k in count_vectors(total):
                    box = tuple(cp[ki] for ki in k)
                    vertices = explicit_vertices(box)
                    for intervals in coefficients.values():
                        lo = min(sum(point[i]*intervals[i][0] for i in range(3)) for point in vertices)
                        hi = max(sum(point[i]*intervals[i][1] for i in range(3)) for point in vertices)
                        lo = cs.dyadic_outer(lo, report_bits, True)
                        hi = cs.dyadic_outer(hi, report_bits, False)
                        checked("precision_all_small_count_vectors_vs_vertex_oracle", (hi-lo)/2 <= target)
    # This purely geometric identity explains the triad-specific constant.
    grid = [tuple(F(k, 8) for k in counts) for counts in count_vectors(8)]
    for p, q in itertools.product(grid, repeat=2):
        tv = sum(abs(pi-qi) for pi, qi in zip(p, q))/2
        checked("triad_total_variation_vs_max_coordinate", tv == max(abs(pi-qi) for pi, qi in zip(p, q)))


def weighted_engine():
    # Explicit vertex oracle, independent of candidate's greedy optimizer.
    original = json.loads((ROOT / "example_input.json").read_text())
    for weights in ((F(1), F(0)), (F(1, 2), F(1, 2)), (F(3, 5), F(2, 5)),
                    (F(1, 2**70), 1-F(1, 2**70))):
        for totals in ((2, 3), (3, 1)):
            for k1, k2 in itertools.product(count_vectors(totals[0]), count_vectors(totals[1])):
                document = deepcopy(original)
                for i, row in enumerate(document["plan"]["contexts"]):
                    row["weight"] = str(weights[i])
                    row["fixed_total_units"] = totals[i]
                    document["outcomes"][row["id"]] = {
                        "counts": list((k1, k2)[i]),
                        "excluded_ledger": {key: 0 for key in cs.EXCLUDED}}
                document["expected_plan_sha256"] = cs.plan_sha256(document["plan"])
                result = cs.analyze(document)
                for name in document["plan"]["comparator_names"]:
                    lo, hi = F(0), F(0)
                    for row in result["contexts"]:
                        box = tuple(tuple(map(F, endpoints)) for endpoints in row["probability_box_exact"])
                        coefficients = tuple(tuple(map(F, endpoints)) for endpoints in row["comparisons"][name]["coefficient_enclosures_exact"])
                        vertices = explicit_vertices(box)
                        weight = F(row["weight_exact"])
                        lo += weight*min(sum(p[i]*coefficients[i][0] for i in range(3)) for p in vertices)
                        hi += weight*max(sum(p[i]*coefficients[i][1] for i in range(3)) for p in vertices)
                    bits = document["plan"]["report_fraction_bits"]
                    expected = [str(cs.dyadic_outer(lo, bits, True)), str(cs.dyadic_outer(hi, bits, False))]
                    checked("weighted_full_engine_vs_independent_vertex_oracle",
                            expected == result["weighted_score_intervals_exact"][name])


def thresholds_and_guards():
    for power in (55, 100, 300):
        tiny, gate = F(1, 2**power), F(-7, 9)
        checked("strict_sub_float_threshold_certificates",
                cs.decide([(gate+tiny, gate+2*tiny)], gate, None) == "certified_success_at_declared_score_gate")
        checked("strict_sub_float_threshold_certificates",
                cs.decide([(gate-2*tiny, gate-tiny)], gate, gate) == "certified_failure_at_declared_score_gate")
        checked("equality_is_not_a_certificate",
                cs.decide([(gate, gate+tiny)], gate, gate) == "inconclusive_at_declared_score_gate")
        lo = cs.dyadic_outer(gate+tiny, 5, True)
        hi = cs.dyadic_outer(gate+2*tiny, 5, False)
        checked("coarse_rounding_conservatively_loses_certificate",
                cs.decide([(lo, hi)], gate, None) == "inconclusive_at_declared_score_gate")
    guards = [lambda: cs.rational(True), lambda: cs.rational(float("nan")),
              lambda: cs.rational("1/0"), lambda: cs.rational("1e-20"),
              lambda: cs.rational(str(2**129)), lambda: cs.log_enclosure(F(0)),
              lambda: cs.log_enclosure(F(1, 2**145)),
              lambda: cs.cp_interval(0, 0, F(1, 20), 4),
              lambda: cs.cp_interval(5, True, F(1, 20), 4),
              lambda: cs.cp_interval(501, 2, F(1, 20), 4),
              lambda: cs.cp_interval(5, 2, F(1, 2), 4),
              lambda: cs.cp_interval(5, 2, F(1, 20), 65),
              lambda: cs.score_projection(((F(2, 5), F(1)),)*3, ((F(0), F(0)),)*3),
              lambda: cs.strict_json('{"x":0,"x":1}'),
              lambda: cs.strict_json('{"x":NaN}')]
    for operation in guards:
        try:
            operation()
        except (ValueError, TypeError):
            checked("invalid_input_and_resource_guards")
        else:
            raise AssertionError("Invalid operation was accepted")
    # Cache warming must not allow equal-valued but inadmissible types through.
    cs.log_enclosure(F(1), 5, 20)
    cs.cp_interval(3, 1, F(1, 20), 4)
    for operation in (lambda: cs.log_enclosure(1, 5, 20),
                      lambda: cs.log_enclosure(True, 5, 20),
                      lambda: cs.cp_interval(3, True, F(1, 20), 4),
                      lambda: cs.cp_interval(3, 1.0, F(1, 20), 4)):
        try:
            operation()
        except (ValueError, TypeError):
            checked("warm_cache_type_guard_checks")
        else:
            raise AssertionError("Warm cache bypassed type guard")
    original = json.loads((ROOT / "example_input.json").read_text())
    bad_total = deepcopy(original["plan"])
    bad_total["contexts"][0]["fixed_total_units"] = 501
    bad_work = deepcopy(original["plan"])
    bad_work["cp_bisection_bits"] = 64
    bad_work["contexts"] = [deepcopy(bad_work["contexts"][0]) for _ in range(16)]
    for index, row in enumerate(bad_work["contexts"]):
        row.update(id=f"cap_c{index}", weight="1/16", fixed_total_units=500)
    no_qualifying = deepcopy(original)
    first = no_qualifying["plan"]["contexts"][0]
    no_qualifying["outcomes"][first["id"]] = {
        "counts": [0, 0, 0], "excluded_ledger": {
            "Other": first["fixed_total_units"], "no_qualified_outcome": 0,
            "unresolved_classification": 0, "missing": 0}}
    for operation in (lambda: cs.validate_plan(bad_total),
                      lambda: cs.validate_plan(bad_work),
                      lambda: cs.analyze(no_qualifying)):
        try:
            operation()
        except ValueError:
            checked("full_frame_caps_and_zero_qualifying_no_certificate")
        else:
            raise AssertionError("Invalid or unevaluable full frame accepted")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group()
    operation.add_argument("--check", action="store_true", help="Compare receipt without modifying it")
    operation.add_argument("--write-receipt", action="store_true", help="Write executed original receipt")
    args = parser.parse_args()
    tails_and_coverage()
    logarithms()
    projections()
    triad_coverage_and_conditional_total()
    precision()
    weighted_engine()
    thresholds_and_guards()
    checked("source_unchanged_during_review_run", SOURCE_AT_IMPORT == hashlib.sha256((ROOT / "certified_score.py").read_bytes()).hexdigest())
    final_snapshot = {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in SOURCES}
    checked("all_reviewed_source_files_unchanged_during_run", final_snapshot == SOURCE_SNAPSHOT)
    receipt = {"status": "pass", "review_type": "independent_internal_adversarial_exact_arithmetic",
               "provenance": "synthetic", "external_peer_review": False,
               "checks": COUNTS, "total_assertions": sum(COUNTS.values()),
               "source_sha256": final_snapshot,
               "review_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "review_notes_sha256": hashlib.sha256((Path(__file__).parent/"REVIEW_NOTES.md").read_bytes()).hexdigest(),
               "claim_limits": ["Finite oracle checks supplement the written proof, not general biological validation.",
                                "Alternative exact log bounds use -log(1-z) series; no Decimal/float oracle enters a certificate.",
                                "Precision exhaustive checks cover the enumerated small counts and frozen finite-precision plans; general guarantee depends on the written triad-specific proof.",
                                "IID random-qualifying-total mixture check does not validate any actual assay's count law."]}
    receipt_path = Path(__file__).parent / "INDEPENDENT_REVIEW_RECEIPT.json"
    if args.check:
        checked_receipt = json.loads(receipt_path.read_text())
        if checked_receipt != receipt:
            raise AssertionError("Stored independent receipt differs from executed review")
    elif args.write_receipt:
        receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"status": receipt["status"], "total_assertions": receipt["total_assertions"], "checks": COUNTS}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
