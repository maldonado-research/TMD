#!/usr/bin/env python3
"""Replay original synthetic tests and receipts; no biological observations."""
from fractions import Fraction as F
import argparse
import hashlib
import io
import itertools
import json
from pathlib import Path
import unittest

import certified_score as cs
import test_certified_score as checks


ROOT = Path(__file__).resolve().parent
SOURCES = ("certified_score.py", "test_certified_score.py", "verify_replay.py", "README.md",
           "LICENSE", "example_input.json", "example_result.json", "precision_shares.json",
           "precision_result.json")


def exact_coverage_receipt():
    """Two synthetic multinomial contexts, one shared region, three comparators."""
    alpha, n = F(1, 5), 6
    tail = alpha / 12
    truths = ((F(1, 10), F(3, 10), F(3, 5)), (F(1, 2), F(1, 3), F(1, 6)))
    forecasts = ((F(1, 4), F(1, 2), F(1, 4)), (F(1, 2), F(3, 10), F(1, 5)))
    comparators = ((F(1, 3),)*3, (F(1, 5), F(1, 2), F(3, 10)), (F(2, 5), F(2, 5), F(1, 5)))
    weights = (F(2, 3), F(1, 3))
    stored, truth_scores = [], [[F(0), F(0)] for _ in comparators]
    for c in range(2):
        coeff = [tuple(cs.log_enclosure(forecasts[c][i]/m[i], 32, 64) for i in range(3)) for m in comparators]
        true_coeff = [tuple(cs.log_enclosure(forecasts[c][i]/m[i], 48, 96) for i in range(3)) for m in comparators]
        for m in range(3):
            for endpoint in range(2):
                truth_scores[m][endpoint] += weights[c] * sum(truths[c][i]*true_coeff[m][i][endpoint] for i in range(3))
        rows = []
        for counts, mass in checks.counts_and_mass(n, truths[c]):
            box = tuple(cs.cp_interval(n, k, tail, 24)[:2] for k in counts)
            covers = all(a <= p <= b for p, (a, b) in zip(truths[c], box))
            intervals = [cs.score_projection(box, a)[:2] for a in coeff]
            rows.append((mass, covers, intervals))
        assert sum(r[0] for r in rows) == 1
        stored.append(rows)
    region_coverage, score_coverage, cases = F(0), F(0), 0
    for row1, row2 in itertools.product(*stored):
        cases += 1
        mass = row1[0]*row2[0]
        covered = row1[1] and row2[1]
        if covered:
            region_coverage += mass
        score_covers = True
        for m in range(3):
            lo = sum(weights[c]*row[2][m][0] for c, row in enumerate((row1, row2)))
            hi = sum(weights[c]*row[2][m][1] for c, row in enumerate((row1, row2)))
            score_covers &= lo <= truth_scores[m][0] <= truth_scores[m][1] <= hi
        assert not covered or score_covers
        if score_covers:
            score_coverage += mass
    assert score_coverage >= region_coverage >= 1-alpha
    return {"contexts": 2, "qualifying_trials_per_context": n,
        "frozen_comparators": 3, "joint_count_vectors_enumerated": cases,
        "alpha_exact": str(alpha), "per_tail_error_exact": str(tail),
        "region_coverage_exact": str(region_coverage),
        "all_comparator_score_coverage_exact": str(score_coverage),
        "nominal_coverage_lower_bound_exact": str(1-alpha),
        "limitations": "A synthetic finite example verifies this construction, not a general power result or biological dataset."}


def verify():
    output = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(checks.CertifiedScoreTests)
    # Load an independent inventory because running a suite consumes its tests.
    ids = sorted(t.id().split(".")[-1] for t in unittest.defaultTestLoader.loadTestsFromTestCase(checks.CertifiedScoreTests))
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise AssertionError(output.getvalue())
    doc = cs.strict_json((ROOT / "example_input.json").read_text())
    regenerated = cs.analyze(doc)
    assert regenerated == cs.strict_json((ROOT / "example_result.json").read_text())
    shares = cs.strict_json((ROOT / "precision_shares.json").read_text())
    precision = cs.precision_plan(doc["plan"], "1/20", shares)
    assert precision == cs.strict_json((ROOT / "precision_result.json").read_text())
    return {"schema_version": 1, "project": "Mutation by Natural Dominance (TMD)",
        "verification_kind": "original_synthetic_exact_rational_score_checks",
        "document_date_pacific": "2026-10-02", "biological_observations": 0,
        "new_external_source_acquisitions": 0, "new_theorem_or_priority_claim": False,
        "registered_experiment": False, "biological_registry_fields_resolved": 0,
        "unit_tests_passed": result.testsRun, "unit_test_names": ids,
        "checks": {"direct_exact_tail_polynomial_cases": 1080,
            "exact_CP_root_bracket_interval_cases": 304,
            "small_n_binomial_coverage_parameter_cases": 60,
            "exact_box_simplex_vs_vertex_cases": 192,
            "signed_log_series_and_independent_Decimal_checks_passed": True,
            "strict_near_threshold_outward_guard_passed": True,
            "full_engine_synthetic_success_failure_inconclusive_checked": True,
            "added_comparator_does_not_change_existing_region_or_bounds": True,
            "frozen_context_weighting_and_full_exclusion_ledger_checked": True,
            "pre_outcome_CP_width_bound_enumerated_on_small_count_vectors": True,
            "malformed_nonfinite_duplicate_count_and_resource_guards_passed": True},
        "exact_finite_coverage": exact_coverage_receipt(),
        "example_analysis_decision": regenerated["decision"],
        "example_frozen_plan_sha256": doc["expected_plan_sha256"],
        "stored_example_and_precision_results_replayed": True,
        "source_sha256": {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in SOURCES},
        "claim_limits": "Certified arithmetic candidate for realized rational frozen forecasts under externally justified assumptions. Synthetic verification supplies no biological validation, effect, power, causal mechanism or external peer review."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    result = verify()
    receipt = ROOT / "VERIFICATION_RECEIPT.json"
    if args.check:
        if cs.strict_json(receipt.read_text()) != result:
            raise SystemExit("Stored verification receipt differs from executed replay")
        print(f"PASS: {result['unit_tests_passed']} synthetic tests, exact coverage enumeration and stored score/precision replays")
    elif args.write_receipt:
        receipt.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
        print("Wrote executed synthetic verification receipt")
    else:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
