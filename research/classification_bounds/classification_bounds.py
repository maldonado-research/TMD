#!/usr/bin/env python3
"""Wrong-label curvature bounds under a prequalified true-triad contract.

Exact rational population partial identification; conservative finite-count
projection using preserved, hash-checked certified CP scalar routines.
Copyright (c) 2026 Ricardo Maldonado. MIT.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROUTES = ("W", "A", "M")
LABELS = ROUTES + ("U",)
ARMS = ("baseline", "selected")
MAX_CONTEXTS = 64
MAX_TRIALS = 5000
MAX_CP_TRIAL_WORK = 60000
MAX_RATIONAL_BITS = 256
MAX_RATIONAL_TEXT = 200
MAX_INPUT_BYTES = 1024 * 1024
CP_SHA256 = "23feb7547d481fc4d361b25da28fe9d46d79be2f9fe66376f9c9ca85c069c79d"
ROOT = Path(__file__).resolve().parent
CONTRACT = {
    "cohort": "independently_prequalified_true_W_A_M_no_other_entrants",
    "observation": "one_W_A_M_U_label_per_unit_U_retained_in_denominator",
    "classifier": "arbitrary_column_stochastic_by_arm_and_context",
    "latent": "strictly_positive_W_A_M_probabilities",
}
COUNT_CONTRACT = {
    "endpoint_sampling": "fixed_denominators_valid_binomial_label_marginals",
    "control_sampling": "fixed_known_truth_denominators_valid_binomial_correct_call_marginals",
    "control_transport": "native_correct_call_probability_at_least_control_probability",
    "design": "contexts_endpoint_rules_and_error_allocation_fixed_before_outcomes",
}


def rational(value, label="value"):
    """Require exact JSON integer/string inputs, never binary-float assumptions."""
    # Fractions are trusted internal intermediates, whose exact divisions can
    # exceed the JSON input limit. JSON cannot encode a Fraction object.
    if isinstance(value, Fraction):
        return value
    if isinstance(value, bool) or not isinstance(value, (int, str, Fraction)):
        raise ValueError(f"{label} must be an exact integer or rational string")
    if isinstance(value, str) and (len(value) > MAX_RATIONAL_TEXT or not re.fullmatch(
            r"[+-]?(?:[0-9]+(?:/[+-]?[0-9]+)?|[0-9]+\.[0-9]+)", value)):
        raise ValueError(f"{label} must use a bounded integer, fraction or decimal token without exponents")
    if isinstance(value, int) and value.bit_length() > MAX_RATIONAL_BITS:
        raise ValueError(f"{label} exceeds the rational input bit limit")
    try:
        result = Fraction(value)
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        raise ValueError(f"{label} must be a finite rational") from exc
    if max(result.numerator.bit_length(), result.denominator.bit_length()) > MAX_RATIONAL_BITS:
        raise ValueError(f"{label} exceeds the rational input bit limit")
    return result


def probability(value, label="probability"):
    result = rational(value, label)
    if not 0 <= result <= 1:
        raise ValueError(f"{label} must lie in [0,1]")
    return result


def mapping(value, keys, label):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError(f"{label} requires exactly {','.join(keys)}")
    return value


def route_values(value, label):
    mapping(value, ROUTES, label)
    return tuple(probability(value[r], f"{label}.{r}") for r in ROUTES)


def count(value, label):
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= MAX_TRIALS:
        raise ValueError(f"{label} must be an explicit integer from 0 to {MAX_TRIALS}")
    return value


def point(values):
    return dict(zip(ROUTES, map(str, values)))


def endpoint(value, attained):
    return {"exact": None if value is None else str(value),
            "infinity": "positive" if value is None else None,
            "attained_in_positive_domain": bool(attained)}


def caps_from_bounds(observed_upper, correct_lower):
    o = route_values(observed_upper, "observed_upper")
    d = route_values(correct_lower, "correct_call_lower")
    return dict(zip(ROUTES, [min(Fraction(1), a / b) if b else Fraction(1)
                            for a, b in zip(o, d)]))


def capped_simplex_bounds(caps):
    """Sharp Q=A²/(WM) range over 0<p_i<=caps_i, sum p_i=1.

    Null upper means +infinity; zero/infinity are limits only. Boundary points
    certify closure endpoints and are never represented as positive biology.
    """
    w, a, m = u = route_values(caps, "caps")
    base = {"caps": point(u), "sum_caps_exact": str(sum(u)),
            "range_kind": "sharp_for_separate_unrestricted_classifiers"}
    if sum(u) < 1:
        return dict(base, status="empty_observation_contract_set",
                    reason="The supplied caps cannot sum to a latent probability law.")
    if not all(u):
        return dict(base, status="no_strictly_positive_latent_law",
                    reason="A zero cap forces a population boundary excluded by this target.")
    # u/sum(u) is strictly positive, within each cap, and sums to one.
    interior = tuple(x / sum(u) for x in u)
    amin = max(Fraction(0), 1 - w - m)
    smin = 1 - amin
    wlo, whi = max(Fraction(0), smin - m), min(w, smin)
    wmin = min(max(smin / 2, wlo), whi)
    lower_point = (wmin, amin, smin - wmin)
    lower = amin**2 / (wmin * (smin - wmin))
    smax = 1 - a
    if not smax:
        upper_point = (Fraction(0), a, Fraction(0))
        upper = None
    else:
        ends = (max(Fraction(0), smax - m), min(w, smax))
        wmax = min(ends, key=lambda x: x * (smax - x))
        upper_point = (wmax, a, smax - wmax)
        den = wmax * (smax - wmax)
        upper = a**2 / den if den else None
    return dict(base, status="ok", lower=endpoint(lower, lower > 0),
                upper=endpoint(upper, upper is not None),
                lower_closure_witness=point(lower_point),
                upper_closure_witness=point(upper_point),
                positive_feasible_witness=point(interior),
                boundary_approximation="(1-epsilon)*closure_witness + epsilon*positive_feasible_witness, 0<epsilon<1")


def complete_classifier(observed, correct_call_lower, latent):
    """Construct an exact 4-by-3 column-stochastic completion, including U."""
    mapping(observed, LABELS, "observed")
    o = tuple(probability(observed[r], "observed." + r) for r in LABELS)
    d = route_values(correct_call_lower, "correct_call_lower")
    p = route_values(latent, "latent")
    if sum(o) != 1 or sum(p) != 1:
        raise ValueError("Observed and latent probability vectors must each sum to one")
    residual = tuple(o[j] - d[j] * p[j] if j < 3 else o[j] for j in range(4))
    if any(x < 0 for x in residual):
        raise ValueError("Latent law violates a diagonal lower bound")
    total = sum(residual)
    z = tuple(x / total for x in residual) if total else (Fraction(0),) * 3 + (Fraction(1),)
    matrix = [[d[i] * int(j == i) + (1 - d[i]) * z[j] for i in range(3)] for j in range(4)]
    return {"row_order": list(LABELS), "column_order": list(ROUTES),
            "matrix_exact": [[str(x) for x in row] for row in matrix],
            "residual_mass_exact": str(total)}


def population_arm(observed, correct_call_lower):
    mapping(observed, LABELS, "observed")
    o = {r: probability(observed[r], "observed." + r) for r in LABELS}
    if sum(o.values()) != 1:
        raise ValueError("Unconditional W,A,M,U probabilities must sum exactly to one")
    caps = caps_from_bounds({r: o[r] for r in ROUTES}, correct_call_lower)
    result = capped_simplex_bounds(caps)
    result["observed_unconditional"] = {r: str(o[r]) for r in LABELS}
    result["correct_call_lower"] = point(route_values(correct_call_lower, "correct_call_lower"))
    if result["status"] == "ok":
        result["classifier_completions"] = {
            key: complete_classifier(o, correct_call_lower, {r: Fraction(v) for r, v in result[key].items()})
            for key in ("lower_closure_witness", "upper_closure_witness", "positive_feasible_witness")}
    return result


def ratio_interval(baseline, selected):
    """Range closure of J=Q(selected)/Q(baseline), with open-limit flags."""
    if baseline["status"] != "ok" or selected["status"] != "ok":
        return {"status": "unevaluable_observation_contract"}
    blo, slo = Fraction(baseline["lower"]["exact"]), Fraction(selected["lower"]["exact"])
    bhi = None if baseline["upper"]["exact"] is None else Fraction(baseline["upper"]["exact"])
    shi = None if selected["upper"]["exact"] is None else Fraction(selected["upper"]["exact"])
    lo = Fraction(0) if not slo or bhi is None else slo / bhi
    hi = None if not blo or shi is None else shi / blo
    return {"status": "ok", "lower": endpoint(lo, lo > 0), "upper": endpoint(hi, hi is not None)}


def common_intersection(intervals):
    if not intervals or any(x["status"] != "ok" for x in intervals):
        return {"status": "unevaluable_observation_contract", "separated": False,
                "reason": "Observation-contract incompatibility is not a curvature rejection."}
    lo = max(Fraction(x["lower"]["exact"]) for x in intervals)
    finite_hi = [Fraction(x["upper"]["exact"]) for x in intervals if x["upper"]["exact"] is not None]
    hi = min(finite_hi) if finite_hi else None
    separated = hi is not None and (lo > hi or (lo == hi and lo == 0))
    return {"status": "separated" if separated else "compatible",
            "separated": separated, "lower": endpoint(lo, lo > 0),
            "upper": endpoint(hi, hi is not None),
            "interpretation": "Overlap is compatibility under the declared model, not evidence that curvatures are equal."}


def validate_document(doc, mode):
    if not isinstance(doc, dict) or doc.get("mode") != mode:
        raise ValueError(f"mode must be {mode}")
    mapping(doc, ("mode", "provenance", "contract", "contexts", "alpha") if mode == "counts"
            else ("mode", "provenance", "contract", "contexts"), "document")
    contract = doc.get("contract")
    if not isinstance(contract, dict):
        raise ValueError("Explicit contract declarations are required")
    expected_keys = set(CONTRACT) | {"endpoint_unit"}
    if mode == "counts":
        expected_keys |= set(COUNT_CONTRACT) | {"known_truth_control_unit"}
    mapping(contract, expected_keys, "contract")
    for key, expected in dict(CONTRACT, **(COUNT_CONTRACT if mode == "counts" else {})).items():
        if contract.get(key) != expected:
            raise ValueError(f"contract.{key} must be {expected}")
    for key in ("endpoint_unit", "known_truth_control_unit") if mode == "counts" else ("endpoint_unit",):
        if not isinstance(contract.get(key), str) or not contract[key].strip():
            raise ValueError(f"contract.{key} must name the actual unit")
    if doc.get("provenance") not in ("synthetic", "observed", "literature_transcription"):
        raise ValueError("Explicit provenance is required")
    rows = doc.get("contexts")
    if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_CONTEXTS:
        raise ValueError(f"One to {MAX_CONTEXTS} contexts are required")
    names = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"].strip():
            raise ValueError("Context identifiers must be nonempty strings")
        mapping(row, ("id",) + ARMS, "context")
        names.append(row["id"])
        for arm in ARMS:
            if not isinstance(row.get(arm), dict):
                raise ValueError(f"Context {row['id']} requires an explicit {arm} object")
    if len(set(names)) != len(names):
        raise ValueError("Context identifiers must be unique")
    return rows


def result_document(doc, contexts):
    return {"schema_version": "classification-bounds-1", "mode": doc["mode"],
            "provenance": doc["provenance"], "contract": doc["contract"],
            "contracts_are_assertions_not_programmatically_established": True,
            "target": "J=Q(selected)/Q(baseline), Q(p)=pA^2/(pW*pM)",
            "contexts": contexts,
            "common_J": common_intersection([row["J"] for row in contexts]),
            "shared_classifier_sharpness_claimed": False}


def population_bounds(doc):
    rows = validate_document(doc, "population")
    contexts = []
    for row in rows:
        out = {"id": row["id"]}
        for arm in ARMS:
            item = row[arm]
            mapping(item, ("observed", "correct_call_lower"), arm)
            out[arm] = population_arm(item["observed"], item["correct_call_lower"])
        out["J"] = ratio_interval(out["baseline"], out["selected"])
        contexts.append(out)
    result = result_document(doc, contexts)
    result["interpretation"] = "Population partial identification, without a sampling confidence claim."
    return result


def load_cp():
    path = ROOT / "sources" / "boundary_confidence.py"
    if hashlib.sha256(path.read_bytes()).hexdigest() != CP_SHA256:
        raise ValueError("Preserved confidence source hash mismatch")
    spec = importlib.util.spec_from_file_location("preserved_boundary_confidence", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def certified_one_sided(cp, k, n, tail, lower):
    if not n or (lower and not k) or (not lower and k == n):
        val = Fraction(0 if lower else 1)
        cert = {"support_boundary": True, "no_observations": n == 0}
    else:
        value, cert = cp.certified_outer_endpoint(n, k, tail, upper=lower)
        val = Fraction.from_float(value)
    return val, {"exact": str(val), "certificate": cert}


def count_bounds(doc):
    rows = validate_document(doc, "counts")
    alpha = rational(doc.get("alpha"), "alpha")
    if not Fraction(1, 10**12) <= alpha < 1:
        raise ValueError("alpha must be at least 1e-12 and below one")
    # Per context: 2 arms x 3 labels x (observed UCB + correct-call LCB).
    allocations = 12 * len(rows)
    tail = alpha / allocations
    trial_work = 0
    # Validate the full count frame and bound expensive exact-tail work before
    # executing any confidence calculation. This is an operational guard, not
    # a general wall-clock performance guarantee.
    for row in rows:
        for arm in ARMS:
            item = row[arm]
            mapping(item, ("observed_counts", "known_truth_controls"), arm)
            mapping(item["observed_counts"], LABELS, arm + ".observed_counts")
            total = count(sum(count(item["observed_counts"][r], arm + "." + r) for r in LABELS), arm + ".total")
            trial_work += 3 * total
            mapping(item["known_truth_controls"], ROUTES, arm + ".known_truth_controls")
            for r in ROUTES:
                control = item["known_truth_controls"][r]
                mapping(control, ("introduced", "correct"), arm + ".controls." + r)
                n = count(control["introduced"], arm + ".introduced." + r)
                k = count(control["correct"], arm + ".correct." + r)
                if k > n:
                    raise ValueError("Correct calls cannot exceed known introduced units")
                trial_work += n
    if trial_work > MAX_CP_TRIAL_WORK:
        raise ValueError(f"Total CP trial work exceeds prototype limit {MAX_CP_TRIAL_WORK}")
    cp = load_cp()
    contexts = []
    for row in rows:
        out = {"id": row["id"]}
        for arm in ARMS:
            item = row[arm]
            mapping(item, ("observed_counts", "known_truth_controls"), arm)
            mapping(item["observed_counts"], LABELS, arm + ".observed_counts")
            obs = {r: count(item["observed_counts"][r], arm + "." + r) for r in LABELS}
            total = count(sum(obs.values()), arm + ".total")
            mapping(item["known_truth_controls"], ROUTES, arm + ".known_truth_controls")
            upper, lower, limits = {}, {}, {}
            for r in ROUTES:
                control = item["known_truth_controls"][r]
                mapping(control, ("introduced", "correct"), arm + ".controls." + r)
                n = count(control["introduced"], arm + ".introduced." + r)
                k = count(control["correct"], arm + ".correct." + r)
                if k > n:
                    raise ValueError("Correct calls cannot exceed known introduced units")
                upper[r], ocert = certified_one_sided(cp, obs[r], total, tail, lower=False)
                lower[r], dcert = certified_one_sided(cp, k, n, tail, lower=True)
                limits[r] = {"observed_upper": ocert, "correct_call_lower": dcert,
                             "observed_successes": obs[r], "observed_trials": total,
                             "control_successes": k, "control_trials": n}
            bounds = capped_simplex_bounds(caps_from_bounds(upper, lower))
            bounds["range_kind"] = "conservative_count_confidence_outer_projection"
            bounds["closure_witness_scope"] = "Cap outer set only; not a claim to satisfy the full joint count-confidence region."
            bounds["marginal_limits"] = limits
            out[arm] = bounds
        out["J"] = ratio_interval(out["baseline"], out["selected"])
        contexts.append(out)
    result = result_document(doc, contexts)
    if result["common_J"]["status"] == "compatible":
        result["common_J"]["status"] = "not_rejected"
        result["common_J"]["interpretation"] = ("The conservative outer intervals overlap; this does not establish "
                                                  "feasibility under fuller confidence or shared-classifier constraints.")
    result["confidence"] = {
        "alpha_exact": str(alpha), "simultaneous_coverage_at_least_exact": str(1 - alpha),
        "one_sided_allocations": allocations, "per_endpoint_error_exact": str(tail),
        "between_cell_independence_required": False,
        "preserved_scalar_CP_sha256": CP_SHA256,
        "finite_count_projection_claimed_sharp": False,
        "control_transport_error_included": False,
        "CP_trial_work": trial_work,
    }
    result["reject_common_J"] = len(rows) >= 2 and result["common_J"]["separated"]
    result["decision_scope"] = ("Finite-sample level-alpha common-curvature test under declared fixed-design/count/transport contracts. "
                                "One context is descriptive. Observation-contract incompatibility is unevaluable.")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        raw = args.input.read_bytes()
        doc = load_json(raw)
        mode = doc.get("mode") if isinstance(doc, dict) else None
        if mode not in ("population", "counts"):
            raise ValueError("mode must be population or counts")
        result = population_bounds(doc) if mode == "population" else count_bounds(doc)
        result["input_sha256"] = hashlib.sha256(raw).hexdigest()
        rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.write_text(rendered)
        else:
            print(rendered, end="")
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, f"Invalid input: {exc}\n")


def load_json(raw):
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError("Input exceeds the one-MiB prototype limit")
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    def constant(value):
        raise ValueError(f"Nonfinite JSON token is forbidden: {value}")
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


if __name__ == "__main__":
    main()
