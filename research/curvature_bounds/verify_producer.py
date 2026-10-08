"""Generate R18 synthetic cases and run non-statistical producer checks."""
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import curvature_bounds as engine

BASE = Path(__file__).resolve().parent


def singleton(values):
    return [[str(value), str(value)] for value in values]


def context(name, masses, growth=(1, 1, 1), recovery=(1, 1, 1)):
    return {"name": name, "endpoint_masses": singleton(masses),
            "supply_weights": singleton((1, 1, 1)),
            "growth_yields": singleton(growth),
            "recovery_probabilities": singleton(recovery)}


def request(contexts, forecast=None):
    return {"schema_version": 1, "provenance": "synthetic",
            "assumptions": copy.deepcopy(engine.REQUIRED_ASSUMPTIONS),
            "contexts": contexts, "forecast_K": forecast}


def direct(point):
    """Separate explicit product formula; do not call engine's ratio kernel."""
    m, q, g, r = (tuple(Fraction(x) for x in point[key])
                  for key in engine.GROUPS)
    return (m[1]*m[1]*q[0]*q[2]*g[0]*g[2]*r[0]*r[2] /
            (m[0]*m[2]*q[1]*q[1]*g[1]*g[1]*r[1]*r[1]))


def fixtures():
    exact_mimic = [context("A", (1, 2, 1), (1, 2, 1)),
                   context("B", (2, 2, Fraction(1, 2)),
                           (2, 2, Fraction(1, 2)))]
    precise = copy.deepcopy(exact_mimic)
    for item in precise:
        item["growth_yields"] = [[str(Fraction(pair[0])*Fraction(99, 100)),
                                 str(Fraction(pair[0])*Fraction(101, 100))]
                                for pair in item["growth_yields"]]
    broad = copy.deepcopy(exact_mimic)
    for item in broad:
        item["growth_yields"] = [["1/4", "4"]] * 3
    unequal = [context("A", (1, 2, 1)), context("B", (1, 3, 1))]
    contact = [context("A", (1, 1, 1)), context("B", (1, 2, 1))]
    contact[0]["endpoint_masses"][1] = ["1", "2"]
    contact[1]["endpoint_masses"][1] = ["2", "3"]
    irrational = [context("variable_middle", (1, 1, 1)),
                  context("fixed_K_two", (1, 1, Fraction(1, 2)))]
    irrational[0]["endpoint_masses"][1] = ["1", "2"]
    gross_loss = [context("A", (1, 2, 1)), context("B", (1, 2, 1))]
    for item in gross_loss:
        item["recovery_probabilities"] = [["1/1000000", "1"]] * 3
    all_factors = context("all_four_factors", (1, 2, 3))
    all_factors["endpoint_masses"] = [["1", "2"], ["2", "3"], ["3", "4"]]
    all_factors["supply_weights"] = [["1", "2"], ["3", "4"], ["5", "6"]]
    all_factors["growth_yields"] = [["1/2", "1"], ["1", "2"], ["2", "3"]]
    all_factors["recovery_probabilities"] = [
        ["1/4", "1/2"], ["1/2", "3/4"], ["1/3", "2/3"]]
    return {
        "exact_growth_mimic": request(exact_mimic, "4"),
        "precise_growth_controls": request(precise, "4"),
        "broad_growth_controls": request(broad, "4"),
        "unequal_corrected_curvature": request(unequal),
        "contact_is_feasible": request(contact, "4"),
        "free_common_vs_fixed_forecast": request(copy.deepcopy(contact), "2"),
        "irrational_interior_witness": request(irrational, "2"),
        "gross_but_finitely_bounded_loss": request(gross_loss, "4"),
        "K_one_is_not_full_conventional_fit":
            request([context("nonzero_eta", (2, 1, Fraction(1, 2)))], "1"),
        "uncertainty_in_all_four_factors": request([all_factors], "16"),
    }


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def verify():
    if not __debug__:
        raise RuntimeError("Producer verification requires ordinary Python without -O/-OO")
    counts = {}
    def check(condition, category):
        if not condition:
            raise RuntimeError("Producer check failed: " + category)
        counts[category] = counts.get(category, 0) + 1

    cases, results = fixtures(), {}
    fixture_dir, result_dir = BASE/"fixtures", BASE/"results"
    fixture_dir.mkdir(exist_ok=True)
    result_dir.mkdir(exist_ok=True)
    for name, data in cases.items():
        write_json(fixture_dir/(name+".json"), data)
        result = engine.certify(data)
        result["input_sha256"] = hashlib.sha256(
            (fixture_dir/(name+".json")).read_bytes()).hexdigest()
        write_json(result_dir/(name+".json"), result)
        results[name] = result
        for admitted, item in zip(data["contexts"], result["contexts"]):
            for corner, endpoint in (("minimum_corner", "lower"),
                                     ("maximum_corner", "upper")):
                point = item[corner]
                check(direct(point) == Fraction(item["K_interval"][endpoint]),
                      "separate_product_endpoint_checks")
                for group in engine.GROUPS:
                    check(all(Fraction(pair[0]) <= Fraction(x) <= Fraction(pair[1])
                              for x, pair in zip(point[group], admitted[group])),
                          "corner_within_admitted_bounds")
                # A normalized witness is a valid simplex vector. Its ratio is
                # unchanged; this does not treat independent share bounds as masses.
                normalized = copy.deepcopy(point)
                for group in ("endpoint_masses", "supply_weights"):
                    total = sum(Fraction(x) for x in point[group])
                    normalized[group] = [str(Fraction(x)/total) for x in point[group]]
                    check(sum(Fraction(x) for x in normalized[group]) == 1,
                          "normalization_of_witness")
                check(direct(normalized) == direct(point),
                      "normalization_preserves_curvature")
        check(result["empirical_histogram_confidence_or_power_claim"] is False,
              "no_statistical_claim")

    precise = results["precise_growth_controls"]
    expected_lo, expected_hi = Fraction(9801, 10201), Fraction(10201, 9801)
    check(all(Fraction(x["K_interval"]["lower"]) == expected_lo and
              Fraction(x["K_interval"]["upper"]) == expected_hi
              for x in precise["contexts"]), "analytical_precise_control_interval")
    check(precise["fixed_curvature_forecast"]["status"] == "conditionally_incompatible"
          and precise["conventional_supply_growth_recovery_model"]["status"] ==
          "conditionally_feasible", "precise_controls_distinguish_raw_mimic_target")
    broad = results["broad_growth_controls"]
    check(all(x["K_interval"]["lower"] == "1/64" and
              x["K_interval"]["upper"] == "1024" for x in broad["contexts"]),
          "analytical_broad_control_interval")
    check(broad["fixed_curvature_forecast"]["status"] == "conditionally_feasible"
          and broad["conventional_supply_growth_recovery_model"]["status"] ==
          "conditionally_feasible", "broad_controls_leave_competing_targets_feasible")
    check(results["exact_growth_mimic"]["free_common_curvature"]["intersection_lower"] == "1"
          and results["exact_growth_mimic"]["free_common_curvature"]["intersection_upper"] == "1",
          "exact_controls_remove_growth_mimic")
    unequal = results["unequal_corrected_curvature"]["free_common_curvature"]
    check(unequal["intersection_lower"] == "9" and unequal["intersection_upper"] == "4"
          and unequal["intersection_empty"], "different_residual_targets_are_incompatible")
    contact = results["contact_is_feasible"]["free_common_curvature"]
    check(contact["intersection_lower"] == contact["intersection_upper"] == "4"
          and not contact["intersection_empty"], "closed_contact_is_feasible")
    split = results["free_common_vs_fixed_forecast"]
    check(not split["free_common_curvature"]["intersection_empty"] and
          split["fixed_curvature_forecast"]["status"] == "conditionally_incompatible",
          "free_common_is_distinct_from_fixed_forecast")
    irrational = results["irrational_interior_witness"]["free_common_curvature"]
    check(irrational["intersection_lower"] == irrational["intersection_upper"] == "2",
          "real_interior_feasibility_without_rational_witness")
    eta_only = results["K_one_is_not_full_conventional_fit"]
    check(eta_only["conventional_qgr_necessary_curvature_condition"]["status"] ==
          "conditionally_feasible" and
          eta_only["conventional_supply_growth_recovery_model"]["status"] ==
          "conditionally_incompatible", "K_one_is_not_sufficient_for_full_conventional_fit")
    all_factors = results["uncertainty_in_all_four_factors"]["contexts"][0]
    check(all_factors["K_interval"]["lower"] == "5/864" and
          all_factors["K_interval"]["upper"] == "16",
          "analytical_all_factor_uncertainty_interval")
    check(all_factors["conventional_qgr_model"]["scale_intersection_lower"] == "1" and
          all_factors["conventional_qgr_model"]["scale_intersection_upper"] == "6/5",
          "analytical_all_factor_full_conventional_scale_interval")
    check(all(Fraction(item["K_interval"]["lower"]) == Fraction(1, 250000000000) and
              Fraction(item["K_interval"]["upper"]) == 4000000000000
              for item in results["gross_but_finitely_bounded_loss"]["contexts"]),
          "gross_finite_loss_is_uninformative_not_an_unknown_bound")

    # The scaling property is exercised on unequal, nonuniform parameter vectors.
    point = {"endpoint_masses": ("2", "7", "3"),
             "supply_weights": ("3", "2", "5"),
             "growth_yields": ("2/3", "5/4", "7/3"),
             "recovery_probabilities": ("1/2", "2/3", "3/4")}
    original = direct(point)
    for group in engine.GROUPS:
        modified = copy.deepcopy(point)
        modified[group] = tuple(str(Fraction(x)*Fraction(3, 7)) for x in point[group])
        check(direct(modified) == original, "context_common_scale_cancels")

    invalid = []
    def changed(path, value):
        data = copy.deepcopy(cases["exact_growth_mimic"])
        target = data
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        return data
    for value in (0, -1, True, 0.5, None, "Infinity", "1/0",
                  "1/"+"9"*30, 2**40):
        invalid.append(changed(("contexts", 0, "endpoint_masses", 0, 0), value))
    invalid += [
        changed(("contexts", 0, "growth_yields", 0), ["2", "1"]),
        changed(("contexts", 0, "recovery_probabilities", 0), ["1", "2"]),
        changed(("contexts", 0, "growth_yields", 0), ["0", "1"]),
        changed(("contexts", 0, "endpoint_masses"), [[1, 1], [1, 1]]),
        changed(("contexts", 1, "name"), "A"),
        changed(("contexts",), []),
        changed(("contexts",), [context(str(i), (1, 1, 1)) for i in range(65)]),
        changed(("schema_version",), True),
        changed(("provenance",), "empirical_histogram"),
        changed(("assumptions", "representation"), "simplex_coordinate_share_bounds"),
    ]
    for key in ("population_expected_mass_model", "cartesian_parameter_bounds",
                "bounds_fixed_independently_of_selected_outcomes", "fixed_route_axis"):
        invalid.append(changed(("assumptions", key), False))
    for key in ("endpoint_count_law_claim", "coverage_or_power_claim"):
        invalid.append(changed(("assumptions", key), True))
    for value in (0, -1, True, 1.0, None):
        if value is not None:
            invalid.append(changed(("forecast_K",), value))
    absent = copy.deepcopy(cases["exact_growth_mimic"])
    del absent["contexts"][0]["supply_weights"]
    invalid.append(absent)
    unknown = copy.deepcopy(cases["exact_growth_mimic"])
    unknown["contexts"][0]["normalized_share_sum"] = 1
    invalid.append(unknown)
    del_assumption = copy.deepcopy(cases["exact_growth_mimic"])
    del del_assumption["assumptions"]["cartesian_parameter_bounds"]
    invalid.append(del_assumption)
    for data in invalid:
        try:
            engine.certify(data)
        except (ValueError, TypeError, RuntimeError):
            counts["invalid_input_guards"] = counts.get("invalid_input_guards", 0)+1
        else:
            raise RuntimeError("An inadmissible request produced a certificate")
    with tempfile.TemporaryDirectory(dir=BASE) as folder:
        folder = Path(folder)
        for text in ('{"a":1,"a":2}', '{"x":Infinity}', '{"x":NaN}'):
            path = folder/"invalid.json"
            path.write_text(text)
            try:
                engine.load_request(path)
            except ValueError:
                counts["json_ambiguity_guards"] = counts.get("json_ambiguity_guards", 0)+1
            else:
                raise RuntimeError("Ambiguous/nonfinite JSON admitted")
        output = folder/"no_output.json"
        process = subprocess.run([sys.executable, "-B", "-O", str(BASE/"curvature_bounds.py"),
            str(fixture_dir/"exact_growth_mimic.json"), "--output", str(output)],
            capture_output=True, text=True)
        check(process.returncode == 2 and not output.exists() and
              "without -O/-OO" in process.stderr, "optimized_engine_refusal")
        process = subprocess.run([sys.executable, "-B", "-O", str(BASE/"verify_producer.py")],
                                 capture_output=True, text=True)
        check(process.returncode != 0 and "without -O/-OO" in process.stderr,
              "optimized_producer_refusal")
        malformed = folder/"malformed.json"
        write_json(malformed, invalid[0])
        output.write_text("preserve-existing-output\n")
        process = subprocess.run([sys.executable, "-B", str(BASE/"curvature_bounds.py"),
                                  str(malformed), "--output", str(output)],
                                 capture_output=True, text=True)
        check(process.returncode == 2 and output.read_text() == "preserve-existing-output\n",
              "declined_request_does_not_overwrite_existing_file")
    receipt = {
        "record_id": "R000018", "status": "passed", "checks": counts,
        "total_checks": sum(counts.values()), "synthetic_cases": list(cases),
        "engine_sha256": hashlib.sha256((BASE/"curvature_bounds.py").read_bytes()).hexdigest(),
        "producer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "independent_review_status": "pending_root_oracle_review",
        "empirical_data_analyzed": False, "confidence_or_power_established": False,
        "scope": "producer checks of exact conditional synthetic feasibility",
    }
    write_json(BASE/"PRODUCER_RECEIPT.json", receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    verify()
