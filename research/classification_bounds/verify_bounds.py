#!/usr/bin/env python3
"""Bounded synthetic checks and artifact reproduction for classification bounds."""
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

import classification_bounds as engine

ROOT = Path(__file__).resolve().parent


def document(mode, rows):
    contract = dict(engine.CONTRACT, endpoint_unit="synthetic independently eligible true-triad unit")
    doc = {"mode": mode, "provenance": "synthetic", "contract": contract, "contexts": rows}
    if mode == "counts":
        contract.update(engine.COUNT_CONTRACT)
        contract["known_truth_control_unit"] = "synthetic independently known introduced true-route unit"
        doc["alpha"] = "1/20"
    return doc


def population(observed, lower):
    return {"observed": dict(zip(engine.LABELS, map(str, observed))),
            "correct_call_lower": dict(zip(engine.ROUTES, map(str, lower)))}


def counts(observed, correct=900, introduced=1000):
    return {"observed_counts": dict(zip(engine.LABELS, observed)),
            "known_truth_controls": {r: {"introduced": introduced, "correct": correct} for r in engine.ROUTES}}


def fixture_documents():
    baseline = population((F(1, 6), F(1, 2), F(1, 3), 0), (F(1, 2), 1, 1))
    selected2 = population((F(2, 7), F(4, 7), F(1, 7), 0), (F(1, 2), 1, 1))
    shared = document("population", [
        {"id": "uniform", "baseline": baseline, "selected": baseline},
        {"id": "WM_tilt", "baseline": baseline, "selected": selected2}])
    countsep = document("counts", [
        {"id": "A_rich", "baseline": counts((300, 300, 300, 100)), "selected": counts((90, 720, 90, 100))},
        {"id": "A_poor", "baseline": counts((300, 300, 300, 100)), "selected": counts((405, 90, 405, 100))}])
    absent = deepcopy(countsep)
    for row in absent["contexts"]:
        for arm in engine.ARMS:
            row[arm]["known_truth_controls"] = counts((0, 0, 0, 0), correct=0, introduced=0)["known_truth_controls"]
    denom = population((F(1, 5), F(1, 5), F(1, 5), F(2, 5)), (F(3, 5),) * 3)
    denominator = document("population", [{"id": "U_retained", "baseline": denom, "selected": denom}])
    bad = population((F(1, 10), F(1, 10), F(1, 10), F(7, 10)), (F(9, 10),) * 3)
    incompatible = document("population", [{"id": "incompatible_contract", "baseline": bad, "selected": bad}])
    return {"shared_classifier": shared, "count_separation": countsep,
            "no_control_observations": absent, "retained_U_denominator": denominator,
            "incompatible_population_contract": incompatible}


def replay_classifier(observed, lower, latent, completion):
    p = [F(latent[r]) for r in engine.ROUTES]
    o = [F(observed[r]) for r in engine.LABELS]
    d = [F(lower[r]) for r in engine.ROUTES]
    matrix = [[F(x) for x in row] for row in completion["matrix_exact"]]
    assert all(x >= 0 for row in matrix for x in row)
    assert all(sum(matrix[j][i] for j in range(4)) == 1 for i in range(3))
    assert all(matrix[i][i] >= d[i] for i in range(3))
    assert all(sum(matrix[j][i] * p[i] for i in range(3)) == o[j] for j in range(4))


def main():
    checks = {"population_completion_certificates": 0, "positive_grid_bounds": 0,
              "count_endpoint_certificates": 0, "refusals": 0}
    docs = fixture_documents()
    results = {}
    for name, doc in docs.items():
        result = engine.population_bounds(doc) if doc["mode"] == "population" else engine.count_bounds(doc)
        results[name] = result
        for row in result["contexts"]:
            for arm in engine.ARMS:
                item = row[arm]
                if item["status"] == "ok" and doc["mode"] == "population":
                    for label, completion in item["classifier_completions"].items():
                        replay_classifier(item["observed_unconditional"], item["correct_call_lower"], item[label], completion)
                        checks["population_completion_certificates"] += 1
        raw = json.dumps(doc, indent=2, sort_keys=True) + "\n"
        result["input_sha256"] = hashlib.sha256(raw.encode()).hexdigest()
        (ROOT / ("example_" + name + ".json")).write_text(raw)
        (ROOT / ("example_" + name + "_result.json")).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    assert results["shared_classifier"]["common_J"]["status"] == "compatible"
    for row in results["shared_classifier"]["contexts"]:
        assert F(row["J"]["lower"]["exact"]) <= 1
        assert row["J"]["upper"]["exact"] is None or F(row["J"]["upper"]["exact"]) >= 1
    assert results["count_separation"]["reject_common_J"]
    assert results["no_control_observations"]["common_J"]["status"] == "not_rejected"
    assert not results["no_control_observations"]["reject_common_J"]
    assert results["retained_U_denominator"]["contexts"][0]["J"]["lower"]["exact"] == "1"
    assert results["retained_U_denominator"]["contexts"][0]["J"]["upper"]["exact"] == "1"
    assert results["incompatible_population_contract"]["common_J"]["status"] == "unevaluable_observation_contract"

    # Exact finite grid verifies both bounds on positive laws, including sparse
    # caps and positive singleton domains. The independent reviewer uses a
    # different polygon-extremum construction for the general endpoint check.
    for wi in range(1, 7):
        for ai in range(1, 7):
            for mi in range(1, 7):
                caps = dict(zip(engine.ROUTES, (F(wi, 6), F(ai, 6), F(mi, 6))))
                result = engine.capped_simplex_bounds(caps)
                if result["status"] != "ok":
                    continue
                lo = F(result["lower"]["exact"])
                hi = None if result["upper"]["exact"] is None else F(result["upper"]["exact"])
                for w in range(1, 18):
                    for a in range(1, 18 - w):
                        p = (F(w, 18), F(a, 18), F(18 - w - a, 18))
                        if all(p[i] <= caps[r] for i, r in enumerate(engine.ROUTES)):
                            q = p[1]**2 / (p[0] * p[2])
                            assert lo <= q and (hi is None or q <= hi)
                            checks["positive_grid_bounds"] += 1
                for key in ("lower_closure_witness", "upper_closure_witness", "positive_feasible_witness"):
                    p = [F(result[key][r]) for r in engine.ROUTES]
                    assert sum(p) == 1 and all(0 <= p[i] <= caps[r] for i, r in enumerate(engine.ROUTES))

    cp = engine.load_cp()
    for result in (results["count_separation"], results["no_control_observations"]):
        tail = F(result["confidence"]["per_endpoint_error_exact"])
        assert result["confidence"]["one_sided_allocations"] == 24
        for row in result["contexts"]:
            for arm in engine.ARMS:
                for limits in row[arm]["marginal_limits"].values():
                    for prefix, is_lower in (("observed", False), ("control", True)):
                        k, n = limits[prefix + "_successes"], limits[prefix + "_trials"]
                        ep = limits["correct_call_lower" if is_lower else "observed_upper"]
                        value = F(ep["exact"])
                        if "support_boundary" not in ep["certificate"]:
                            assert cp.tail_at_most(n, k, float(value), tail, is_lower)
                        else:
                            assert value == (0 if is_lower else 1)
                        checks["count_endpoint_certificates"] += 1

    def refuses(call):
        try:
            call()
        except (ValueError, TypeError, KeyError):
            checks["refusals"] += 1
        else:
            raise AssertionError("Malformed/unsupported input was accepted")

    for value in (True, 0.5, "NaN", "1/0", "1e999999999", "9" * 201, "1/" + "9" * 100, 2**257):
        refuses(lambda value=value: engine.rational(value))
    for raw in ('{"a":1,"a":2}', '{"x":NaN}', '{"x":Infinity}', b" " * (engine.MAX_INPUT_BYTES + 1)):
        refuses(lambda raw=raw: engine.load_json(raw))
    for path, value in (
            (("extra",), True), (("alpha",), "0"), (("contract", "cohort"), "selected_by_observed_WAM"),
            (("contexts", 0, "extra"), 1), (("contexts", 0, "baseline", "observed_counts", "W"), True),
            (("contexts", 0, "baseline", "observed_counts", "U"), -1),
            (("contexts", 0, "baseline", "known_truth_controls", "W", "correct"), 1001)):
        altered = deepcopy(docs["count_separation"])
        place = altered
        for key in path[:-1]:
            place = place[key]
        place[path[-1]] = value
        refuses(lambda altered=altered: engine.count_bounds(altered))
    missing_u = deepcopy(docs["count_separation"])
    del missing_u["contexts"][0]["baseline"]["observed_counts"]["U"]
    refuses(lambda: engine.count_bounds(missing_u))
    huge_work = deepcopy(docs["count_separation"])
    huge_work["contexts"] *= 3
    for i, row in enumerate(huge_work["contexts"]):
        # Avoid aliased rows from the list multiplication.
        huge_work["contexts"][i] = dict(deepcopy(row), id="work_" + str(i))
    refuses(lambda: engine.count_bounds(huge_work))
    # Explicit zero observations do not assert population zeros.
    z = counts((0, 0, 0, 0), 0, 0)
    zero = engine.count_bounds(document("counts", [{"id": "empty", "baseline": z, "selected": z}]))
    assert zero["contexts"][0]["J"]["lower"]["exact"] == "0"
    assert zero["contexts"][0]["J"]["upper"]["exact"] is None
    assert not zero["reject_common_J"]
    # Positive-domain boundaries and exact transport special case.
    assert engine.capped_simplex_bounds({"W": 0, "A": 1, "M": 1})["status"] == "no_strictly_positive_latent_law"
    exact = engine.population_arm({"W": "1/4", "A": "1/2", "M": "1/4", "U": 0}, dict.fromkeys(engine.ROUTES, 1))
    assert exact["lower"]["exact"] == exact["upper"]["exact"] == "4"
    replay_classifier(exact["observed_unconditional"], exact["correct_call_lower"], exact["positive_feasible_witness"],
                      exact["classifier_completions"]["positive_feasible_witness"])
    receipt = {"status": "pass", "all_inputs_synthetic": True, "checks": checks,
               "producer_sha256": hashlib.sha256((ROOT / "classification_bounds.py").read_bytes()).hexdigest(),
               "source_CP_sha256": engine.CP_SHA256,
               "count_example_rejects": results["count_separation"]["reject_common_J"],
               "no_control_example_rejects": results["no_control_observations"]["reject_common_J"],
               "claim": "Executed bounded checks, not a general power or biological validation result."}
    (ROOT / "VERIFICATION.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
