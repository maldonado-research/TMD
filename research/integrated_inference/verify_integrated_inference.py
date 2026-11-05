#!/usr/bin/env python3
"""Bounded synthetic checks of integrated allocation, endpoints and projection."""
from copy import deepcopy
from fractions import Fraction as F
import argparse
import hashlib
import json
from pathlib import Path
from unittest.mock import patch

import integrated_inference as integration

ROOT = Path(__file__).resolve().parent


def fixtures(threshold):
    contract = dict(integration.CONTRACT, endpoint_unit="one synthetic independent full-cohort unit",
                    true_route_control_unit="one synthetic independent known-route introduction",
                    conditional_sampling_justification="All synthetic future units and route controls are independent of all training/calibration; fixed frozen pipelines give binomial marginals.")
    cal_contract = dict(threshold.CONTRACT, control_unit="one synthetic independently known-Other unit",
                        control_population="one synthetic iid control population in this arm/context",
                        score_definition="fixed synthetic scalar score; independently trained before every calibration sample")
    plan = {"schema_version": "integrated-plan-1", "alpha": "1/20", "calibration_error_share": "1/8", "contract": contract, "contexts": []}
    records = {"schema_version": "integrated-observations-1", "provenance": "synthetic", "plan_sha256": "", "contexts": []}
    for context, selected in (("A_rich", (90, 720, 90, 100)), ("A_poor", (405, 90, 405, 100))):
        prow, rrow = {"id": context}, {"id": context}
        for arm in ("baseline", "selected"):
            pipeline = "synthetic-" + context + "-" + arm
            prow[arm] = {"pipeline_id": pipeline,
                         "calibration": {"rule": "strict_maximum", "tested": 1000, "contract": deepcopy(cal_contract)},
                         "future_cohort_tested": 1000, "true_route_control_introduced": dict.fromkeys(("W", "A", "M"), 1000)}
            rrow[arm] = {"pipeline_id": pipeline, "calibration_summary": {"tested": 1000, "maximum": 0},
                         "observed_counts": dict(zip(("W", "A", "M", "U"), (300, 300, 300, 100) if arm == "baseline" else selected)),
                         "gate_counts": {"tested": 1000, "positive": 950},
                         "known_truth_controls": {r: {"introduced": 1000, "correct": 900} for r in ("W", "A", "M")},
                         "provenance": {key: "Chosen synthetic record: " + pipeline + ":" + key for key in integration.PROVENANCE_KEYS}}
        plan["contexts"].append(prow)
        records["contexts"].append(rrow)
    cases = {"strict_separation": (plan, records)}
    tied_plan, tied = deepcopy(plan), deepcopy(records)
    for prow, row in zip(tied_plan["contexts"], tied["contexts"]):
        for arm in ("baseline", "selected"):
            prow[arm]["calibration"]["rule"] = "inclusive_maximum"
            row[arm]["calibration_summary"]["maximum_multiplicity"] = 1000
    cases["inclusive_all_tied"] = tied_plan, tied
    missing_plan, missing = deepcopy(plan), deepcopy(records)
    missing_plan["contexts"], missing["contexts"] = missing_plan["contexts"][:1], missing["contexts"][:1]
    for arm in ("baseline", "selected"):
        missing_plan["contexts"][0][arm]["true_route_control_introduced"] = dict.fromkeys(("W", "A", "M"), 0)
        missing["contexts"][0][arm]["known_truth_controls"] = {r: {"introduced": 0, "correct": 0} for r in ("W", "A", "M")}
    cases["one_context_no_truth_controls"] = missing_plan, missing
    for p, r in cases.values():
        r["plan_sha256"] = integration.canonical_digest(p)
    return cases


def exact_binomial_tail(n, k, p, lower_cdf):
    """Independent integer-coefficient evaluation; no preserved tail code."""
    a, b = p.numerator, p.denominator
    if a == 0 or a == b:
        outcome = n if a else 0
        return F(int(outcome <= k if lower_cdf else outcome >= k))
    mass, total = (b - a)**n, 0
    for j in range(n + 1):
        if j <= k if lower_cdf else j >= k:
            total += mass
        if j < n:
            mass = mass * (n - j) * a // ((j + 1) * (b - a))
    return F(total, b**n)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=integration.DEFAULT_REPOSITORY)
    args = parser.parse_args()
    engine, cp, threshold, eligibility = integration.load_dependencies(args.repository)
    checks = {"fixtures": 0, "exact_endpoint_checks": 0, "allocation_identities": 0,
              "projection_crosschecks": 0, "input_refusals": 0, "dependency_refusals": 0,
              "counterexamples": 0, "boundary_behaviors": 0}
    cases, results = fixtures(threshold), {}
    for name, (plan, records) in cases.items():
        result = integration.infer(engine, cp, threshold, eligibility, plan, records)
        results[name] = result
        for suffix, doc in (("plan", plan), ("observations", records), ("result", result)):
            (ROOT / ("example_" + name + "_" + suffix + ".json")).write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
        budget = result["confidence"]
        gamma, eta, alpha = (F(budget[k]) for k in ("per_calibration_error_exact", "per_count_endpoint_error_exact", "alpha_exact"))
        assert budget["calibration_components"] * gamma + budget["count_components"] * eta == alpha
        assert F(budget["global_error_bound_exact"]) == alpha
        checks["allocation_identities"] += 1
        for row in result["contexts"]:
            for arm in engine.ARMS:
                item = row[arm]
                cal = item["calibration"]
                numerical = cal["numerical_endpoint"]
                n, k = numerical["n"], numerical["equivalent_k"]
                fu = F(cal["control_false_gate_upper_exact"])
                assert fu == 1 if k == n else exact_binomial_tail(n, k, fu, True) <= gamma
                checks["exact_endpoint_checks"] += 1
                g = item["gate_counts"]
                gl = F(item["gate_positive_lower"]["exact"])
                assert gl == 0 if not g["positive"] else exact_binomial_tail(g["tested"], g["positive"], gl, False) <= eta
                checks["exact_endpoint_checks"] += 1
                upper, lower = {}, {}
                for route in engine.ROUTES:
                    lim = item["marginal_limits"][route]
                    upper[route], lower[route] = F(lim["observed_upper"]["exact"]), F(lim["correct_call_lower"]["exact"])
                    for target, n, k, is_lower in ((upper[route], lim["observed_trials"], lim["observed_successes"], False),
                                                   (lower[route], lim["control_trials"], lim["control_successes"], True)):
                        if not n or (is_lower and not k) or (not is_lower and k == n):
                            assert target == (0 if is_lower else 1)
                        else:
                            assert exact_binomial_tail(n, k, target, not is_lower) <= eta
                        checks["exact_endpoint_checks"] += 1
                beta = max(F(0), (gl - fu) / (1 - fu)) if fu < 1 else F(0)
                assert beta == F(item["eligibility"]["eligible_fraction_lower_exact"])
                caps = {r: min(F(1), upper[r] / (beta * lower[r])) if beta * lower[r] else F(1) for r in engine.ROUTES}
                assert item["caps"] == {r: str(caps[r]) for r in engine.ROUTES}
                expected = engine.capped_simplex_bounds(caps)
                for key in ("status", "lower", "upper"):
                    assert item[key] == expected[key]
                checks["projection_crosschecks"] += 1
            assert row["J"] == engine.ratio_interval(row["baseline"], row["selected"])
        checks["fixtures"] += 1
    assert results["strict_separation"]["reject_common_J"]
    for name in ("inclusive_all_tied", "one_context_no_truth_controls"):
        assert not results[name]["reject_common_J"]
        for row in results[name]["contexts"]:
            assert row["J"]["lower"]["exact"] == "0" and row["J"]["upper"]["exact"] is None
    assert all(row[a]["eligibility"]["eligible_fraction_lower_exact"] == "0"
               for row in results["inclusive_all_tied"]["contexts"] for a in engine.ARMS)
    checks["boundary_behaviors"] += 3

    plan, records = cases["strict_separation"]
    for share in (F(1, 8), F(1, 4), F(3, 4)):
        changed = deepcopy(plan)
        changed["calibration_error_share"] = str(share)
        budget = integration.validate_plan(engine, threshold, changed)
        assert 4 * F(budget["per_calibration_error_exact"]) + 28 * F(budget["per_count_endpoint_error_exact"]) == F(1, 20)
        if share == F(1, 8):
            assert F(budget["per_calibration_error_exact"]) == F(budget["per_count_endpoint_error_exact"]) == F(1, 640)
        checks["allocation_identities"] += 1
    gamma = F(1, 640)
    upper59 = engine.certified_one_sided(cp, 0, 59, gamma, False)[0]
    upper125 = engine.certified_one_sided(cp, 0, 125, gamma, False)[0]
    upper126 = engine.certified_one_sided(cp, 0, 126, gamma, False)[0]
    assert F(19, 20)**125 > gamma >= F(19, 20)**126
    assert F(1, 10) < upper59 < F(11, 100) and upper125 > F(1, 20) > upper126
    for n, upper in ((59, upper59), (125, upper125), (126, upper126)):
        assert (1 - upper)**n <= gamma
        checks["exact_endpoint_checks"] += 1
    # A true common-J decision remains unevaluable on incompatible outer caps.
    bad_caps = engine.capped_simplex_bounds(dict.fromkeys(engine.ROUTES, F(1, 4)))
    j = engine.ratio_interval(bad_caps, bad_caps)
    assert engine.common_intersection([j, j])["status"] == "unevaluable_observation_contract"
    assert not engine.common_intersection([j, j])["separated"]
    checks["boundary_behaviors"] += 1
    # Calibration Uniform[0,1], strict maximum n=1: ideal failure probability
    # gamma=.05. Independent future correct-call count n=1, true p=.049:
    # the lower endpoint on success exceeds p, hence failure probability .049.
    # Combining their separate .05 budgets does not give simultaneous .95.
    lower1 = engine.certified_one_sided(cp, 1, 1, F(1, 20), True)[0]
    assert lower1 > F(49, 1000)
    ideal_joint_failure = F(1, 20) + F(49, 1000) - F(1, 20) * F(49, 1000)
    assert ideal_joint_failure == F(1931, 20000) > F(1, 20)
    certified_calibration_upper = engine.certified_one_sided(cp, 0, 1, F(1, 20), False)[0]
    calibration_failure = 1 - certified_calibration_upper
    joint_failure = calibration_failure + F(49, 1000) - calibration_failure * F(49, 1000)
    assert joint_failure > F(1, 20)
    checks["counterexamples"] += 1

    def refuses(call, kind="input_refusals"):
        try:
            call()
        except (ValueError, OSError, KeyError, TypeError, ArithmeticError):
            checks[kind] += 1
        else:
            raise AssertionError("Invalid input accepted")
    def change(doc, path, value):
        doc = deepcopy(doc)
        at = doc
        for key in path[:-1]:
            at = at[key]
        at[path[-1]] = value
        return doc
    for path, value in (
            (("alpha",), 0.05), (("alpha",), "0"), (("alpha",), "1"),
            (("calibration_error_share",), "0"), (("calibration_error_share",), "1"),
            (("calibration_error_share",), "1/1000000000000"), (("extra",), 1),
            (("contract", "endpoint_sampling"), "unconditional_binomial_only"),
            (("contract", "chronology"), "same_data_for_fit_and_evaluation"),
            (("contexts", 0, "baseline", "calibration", "tested"), 0),
            (("contexts", 0, "baseline", "calibration", "tested"), True),
            (("contexts", 0, "baseline", "calibration", "rule"), "chosen_after_outcomes"),
            (("contexts", 0, "baseline", "calibration", "contract", "score_pipeline"), "fitted_on_calibration"),
            (("contexts", 0, "baseline", "future_cohort_tested"), 5001),
            (("contexts", 1, "id"), "A_rich")):
        changed = change(plan, path, value)
        refuses(lambda changed=changed: integration.validate_plan(engine, threshold, changed))
    for path, value in (
            (("plan_sha256",), "0" * 64), (("provenance",), ""), (("contexts",), records["contexts"][:1]),
            (("contexts", 0, "baseline", "pipeline_id"), "different"),
            (("contexts", 0, "baseline", "calibration_summary", "tested"), 999),
            (("contexts", 0, "baseline", "calibration_summary", "maximum"), 0.0),
            (("contexts", 0, "baseline", "calibration_summary", "positive"), 0),
            (("contexts", 0, "baseline", "observed_counts", "U"), 0),
            (("contexts", 0, "baseline", "gate_counts", "tested"), 999),
            (("contexts", 0, "baseline", "gate_counts", "positive"), 899),
            (("contexts", 0, "baseline", "known_truth_controls", "W", "introduced"), 999),
            (("contexts", 0, "baseline", "known_truth_controls", "W", "correct"), 1001),
            (("contexts", 0, "baseline", "provenance", "frozen_pipeline_record"), " ")):
        changed = change(records, path, value)
        refuses(lambda changed=changed: integration.infer(engine, cp, threshold, eligibility, plan, changed))
    tied_plan, tied = cases["inclusive_all_tied"]
    for k in (0, 1001, True):
        changed = change(tied, ("contexts", 0, "baseline", "calibration_summary", "maximum_multiplicity"), k)
        refuses(lambda changed=changed: integration.infer(engine, cp, threshold, eligibility, tied_plan, changed))
    changed = deepcopy(tied)
    del changed["contexts"][0]["baseline"]["calibration_summary"]["maximum_multiplicity"]
    refuses(lambda: integration.infer(engine, cp, threshold, eligibility, tied_plan, changed))
    changed_plan = change(plan, ("contexts", 0, "baseline", "future_cohort_tested"), 5000)
    for row in changed_plan["contexts"]:
        for arm in engine.ARMS:
            row[arm]["future_cohort_tested"] = 5000
    refuses(lambda: integration.validate_plan(engine, threshold, changed_plan))
    for raw in ('{"a":1,"a":2}', '{"x":NaN}', '{"x":Infinity}', b" " * (engine.MAX_INPUT_BYTES + 1)):
        refuses(lambda raw=raw: engine.load_json(raw))
    # Deliberate hash mismatch without copying or modifying frozen sources.
    read_bytes = Path.read_bytes
    for relative, _ in integration.PINS.values():
        altered = (Path(args.repository) / relative).resolve()
        def fake_read(path, altered=altered):
            raw = read_bytes(path)
            return raw + b"\n" if path.resolve() == altered else raw
        with patch.object(Path, "read_bytes", fake_read):
            refuses(lambda: integration.load_dependencies(args.repository), "dependency_refusals")

    receipt = {
        "status": "pass", "all_fixtures_synthetic": True, "checks": checks,
        "producer_sha256": hashlib.sha256((ROOT / "integrated_inference.py").read_bytes()).hexdigest(),
        "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "dependencies": {key: value[1] for key, value in integration.PINS.items()},
        "planning_example": {"C": 2, "alpha": "1/20", "calibration_error_share": "1/8", "gamma_and_eta": "1/640",
                             "strict_59_upper_exact": str(upper59), "strict_125_upper_exact": str(upper125), "strict_126_upper_exact": str(upper126),
                             "smallest_n_for_ideal_strict_5_percent_bound": 126,
                             "exact_comparison": "(19/20)^125 > 1/640 >= (19/20)^126"},
        "unbudgeted_composition_counterexample": {"separate_calibration_error": "1/20", "separate_count_error": "1/20",
                                                    "ideal_endpoint_joint_failure_exact": str(ideal_joint_failure),
                                                    "certified_endpoint_joint_failure_exact": str(joint_failure),
                                                    "scope": "Simultaneous-coverage claim, not a simulated common-J rejection rate."},
        "scope": "Bounded arithmetic, allocation, interface and projection checks; no native controls, power calculation, study recommendation or general proof by enumeration.",
    }
    (ROOT / "VERIFICATION.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
