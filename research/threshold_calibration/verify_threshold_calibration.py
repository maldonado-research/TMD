#!/usr/bin/env python3
"""Exact bounded checks of maximum-threshold certificates on synthetic laws."""
from copy import deepcopy
from fractions import Fraction as F
import argparse
import hashlib
import json
from math import comb
from pathlib import Path
import tempfile

import threshold_calibration as extension

ROOT = Path(__file__).resolve().parent


def fixtures():
    contract = dict(extension.CONTRACT,
                    control_unit="synthetic independently truth-labelled Other unit",
                    control_population="one synthetic iid Other population",
                    score_definition="one scalar rational score from a fixed synthetic measurement pipeline")
    strict = {"rule": "strict_maximum", "provenance": "synthetic", "contract": contract,
              "gamma": "1/20", "control_summary": {"tested": 12, "maximum": 50}}
    planned = deepcopy(strict)
    planned["control_summary"] = {"tested": 59, "maximum": "3/2"}
    inclusive = deepcopy(strict)
    inclusive["rule"] = "inclusive_maximum"
    inclusive["control_summary"]["maximum_multiplicity"] = 1
    tied = deepcopy(inclusive)
    tied["control_summary"]["maximum_multiplicity"] = 12
    return {"strict_twelve": strict, "strict_fifty_nine": planned,
            "inclusive_unique_maximum": inclusive, "inclusive_all_tied": tied}


def cdf(n, k, p):
    """Independent exact binomial lower tail; no imported tail evaluator."""
    return sum((comb(n, j) * p**j * (1 - p)**(n - j) for j in range(k + 1)), F(0))


def failure_mass(law, n, endpoints, inclusive):
    """Enumerate joint maximum/tie-count outcomes under a finite iid law."""
    mass, total, below = F(0), F(0), F(0)
    for atom in law:
        tail = 1 - below if inclusive else 1 - below - atom
        for k in range(1, n + 1):
            probability = comb(n, k) * atom**k * below**(n - k)
            total += probability
            if tail > endpoints[k if inclusive else 0]:
                mass += probability
        below += atom
    assert total == below == 1
    return mass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=extension.DEFAULT_REPOSITORY)
    args = parser.parse_args()
    engine, cp = extension.load_engine(args.repository)
    checks = {"endpoint_certificates": 0, "finite_law_coverage_cases": 0,
              "input_refusals": 0, "dependency_refusals": 0, "counterexamples": 0}
    docs, results = fixtures(), {}
    for name, doc in docs.items():
        result = extension.calibrate(engine, cp, doc)
        raw = json.dumps(doc, indent=2, sort_keys=True) + "\n"
        result["input_sha256"] = hashlib.sha256(raw.encode()).hexdigest()
        (ROOT / ("example_" + name + ".json")).write_text(raw)
        (ROOT / ("example_" + name + "_result.json")).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        results[name] = result
    assert F(results["strict_twelve"]["control_false_gate_upper_exact"]) > F(1, 5)
    assert F(results["strict_fifty_nine"]["control_false_gate_upper_exact"]) < F(1, 20)
    assert results["inclusive_all_tied"]["control_false_gate_upper_exact"] == "1"
    assert F(results["inclusive_unique_maximum"]["control_false_gate_upper_exact"]) > F(results["strict_twelve"]["control_false_gate_upper_exact"])
    assert all(row["native_false_gate_upper"] is None for row in results.values())

    # Finite support includes ties, constant laws and concentrated atoms.
    laws = [(F(i, 8), F(j, 8), F(8 - i - j, 8))
            for i in range(9) for j in range(9 - i)]
    laws += [(F(1, 100), F(99, 100)), (F(97, 100), F(3, 100))]
    for gamma in (F(1, 20), F(1, 5), F(3, 4)):
        for n in range(1, 9):
            endpoints = [engine.certified_one_sided(cp, k, n, gamma, False)[0] for k in range(n + 1)]
            for k, upper in enumerate(endpoints):
                assert 0 <= upper <= 1
                assert upper == 1 if k == n else cdf(n, k, upper) <= gamma
                checks["endpoint_certificates"] += 1
            for law in laws:
                for inclusive in (False, True):
                    assert failure_mass(law, n, endpoints, inclusive) <= gamma
                    checks["finite_law_coverage_cases"] += 1
    # Strict-max root enclosure at operational boundary values, verified by
    # its exact scalar power rather than the preserved CP implementation.
    for n, gamma in ((12, F(1, 20)), (5000, F(1, 10**12)), (1, F(999999999999, 10**12))):
        upper = engine.certified_one_sided(cp, 0, n, gamma, False)[0]
        assert (1 - upper)**n <= gamma
        checks["endpoint_certificates"] += 1

    # Conditional planning arithmetic, not a recommendation for a native assay.
    assert F(19, 20)**59 <= F(1, 20) < F(19, 20)**58

    # Constant scores expose why CP(0,n) cannot calibrate an inclusive gate.
    strict_upper = F(results["strict_twelve"]["control_false_gate_upper_exact"])
    assert strict_upper < 1 and failure_mass((F(1),), 12, [strict_upper] * 13, True) == 1
    checks["counterexamples"] += 1
    # A calibration-trained score S_D(x)=0 on observed raw categories, 1
    # otherwise, on 100 equiprobable categories with n=2: every observed
    # maximum is zero, but future strict-pass probability is at least 98%.
    upper_two = engine.certified_one_sided(cp, 0, 2, F(1, 20), False)[0]
    assert F(49, 50) > upper_two
    checks["counterexamples"] += 1

    def refuses(call, label="input_refusals"):
        try:
            call()
        except (ValueError, TypeError, KeyError, OSError, ArithmeticError):
            checks[label] += 1
        else:
            raise AssertionError("Malformed input or dependency was accepted")

    for path, value in (
            (("rule",), "arbitrary_selected_threshold"), (("provenance",), ""),
            (("extra",), 0), (("gamma",), "0"), (("gamma",), "1"),
            (("gamma",), "1/1000000000001"), (("gamma",), 0.05),
            (("gamma",), True), (("gamma",), "1/0"),
            (("control_summary", "tested"), 0), (("control_summary", "tested"), True),
            (("control_summary", "tested"), 5001), (("control_summary", "tested"), 1.0),
            (("control_summary", "maximum"), 0.5), (("control_summary", "maximum"), True),
            (("control_summary", "maximum"), "1e2"), (("control_summary", "maximum"), "9" * 201),
            (("control_summary", "maximum"), 2**257),
            (("contract", "score_pipeline"), "trained_on_these_controls"),
            (("contract", "sampling"), "stopped_when_favorable"),
            (("contract", "control_unit"), " ")):
        doc = deepcopy(docs["strict_twelve"])
        at = doc
        for key in path[:-1]:
            at = at[key]
        at[path[-1]] = value
        refuses(lambda doc=doc: extension.calibrate(engine, cp, doc))
    for k in (0, 13, True, 1.0):
        doc = deepcopy(docs["inclusive_unique_maximum"])
        doc["control_summary"]["maximum_multiplicity"] = k
        refuses(lambda doc=doc: extension.calibrate(engine, cp, doc))
    doc = deepcopy(docs["inclusive_unique_maximum"])
    del doc["control_summary"]["maximum_multiplicity"]
    refuses(lambda: extension.calibrate(engine, cp, doc))
    for raw in ('{"a":1,"a":2}', '{"x":NaN}', '{"x":Infinity}', b" " * (engine.MAX_INPUT_BYTES + 1)):
        refuses(lambda raw=raw: engine.load_json(raw))

    with tempfile.TemporaryDirectory(prefix="threshold-pins-", dir=ROOT) as folder:
        repository = Path(folder)
        dep = repository / "research" / "classification_bounds"
        (dep / "sources").mkdir(parents=True)
        source = Path(args.repository) / "research" / "classification_bounds"
        (dep / "classification_bounds.py").write_bytes((source / "classification_bounds.py").read_bytes() + b"\n")
        refuses(lambda: extension.load_engine(repository), "dependency_refusals")
        (dep / "classification_bounds.py").write_bytes((source / "classification_bounds.py").read_bytes())
        (dep / "sources" / "boundary_confidence.py").write_bytes((source / "sources" / "boundary_confidence.py").read_bytes() + b"\n")
        refuses(lambda: extension.load_engine(repository), "dependency_refusals")

    receipt = {
        "status": "pass", "all_data_and_laws_synthetic": True, "checks": checks,
        "producer_sha256": hashlib.sha256((ROOT / "threshold_calibration.py").read_bytes()).hexdigest(),
        "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "classification_sha256": extension.CLASSIFICATION_SHA256, "CP_sha256": extension.CP_SHA256,
        "conditional_planning": {"epsilon_exact": "1/20", "gamma_exact": "1/20", "minimum_fixed_n": 59},
        "scope": "Bounded implementation checks and counterexamples; general guarantees rely on the README proofs and declared premises. No native validation or power study.",
    }
    (ROOT / "VERIFICATION.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
