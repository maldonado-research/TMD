#!/usr/bin/env python3
"""Direct finite multinomial checks, synthetic fixtures and a plug-in failure."""
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction as F
from itertools import product
import hashlib
import json
from math import comb, prod
from pathlib import Path

from conditional_homogeneity import conditional_test, _strict_object, _reject_constant
from baseline_conditional_homogeneity import baseline_conditional_test

HERE = Path(__file__).resolve().parent
CHECKS = 0


def check(condition, label):
    global CHECKS
    if not condition:
        raise AssertionError(label)
    CHECKS += 1


def counts(n):
    return [(w, a, n-w-a) for w in range(n+1) for a in range(n-w+1)]


def mass(x, p):
    # Direct independent oracle uses combinatorial coefficients and normalized
    # multinomial probabilities, not the engine's nuisance-free weights.
    n = sum(x)
    return comb(n, x[0]) * comb(n-x[0], x[1]) * prod(v**k for v, k in zip(p, x))


def tilt(q, theta_exp, eta_exp):
    raw = (q[0]*eta_exp, q[1]*theta_exp, q[2]/eta_exp)
    return tuple(v/sum(raw) for v in raw)


def known_doc(xs, qs):
    return {
        "offset_contract": "fixed_known_positive_rational",
        "sampling_contract": "independent_multinomial_given_totals",
        "alpha": "1/20",
        "contexts": [{"id": f"c{i}", "counts": list(x), "q": list(map(str, q))} for i, (x, q) in enumerate(zip(xs, qs))],
    }


def baseline_doc(ks, xs):
    return {
        "observation_contract": "shared_positive_offset_within_context",
        "sampling_contract": "independent_baseline_selected_multinomials",
        "alpha": "1/20",
        "contexts": [{"id": f"c{i}", "baseline": list(k), "selected": list(x)} for i, (k, x) in enumerate(zip(ks, xs))],
    }


def direct_groups(ns, qs, theta_exp, eta_exps, ms=None):
    local = []
    for i, (n, q, eta) in enumerate(zip(ns, qs, eta_exps)):
        p = tilt(q, theta_exp, eta)
        if ms is None:
            local.append([(None, x, mass(x, p)) for x in counts(n)])
        else:
            local.append([(k, x, mass(k, q)*mass(x, p)) for k in counts(ms[i]) for x in counts(n)])
    grouped = defaultdict(list)
    for sample in product(*local):
        ks, xs, probabilities = zip(*sample)
        key = (tuple(x[0]-x[2] for x in xs), sum(x[1] for x in xs))
        if ms is not None:
            key += (tuple(tuple(a+b for a, b in zip(k, x)) for k, x in zip(ks, xs)),)
        grouped[key].append((ks, xs, prod(probabilities)))
    return grouped


def verify_groups(grouped, qs, with_baseline):
    total_mass = F(0)
    reject_mass = F(0)
    informative = 0
    states = 0
    max_support = 0
    for members in grouped.values():
        ks, xs, _ = members[0]
        doc = baseline_doc(ks, xs) if with_baseline else known_doc(xs, qs)
        result = (baseline_conditional_test if with_baseline else conditional_test)(doc, include_fiber=True)
        calculated = {tuple(row["A"]): F(row["probability"]) for row in result["fiber"]}
        group_mass = sum((entry[2] for entry in members), F(0))
        actual = {tuple(x[1] for x in item[1]): item[2]/group_mass for item in members}
        check(calculated == actual, "conditional law equals independently normalized multinomials")
        pvalues = {a: sum((z for z in actual.values() if z <= probability), F(0)) for a, probability in actual.items()}
        observed_a = tuple(x[1] for x in xs)
        check(F(result["p_value"]) == pvalues[observed_a], "reported p equals complete tied tail")
        for level in set(pvalues.values()):
            check(sum((actual[a] for a, p in pvalues.items() if p <= level), F(0)) <= level, "conditional superuniformity at each attained threshold")
        check(F(result["minimum_attainable_p"]) == min(pvalues.values()), "smallest attainable tail")
        reject_mass += group_mass * sum((actual[a] for a, p in pvalues.items() if p <= F(1,20)), F(0))
        total_mass += group_mass
        informative += len(members) > 1
        states += len(members)
        max_support = max(max_support, len(members))
    check(total_mass == 1, "complete unconditional probability is one")
    check(reject_mass <= F(1,20), "complete small-null size at alpha 1/20")
    return {"tables": states, "fibers": len(grouped), "informative_fibers": informative,
            "max_fiber_size": max_support, "rejection_probability": str(reject_mass)}


def plugin_counterexample():
    q = (F(1,3),)*3
    qhats = [tuple(F(2*(i==j)+1,5) for i in range(3)) for j in range(3)]
    rows = []
    mean_error = F(0)
    for estimates in product(qhats, repeat=2):
        error = F(0)
        for xs in product(counts(5), repeat=2):
            # Intentionally MISDECLARE the point estimate as known to demonstrate
            # the error from an inadmissible plug-in use. This is not validation
            # or admission of the known-offset input contract.
            result = conditional_test(known_doc(xs, estimates))
            if F(result["p_value"]) <= F(1,20):
                error += prod(mass(x, q) for x in xs)
        rows.append({"qhat": [list(map(str, v)) for v in estimates], "conditional_on_calibration_rejection_probability": str(error)})
        mean_error += error/9
    check(mean_error == F(30620,531441), "independent baseline plug-in counterexample exact value")
    check(mean_error > F(1,20), "independence does not restore known-offset level")
    return {"baseline_N_per_context": 1, "selected_N_per_context": 5, "contexts": 2,
            "true_q": ["1/3"]*3, "theta_exp": "1", "eta_exp": ["1","1"],
            "alpha": "1/20", "unconditional_rejection_probability": str(mean_error), "calibration_cases": rows}


def refusal_checks():
    q = (F(1,3),)*3
    good = known_doc(((2,2,2),(2,2,2)), (q,q))
    bad = []
    for value in (False, 0.05, "0.05", "0", "1"):
        item = deepcopy(good); item["alpha"] = value; bad.append(item)
    item = deepcopy(good); item["offset_contract"] = "independently_estimated"; bad.append(item)
    item = deepcopy(good); item["sampling_contract"] = "valid_marginals_only"; bad.append(item)
    item = deepcopy(good); item["contexts"][1]["id"] = "c0"; bad.append(item)
    for qbad in (["0","1/2","1/2"], [0.2,0.3,0.5], ["1/3"]*2, ["1/2"]*3):
        item = deepcopy(good); item["contexts"][0]["q"] = qbad; bad.append(item)
    for xbad in ([True,1,1], [-1,2,2], [1.0,2,2], [201,0,0]):
        item = deepcopy(good); item["contexts"][0]["counts"] = xbad; bad.append(item)
    item = known_doc(((50,100,50),)*4, (q,)*4); bad.append(item)
    huge = 2**240
    large_q = (F(1,huge),F(1,huge),F(huge-2,huge))
    item = known_doc(((10,20,10),)*3, (large_q,)*3); bad.append(item)
    for item in bad:
        try:
            conditional_test(item)
        except ValueError:
            check(True, "invalid known-offset input refused")
        else:
            check(False, "invalid known-offset input admitted")
    paired = baseline_doc(((2,2,2),(2,2,2)), ((2,2,2),(2,2,2)))
    bad_paired = []
    for key, value in (("observation_contract", "recovery_estimates_are_exact"), ("sampling_contract", "paired_correlated_runs")):
        item = deepcopy(paired); item[key] = value; bad_paired.append(item)
    item = deepcopy(paired); item["contexts"][0]["baseline"] = [False,1,1]; bad_paired.append(item)
    item = baseline_doc(((100,100,0),)*5, ((0,0,0),)*5); bad_paired.append(item)
    # Both arms permit a large support; bounded code must decline exhaustion.
    item = baseline_doc(((33,34,33),)*4, ((33,34,33),)*4); bad_paired.append(item)
    for item in bad_paired:
        try:
            baseline_conditional_test(item)
        except ValueError:
            check(True, "invalid baseline input refused")
        else:
            check(False, "invalid baseline input admitted")
    for text in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}'):
        try:
            json.loads(text, object_pairs_hook=_strict_object, parse_constant=_reject_constant)
        except ValueError:
            check(True, "ambiguous or nonstandard JSON refused")
        else:
            check(False, "invalid JSON admitted")
    return len(bad)+len(bad_paired)


def fixture_checks():
    q = (F(1,3),)*3
    known = known_doc(((6,0,6),(0,12,0)), (q,q))
    paired = baseline_doc(((4,4,4),(4,4,4)), ((6,0,6),(0,12,0)))
    for name, document, engine in (("known",known,conditional_test), ("baseline",paired,baseline_conditional_test)):
        result = engine(document, include_fiber=True)
        check(result["decision"] == "reject_shared_curvature", "synthetic strong departure")
        flipped = deepcopy(document)
        flipped["contexts"] = list(reversed(flipped["contexts"]))
        check(engine(flipped)["p_value"] == result["p_value"], "context order invariance")
        for row in flipped["contexts"]:
            for key in ("counts","q","baseline","selected"):
                if key in row:
                    row[key] = list(reversed(row[key]))
        check(engine(flipped)["p_value"] == result["p_value"], "W/M relabel invariance")
        (HERE/f"example_{name}.json").write_text(json.dumps(document, indent=2)+"\n")
        (HERE/f"example_{name}_result.json").write_text(json.dumps(result, indent=2)+"\n")
    for xs in (((0,0,0),), ((0,4,0),), ((3,0,0),(0,0,3)), ((1,1,0),(1,1,0))):
        result = conditional_test(known_doc(xs, (q,)*len(xs)))
        check(result["singleton_fiber"] and result["p_value"] == "1", "known singleton and parity cases")
    result = baseline_conditional_test(baseline_doc(((0,0,0),(0,0,0)), ((3,4,3),(3,4,3))))
    check(result["singleton_fiber"] and result["p_value"] == "1", "no baseline means no conditional information")
    tied = conditional_test(known_doc(((1,0,1),(0,2,0)), (q,q)), include_fiber=True)
    check(tied["fiber_size"] == 2 and tied["p_value"] == "1", "all equal probability allocations retain all ties")
    return {"known": json.loads((HERE/"example_known_result.json").read_text()), "baseline": json.loads((HERE/"example_baseline_result.json").read_text())}


def main():
    q3 = ((F(1,4),F(1,2),F(1,4)), (F(1,3),F(1,6),F(1,2)), (F(1,5),F(1,5),F(3,5)))
    known = []
    for theta, etas in ((F(2,3),(F(1,2),F(4,3),F(3,2))), (F(3,2),(F(3),F(2,5),F(5,4)))):
        known.append(verify_groups(direct_groups((4,5,3), q3, theta, etas), q3, False))
    uniform = ((F(1,3),)*3,)*2
    paired = []
    for n,m in ((5,1),(3,3),(4,4)):
        paired.append({"N_per_context": n, "M_per_context": m, **verify_groups(direct_groups((n,n), uniform, F(1), (F(1),F(1)), (m,m)), uniform, True)})
    heterogeneous = verify_groups(direct_groups((3,3), q3[:2], F(3,2), (F(2,3),F(4,3)), (3,3)), q3[:2], True)
    counterexample = plugin_counterexample()
    refusals = refusal_checks()
    examples = fixture_checks()
    result = {"status": "passed", "assertions": CHECKS, "known_offset_complete_nulls": known,
              "baseline_complete_uniform_nulls": paired, "baseline_heterogeneous_offset_and_tilt_null": heterogeneous,
              "plugin_counterexample": counterexample, "refusal_cases": refusals, "synthetic_examples": examples,
              "source_hashes": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (HERE/"conditional_homogeneity.py", HERE/"baseline_conditional_homogeneity.py", HERE/"verify_conditional.py")},
              "biological_fit": False, "study_registry_changed": False, "external_peer_review": False}
    (HERE/"VERIFICATION.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"status": result["status"], "assertions": CHECKS, "baseline_complete_uniform_nulls": paired,
                      "plugin_false_positive_probability": counterexample["unconditional_rejection_probability"],
                      "example_p_values": {k:v["p_value"] for k,v in examples.items()}}, indent=2))


if __name__ == "__main__":
    main()
