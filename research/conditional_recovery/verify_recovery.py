#!/usr/bin/env python3
"""Bounded producer checks; all count tables and recovery bounds are synthetic."""
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import tempfile

from recovery_sensitivity import certified_reference_supremum, recovery_sensitivity_test
import baseline_conditional_homogeneity as baseline_engine
import conditional_homogeneity as common_engine

ROOT = Path(__file__).resolve().parent


def document(contexts, interval=(1, 1), gamma=0):
    return {
        "observation_contract": "shared_biological_curvature_with_differential_recovery",
        "sampling_contract": "independent_baseline_selected_multinomials",
        "recovery_bound_contract": "externally_justified_coverage_interval",
        "differential_tilt_interval": [str(x) for x in interval],
        "bound_noncoverage_probability": str(gamma),
        "alpha": "1/20",
        "contexts": [{"id": f"c{j + 1}", "baseline": list(k), "selected": list(x)}
                     for j, (k, x) in enumerate(contexts)],
    }


def _with_allocation(original, allocation):
    changed = deepcopy(original)
    for row, a in zip(changed["contexts"], allocation):
        n = sum(row["selected"])
        d = row["selected"][0] - row["selected"][2]
        pooled = [k + x for k, x in zip(row["baseline"], row["selected"])]
        selected = [(n - a + d) // 2, a, (n - a - d) // 2]
        row["selected"] = selected
        row["baseline"] = [t - x for t, x in zip(pooled, selected)]
    return changed


def main():
    examples = {
        "two_point": document([((0, 4, 0), (2, 0, 2)), ((2, 0, 2), (1, 2, 1))],
                              (1, Fraction(24, 19))),
        "two_tails": document([((0, 4, 0), (2, 0, 2)), ((2, 0, 2), (0, 4, 0))],
                              (Fraction(1, 4), 4)),
        "previous_baseline": document([((4, 4, 4), (6, 0, 6)), ((4, 4, 4), (0, 12, 0))],
                                      (Fraction(1, 33), 33)),
    }
    results = {name: recovery_sensitivity_test(doc, include_fiber=True)
               for name, doc in examples.items()}
    assert results["two_point"]["reference_p_exact"] == "1/25"
    assert results["two_point"]["robust_p_exact"] == "1/20"
    assert results["two_point"]["reject"]
    assert results["two_tails"]["reference_p_exact"] == "1/289"
    assert results["two_tails"]["robust_p_exact"] == "17/2321"
    assert results["two_tails"]["maximizing_endpoints"] == ["lower", "upper"]
    assert results["previous_baseline"]["reference_p_exact"] == "875/755849"
    assert results["previous_baseline"]["robust_p_exact"] == "9625/189283"
    assert not results["previous_baseline"]["reject"]

    # Exact null thresholds under both point and bounded nuisance laws.
    point_matches = threshold_checks = direct_tail_checks = 0
    for name, original in examples.items():
        fiber = results[name]["fiber"]
        weights = [Fraction(row["reference_weight_exact"]) for row in fiber]
        for observed_index, row in enumerate(fiber):
            doc = _with_allocation(original, row["selected_A"])
            doc["differential_tilt_interval"] = ["1", "1"]
            checked = recovery_sensitivity_test(doc)
            reference = {key: doc[key] for key in ("contexts", "alpha", "sampling_contract")}
            reference["observation_contract"] = "shared_positive_offset_within_context"
            unchanged = baseline_engine.baseline_conditional_test(reference)
            assert checked["robust_p_exact"] == unchanged["p_value"]
            point_matches += 1
            event = [j for j, h in enumerate(weights) if h <= weights[observed_index]]
            for tilt in (Fraction(1, 4), Fraction(1), Fraction(4)):
                doc["differential_tilt_interval"] = [str(tilt), str(tilt)]
                direct = sum(weights[j] * tilt ** j for j in event) / sum(h * tilt ** j for j, h in enumerate(weights))
                assert recovery_sensitivity_test(doc)["robust_p_exact"] == str(direct)
                direct_tail_checks += 1
        for true_t in (Fraction(1, 4), Fraction(1), Fraction(4)):
            mass = [h * true_t ** j for j, h in enumerate(weights)]
            mass = [x / sum(mass) for x in mass]
            for interval in ((true_t, true_t), (Fraction(1, 4), Fraction(4))):
                p_values = []
                for row in fiber:
                    doc = _with_allocation(original, row["selected_A"])
                    doc["differential_tilt_interval"] = list(map(str, interval))
                    p_values.append(Fraction(recovery_sensitivity_test(doc)["adjusted_p_exact"]))
                for threshold in set(p_values):
                    assert sum(p for p, value in zip(mass, p_values) if value <= threshold) <= threshold
                    threshold_checks += 1

    # Inclusive alpha boundary, gamma allocation and asymmetric intervals.
    doc = deepcopy(examples["two_point"])
    doc["differential_tilt_interval"] = ["1", "4/3"]
    assert not recovery_sensitivity_test(doc)["reject"]
    doc["differential_tilt_interval"] = ["1", "1"]
    doc["bound_noncoverage_probability"] = "1/100"
    assert recovery_sensitivity_test(doc)["adjusted_p_exact"] == "1/20"
    assert recovery_sensitivity_test(doc)["reject"]
    doc["bound_noncoverage_probability"] = "1/50"
    assert not recovery_sensitivity_test(doc)["reject"]
    doc["bound_noncoverage_probability"] = "99/100"
    assert recovery_sensitivity_test(doc)["adjusted_p_exact"] == "1"
    doc = deepcopy(examples["previous_baseline"])
    doc["differential_tilt_interval"] = ["1/4", "1/2"]
    assert recovery_sensitivity_test(doc)["robust_p_exact"] == "875/1956323"

    # Context reversal changes the nuisance interval reciprocally.
    reversal_checks = 0
    for original in examples.values():
        reverse = deepcopy(original)
        reverse["contexts"].reverse()
        lo, hi = map(Fraction, original["differential_tilt_interval"])
        reverse["differential_tilt_interval"] = [str(1 / hi), str(1 / lo)]
        assert recovery_sensitivity_test(reverse)["adjusted_p_exact"] == recovery_sensitivity_test(original)["adjusted_p_exact"]
        reversal_checks += 1

    singleton = document([((0, 0, 0), (2, 1, 0)), ((0, 0, 0), (0, 1, 2))],
                         (Fraction(1, 4), 4))
    assert recovery_sensitivity_test(singleton)["information_status"] == "uninformative_singleton_fiber"
    assert recovery_sensitivity_test(singleton)["adjusted_p_exact"] == "1"
    maximum = document([((0, 200, 0), (100, 0, 100)), ((100, 0, 100), (0, 200, 0))],
                       (Fraction(1, 2), 2))
    maximum_result = recovery_sensitivity_test(maximum)
    assert maximum_result["fiber_size"] == 101

    # This generic non-log-concave example has an interior maximum; refusing
    # its disconnected complement is required for a sound endpoint certificate.
    assert Fraction(1, 5) > Fraction(1, 6)
    failures = 0
    def must_refuse(call):
        nonlocal failures
        try:
            call()
        except ValueError:
            failures += 1
        else:
            raise AssertionError("Malformed or unsupported input was accepted")
    must_refuse(lambda: certified_reference_supremum([2, 1, 2], 1, "1/2", 2))
    must_refuse(lambda: certified_reference_supremum([1] * 101, 0, 1, 1 << 255))
    for bad_weights in ([], [0], [True], [Fraction(1)], [1] * 102, [1 << 802]):
        must_refuse(lambda w=bad_weights: certified_reference_supremum(w, 0, 1, 1))
    for bad_index in (True, -1, 2, "0"):
        must_refuse(lambda j=bad_index: certified_reference_supremum([1, 1], j, 1, 1))
    bad_mutations = [
        ("contexts", []), ("contexts", examples["two_point"]["contexts"] * 2),
        ("observation_contract", "shared_positive_offset_within_context"),
        ("sampling_contract", "marginals_only"), ("recovery_bound_contract", "estimated_point"),
        ("bound_noncoverage_probability", "-1/10"), ("bound_noncoverage_probability", 1),
        ("bound_noncoverage_probability", True), ("bound_noncoverage_probability", 0.01),
        ("alpha", 0), ("alpha", 1), ("alpha", "0.05"),
    ]
    for key, value in bad_mutations:
        changed = deepcopy(examples["two_point"])
        changed[key] = value
        must_refuse(lambda d=changed: recovery_sensitivity_test(d))
    for bad_interval in ([0, 1], [2, 1], [1], [1, None], [True, 1], [0.5, 1],
                         ["1/0", 1], ["NaN", 1], [1, 1 << 256]):
        changed = deepcopy(examples["two_point"])
        changed["differential_tilt_interval"] = bad_interval
        must_refuse(lambda d=changed: recovery_sensitivity_test(d))
    for bad_counts in ([True, 0, 0], [-1, 1, 1], [201, 0, 0], [1.0, 0, 0], [1, 1]):
        changed = deepcopy(examples["two_point"])
        changed["contexts"][0]["baseline"] = bad_counts
        must_refuse(lambda d=changed: recovery_sensitivity_test(d))
    changed = deepcopy(examples["two_point"])
    changed["contexts"][1]["id"] = changed["contexts"][0]["id"]
    must_refuse(lambda: recovery_sensitivity_test(changed))
    with tempfile.TemporaryDirectory(dir=ROOT) as temp:
        for j, raw in enumerate(('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}')):
            path = Path(temp) / f"bad_{j}.json"
            path.write_text(raw)
            must_refuse(lambda p=path: common_engine.load_input(p))

    for name, doc in examples.items():
        (ROOT / f"example_{name}.json").write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
        (ROOT / f"example_{name}_result.json").write_text(json.dumps(results[name], indent=2, sort_keys=True) + "\n")
    sources = [ROOT / "recovery_sensitivity.py", ROOT / "verify_recovery.py", ROOT / "README.md",
               Path(baseline_engine.__file__), Path(common_engine.__file__)]
    receipt = {
        "status": "passed", "scope": "synthetic producer checks; not external peer review",
        "point_interval_matches_unchanged_engine": point_matches,
        "direct_rational_tail_comparisons": direct_tail_checks,
        "complete_attainable_conditional_threshold_checks": threshold_checks,
        "context_reversal_checks": reversal_checks,
        "malformed_or_unsupported_input_refusals": failures,
        "maximum_supported_fiber_size_checked": maximum_result["fiber_size"],
        "gamma_adjustment_and_inclusive_boundary_checked": True,
        "source_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sources},
    }
    (ROOT / "VERIFICATION.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
