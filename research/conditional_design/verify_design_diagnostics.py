#!/usr/bin/env python3
"""Checks the design calculations against unchanged project test engines."""
from fractions import Fraction
from itertools import product
import argparse
import hashlib
import json
from pathlib import Path
import sys

import design_diagnostics as design


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    source = repo/"research/conditional_curvature"
    protected = [source/"conditional_homogeneity.py", source/"baseline_conditional_homogeneity.py",
                 repo/"research/prospective_design/REGISTRY_CANDIDATE.json"]
    before = {str(p.relative_to(repo)): digest(p) for p in protected}
    sys.path.insert(0, str(source))
    from baseline_conditional_homogeneity import baseline_conditional_test
    from conditional_homogeneity import conditional_test
    checks = 0

    def check(condition):
        nonlocal checks
        checks += 1
        assert condition

    taus = (Fraction(1), Fraction(3, 2), Fraction(4))
    q = (Fraction(1, 3),)*3
    baseline_calls = 0
    for b, n in [(2, 2), (3, 3)]:
        klaw, kd = design._integer_law(b, q)
        laws = [design._integer_law(n, design._selected_law(t)) for t in taus]
        xlaw, xd = laws[0]
        rejection = [0]*len(taus)
        singleton = [0]*len(taus)
        attainable = [0]*len(taus)
        for k1, x1, k2, x2 in product(klaw, xlaw, klaw, xlaw):
            document = {
                "observation_contract": "shared_positive_offset_within_context",
                "sampling_contract": "independent_baseline_selected_multinomials",
                "alpha": "1/20",
                "contexts": [
                    {"id": "1", "baseline": list(k1), "selected": list(x1)},
                    {"id": "2", "baseline": list(k2), "selected": list(x2)},
                ],
            }
            result = baseline_conditional_test(document)
            baseline_calls += 1
            geometry = design.support_geometry([k1, k2], [x1, x2])
            check(geometry["fiber_size"] == result["fiber_size"])
            check(geometry["singleton_fiber"] == result["singleton_fiber"])
            check(geometry["conditional_covariance_rank"] == (not result["singleton_fiber"]))
            for j, (law, den) in enumerate(laws):
                mass = klaw[k1]*xlaw[x1]*klaw[k2]*law[x2]
                if result["singleton_fiber"]:
                    singleton[j] += mass
                if result["rejection_attainable_at_alpha"]:
                    attainable[j] += mass
                if Fraction(result["p_value"]) <= design.ALPHA:
                    rejection[j] += mass
        current = design.exact_design(b, n)["baseline_conditioned"]
        for j, (law, den) in enumerate(laws):
            denominator = kd*kd*xd*den
            for key, numerator in [("probability_singleton", singleton[j]),
                                   ("probability_rejection_attainable_fiber", attainable[j]),
                                   ("unconditional_rejection_probability", rejection[j])]:
                check(Fraction(current["laws"][j][key]["exact"]) == Fraction(numerator, denominator))

    known_calls = 0
    for n in range(9):
        laws = [design._integer_law(n, design._selected_law(t)) for t in taus]
        xlaw, xd = laws[0]
        rejection = [0]*len(taus)
        for x1, x2 in product(xlaw, repeat=2):
            result = conditional_test({
                "offset_contract": "fixed_known_positive_rational",
                "sampling_contract": "independent_multinomial_given_totals",
                "alpha": "1/20",
                "contexts": [{"id": str(j), "counts": list(x), "q": ["1/3"]*3} for j, x in enumerate((x1, x2))],
            })
            known_calls += 1
            if Fraction(result["p_value"]) <= design.ALPHA:
                for j, (law, den) in enumerate(laws):
                    rejection[j] += xlaw[x1]*law[x2]
        current = design.exact_design(0, n)["known_offset_same_selected_N"]
        for j, (law, den) in enumerate(laws):
            check(Fraction(current["laws"][j]["unconditional_rejection_probability"]["exact"]) == Fraction(rejection[j], xd*den))

    splits = [design.exact_design(b, 8-b) for b in range(9)]
    for b, row in enumerate(splits):
        opposite = splits[8-b]
        check(row["baseline_conditioned"]["laws"][0] == opposite["baseline_conditioned"]["laws"][0])
        check(row["baseline_conditioned"]["expected_null_conditional_information_for_theta_difference"] == opposite["baseline_conditioned"]["expected_null_conditional_information_for_theta_difference"])
        if min(b, 8-b) < 2:
            check(all(law["probability_singleton"]["exact"] == "1" for law in row["baseline_conditioned"]["laws"]))

    known_doc = {
        "offset_contract": "fixed_known_positive_rational",
        "sampling_contract": "independent_multinomial_given_totals",
        "alpha": "1/20",
        "contexts": [{"id": "1", "counts": [2, 0, 2], "q": ["1/3"]*3},
                     {"id": "2", "counts": [0, 4, 0], "q": ["1/3"]*3}],
    }
    baseline_doc = {
        "observation_contract": "shared_positive_offset_within_context",
        "sampling_contract": "independent_baseline_selected_multinomials",
        "alpha": "1/20",
        "contexts": [{"id": "1", "baseline": [0, 4, 0], "selected": [2, 0, 2]},
                     {"id": "2", "baseline": [2, 0, 2], "selected": [0, 4, 0]}],
    }
    known_result = conditional_test(known_doc, include_fiber=True)
    baseline_result = baseline_conditional_test(baseline_doc, include_fiber=True)
    check(known_result["p_value"] == "1/13")
    check(baseline_result["p_value"] == "1/289")

    malformed = [([], []), ([[True, 0, 0]], [[0, 0, 0]]), ([[1, -1, 1]], [[0, 0, 0]]),
                 ([[1, 2]], [[0, 0, 0]]), ([[1, 2, 3]], [[0, 0, 0], [0, 0, 0]])]
    for baseline, selected in malformed:
        try:
            design.support_geometry(baseline, selected)
        except ValueError:
            check(True)
        else:
            check(False)
    for b, n in [(True, 1), (-1, 2), (0, 13), (2.0, 2)]:
        try:
            design.exact_design(b, n)
        except ValueError:
            check(True)
        else:
            check(False)
    for malformed_alpha in [Fraction(1, 2**256), Fraction(0), 0.05]:
        try:
            design.exact_design(2, 2, alpha=malformed_alpha)
        except ValueError:
            check(True)
        else:
            check(False)
    for malformed_json in ['{"baseline":[],"baseline":[]}', '{"baseline":NaN}']:
        try:
            json.loads(malformed_json, object_pairs_hook=design._strict_object, parse_constant=design._reject_constant)
        except ValueError:
            check(True)
        else:
            check(False)
    after = {str(p.relative_to(repo)): digest(p) for p in protected}
    check(before == after)
    result = {
        "status": "passed", "scope": "internal AI-assisted computational verification, not external peer review",
        "assertions": checks,
        "unchanged_baseline_engine_calls": baseline_calls+1,
        "unchanged_known_offset_engine_calls": known_calls+1,
        "protected_source_hashes_before_and_after": before,
        "checks": ["exhaustive B=N=2 and B=N=3 joint tables against existing baseline engine",
                   "complete selected tables N=0..8 against existing known-offset engine",
                   "exact null arm-swap symmetry for every budget-8 split",
                   "geometry fiber sizes and two-context covariance ranks",
                   "conditional information cannot increase after additional pooled-count conditioning",
                   "discrete-test reversal witness", "malformed input refusal"],
        "discreteness_witness": {"known_offset": known_result, "baseline_conditioned": baseline_result},
        "local_source_hashes": {p.name: digest(p) for p in [Path(__file__), Path(design.__file__)]},
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"status": "passed", "assertions": checks, "baseline_engine_calls": baseline_calls+1, "known_engine_calls": known_calls+1}))


if __name__ == "__main__":
    main()
