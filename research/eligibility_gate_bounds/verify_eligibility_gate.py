#!/usr/bin/env python3
"""Bounded synthetic checks for the eligibility extension; no biological data."""
from copy import deepcopy
from fractions import Fraction as F
import argparse
import hashlib
import json
from math import comb
from pathlib import Path

import eligibility_gate_bounds as extension

ROOT = Path(__file__).resolve().parent


def fixtures(engine):
    contract = dict(extension.CONTRACT, endpoint_unit="synthetic full-cohort endpoint unit")
    gate = {"mode": "gate", "provenance": "synthetic", "contract": contract,
            "gate_positive_lower": "19/20", "other_false_gate_upper": "1/20"}
    count_contract = dict(contract, **extension.COUNT_CONTRACT,
                          true_route_control_unit="synthetic independently known true-route unit",
                          known_Other_control_unit="synthetic independently known true-Other unit")

    def arm(values):
        return {"observed_counts": dict(zip(engine.LABELS, values)),
                "known_truth_controls": {r: {"introduced": 1000, "correct": 900} for r in engine.ROUTES},
                "gate_counts": {"tested": 1000, "positive": 950},
                "known_Other_controls": {"tested": 1000, "positive": 0}}

    calibrated = {"mode": "counts", "provenance": "synthetic", "contract": count_contract,
                  "alpha": "1/20", "contexts": [
                      {"id": "A_rich", "baseline": arm((300, 300, 300, 100)), "selected": arm((90, 720, 90, 100))},
                      {"id": "A_poor", "baseline": arm((300, 300, 300, 100)), "selected": arm((405, 90, 405, 100))}]}
    absent = deepcopy(calibrated)
    for row in absent["contexts"]:
        for name in engine.ARMS:
            row[name]["known_Other_controls"] = {"tested": 0, "positive": 0}
    return {"population_gate": gate, "calibrated_counts": calibrated, "no_Other_controls": absent}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=extension.DEFAULT_REPOSITORY)
    args = parser.parse_args()
    engine, cp = extension.load_engine(args.repository)
    checks = {"gate_witnesses": 0, "gate_grid_inequalities": 0, "endpoint_certificates": 0,
              "small_binomial_coverage_cases": 0, "refusals": 0}
    # Independent exact inequality evaluation and sharpness witnesses, including
    # F=1, T=0, beta=1 and strict-positive-T limiting sequences.
    grid = [F(i, 8) for i in range(9)]
    for gl in grid:
        for fu in grid:
            bound = extension.gate_bound(engine, gl, fu)
            beta = F(bound["eligible_fraction_lower_exact"])
            witness = {k: F(v) for k, v in bound["closed_model_witness"].items()}
            assert witness["T"] == beta and witness["f"] <= fu
            assert witness["g"] == witness["a"] * witness["T"] + witness["f"] * (1 - witness["T"]) == gl
            if beta == 0:
                for t in (F(1, 2), F(1, 1000)):
                    assert gl * t + gl * (1 - t) == gl and gl <= fu
            checks["gate_witnesses"] += 1
    for t in grid:
        for a in grid:
            for f in grid:
                g = a * t + f * (1 - t)
                for fu in grid:
                    if fu >= f:
                        beta = F(extension.gate_bound(engine, g, fu)["eligible_fraction_lower_exact"])
                        assert beta <= t
                        checks["gate_grid_inequalities"] += 1

    docs, results = fixtures(engine), {}
    for name, doc in docs.items():
        result = extension.population_gate_bounds(engine, doc) if doc["mode"] == "gate" else extension.count_bounds(engine, cp, doc)
        raw = json.dumps(doc, indent=2, sort_keys=True) + "\n"
        result["input_sha256"] = hashlib.sha256(raw.encode()).hexdigest()
        (ROOT / ("example_" + name + ".json")).write_text(raw)
        (ROOT / ("example_" + name + "_result.json")).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        results[name] = result
    assert results["population_gate"]["eligibility"]["eligible_fraction_lower_exact"] == "18/19"
    assert results["calibrated_counts"]["reject_common_J"]
    assert not results["no_Other_controls"]["reject_common_J"]
    for name in ("calibrated_counts", "no_Other_controls"):
        result = results[name]
        assert result["confidence"]["one_sided_allocations"] == 32
        assert result["confidence"]["per_endpoint_error_exact"] == "1/640"
        tail = F(result["confidence"]["per_endpoint_error_exact"])
        for row in result["contexts"]:
            for arm in engine.ARMS:
                cell = row[arm]
                if name == "no_Other_controls":
                    assert cell["eligibility"]["eligible_fraction_lower_exact"] == "0"
                    assert cell["caps"] == dict.fromkeys(engine.ROUTES, "1")
                    assert cell["lower"]["exact"] == "0" and cell["upper"]["exact"] is None
                endpoints = []
                for item in cell["marginal_limits"].values():
                    endpoints.extend([(item["observed_successes"], item["observed_trials"], item["observed_upper"], False),
                                      (item["control_successes"], item["control_trials"], item["correct_call_lower"], True)])
                gates = cell["gate_limits"]
                endpoints.extend([(gates["gate_positive_successes"], gates["gate_trials"], gates["gate_positive_lower"], True),
                                  (gates["Other_positive_successes"], gates["Other_trials"], gates["other_false_gate_upper"], False)])
                for k, n, ep, lower in endpoints:
                    value = F(ep["exact"])
                    if "support_boundary" not in ep["certificate"]:
                        assert cp.tail_at_most(n, k, float(value), tail, lower)
                    else:
                        assert value == (0 if lower else 1)
                    checks["endpoint_certificates"] += 1
    # Enumerate complete small binomial experiments to check the reused one-sided
    # limits in both directions, using rational probabilities and exact masses.
    tail = F(1, 20)
    for n in range(1, 9):
        lower = [engine.certified_one_sided(cp, k, n, tail, True)[0] for k in range(n + 1)]
        upper = [engine.certified_one_sided(cp, k, n, tail, False)[0] for k in range(n + 1)]
        for p in grid:
            mass = [comb(n, k) * p**k * (1 - p)**(n - k) for k in range(n + 1)]
            assert sum(mass[k] for k in range(n + 1) if lower[k] > p) <= tail
            assert sum(mass[k] for k in range(n + 1) if upper[k] < p) <= tail
            checks["small_binomial_coverage_cases"] += 2
    # A beta bound is a full-cohort fraction, not PPV. Exact known-beta caps
    # must enlarge as eligibility or correct-call information weakens.
    observed = dict.fromkeys(engine.ROUTES, F(1, 5))
    correct = dict.fromkeys(engine.ROUTES, F(3, 5))
    assert extension.eligibility_caps(engine, observed, correct, F(1, 10)) == dict.fromkeys(engine.ROUTES, F(1))
    assert extension.eligibility_caps(engine, observed, correct, F(1)) == dict.fromkeys(engine.ROUTES, F(1, 3))
    assert extension.eligibility_caps(engine, dict.fromkeys(engine.ROUTES, 0), correct, 0) == dict.fromkeys(engine.ROUTES, F(1))

    def refuses(call):
        try:
            call()
        except (ValueError, TypeError, KeyError, OSError):
            checks["refusals"] += 1
        else:
            raise AssertionError("Malformed input was accepted")

    for value in (True, 0.5, "1/0", "1e-2", "-1", "2", "9" * 201, 2**257):
        refuses(lambda value=value: extension.gate_bound(engine, value, "1/20"))
    for raw in ('{"a":1,"a":2}', '{"x":NaN}', '{"x":Infinity}', b" " * (engine.MAX_INPUT_BYTES + 1)):
        refuses(lambda raw=raw: engine.load_json(raw))
    for path, value in (
            (("alpha",), "0"), (("extra",), 1), (("contract", "cohort"), "gate_positive_only"),
            (("contexts", 0, "baseline", "gate_counts", "tested"), True),
            (("contexts", 0, "baseline", "gate_counts", "tested"), 999),
            (("contexts", 0, "baseline", "gate_counts", "positive"), 1001),
            (("contexts", 0, "baseline", "known_Other_controls", "positive"), -1),
            (("contexts", 0, "baseline", "known_truth_controls", "W", "correct"), 1001)):
        altered = deepcopy(docs["calibrated_counts"])
        at = altered
        for key in path[:-1]:
            at = at[key]
        at[path[-1]] = value
        refuses(lambda altered=altered: extension.count_bounds(engine, cp, altered))
    missing = deepcopy(docs["calibrated_counts"])
    del missing["contexts"][0]["baseline"]["known_Other_controls"]
    refuses(lambda: extension.count_bounds(engine, cp, missing))
    excessive = deepcopy(docs["calibrated_counts"])
    excessive["contexts"] = [dict(deepcopy(excessive["contexts"][0]), id=str(i)) for i in range(4)]
    refuses(lambda: extension.count_bounds(engine, cp, excessive))
    empty = deepcopy(docs["calibrated_counts"])
    empty["contexts"] = empty["contexts"][:1]
    for arm in engine.ARMS:
        cell = empty["contexts"][0][arm]
        cell["observed_counts"] = dict.fromkeys(engine.LABELS, 0)
        cell["gate_counts"] = cell["known_Other_controls"] = {"tested": 0, "positive": 0}
        cell["known_truth_controls"] = {r: {"introduced": 0, "correct": 0} for r in engine.ROUTES}
    empty_result = extension.count_bounds(engine, cp, empty)
    assert not empty_result["reject_common_J"]
    assert empty_result["contexts"][0]["J"]["lower"]["exact"] == "0"
    assert empty_result["contexts"][0]["J"]["upper"]["exact"] is None
    receipt = {
        "status": "pass", "all_inputs_synthetic": True, "checks": checks,
        "producer_sha256": hashlib.sha256((ROOT / "eligibility_gate_bounds.py").read_bytes()).hexdigest(),
        "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "classification_sha256": extension.CLASSIFICATION_SHA256, "CP_sha256": extension.CP_SHA256,
        "calibrated_example_rejects": results["calibrated_counts"]["reject_common_J"],
        "no_Other_controls_example_rejects": results["no_Other_controls"]["reject_common_J"],
        "scope": "Bounded synthetic implementation checks; no native data, power study or external biological validation.",
    }
    (ROOT / "VERIFICATION.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
