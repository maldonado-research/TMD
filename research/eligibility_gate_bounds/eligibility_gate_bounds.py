#!/usr/bin/env python3
"""Calibrated full-cohort eligibility lower bound and conservative Q/J projection.

Original TMD extension; standard library only. Copyright (c) 2026 Ricardo
Maldonado. MIT. The classification and certified CP dependencies are hash pinned.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
DEFAULT_REPOSITORY = ROOT.parent.parent
CLASSIFICATION_SHA256 = "66996adfd4f90bccf7315a82022d6b96d390378f4be781f992e7229058bfb368"
CP_SHA256 = "23feb7547d481fc4d361b25da28fe9d46d79be2f9fe66376f9c9ca85c069c79d"
CONTRACT = {
    "cohort": "full_cohort_before_gate_selection_true_W_A_M_or_Other",
    "eligibility": "frozen_independent_truth_definition_W_A_M_versus_Other",
    "gate": "binary_gate_on_full_cohort_same_rule_in_native_and_Other_controls",
}
COUNT_CONTRACT = {
    "observation": "one_W_A_M_U_label_per_full_cohort_unit_U_retained",
    "target": "strictly_positive_W_A_M_composition_conditional_on_true_eligibility_T_positive",
    "classifier": "arbitrary_column_stochastic_by_arm_and_context_unrestricted_Other_column",
    "endpoint_sampling": "same_full_cohort_units_fixed_denominator_valid_binomial_label_and_gate_marginals",
    "control_sampling": "fixed_known_truth_denominators_valid_binomial_correct_call_and_Other_false_gate_marginals",
    "correct_call_transport": "native_eligible_correct_call_probability_at_least_true_route_control_probability",
    "false_gate_transport": "native_Other_gate_positive_probability_at_most_known_Other_control_probability",
    "design": "contexts_endpoint_gate_rules_and_error_allocation_fixed_before_outcomes",
}


def load_engine(repository=DEFAULT_REPOSITORY):
    """Reuse unchanged project routines, refusing unexpected source bytes."""
    path = Path(repository) / "research" / "classification_bounds" / "classification_bounds.py"
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != CLASSIFICATION_SHA256:
        raise ValueError("Classification dependency hash mismatch")
    # Keep the original project tree read-only, including __pycache__ files.
    saved = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location("pinned_classification_bounds", path)
        engine = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(engine)
        if engine.CP_SHA256 != CP_SHA256:
            raise ValueError("Certified CP dependency declaration mismatch")
        cp = engine.load_cp()
    finally:
        sys.dont_write_bytecode = saved
    return engine, cp


def gate_bound(engine, gate_positive_lower, other_false_gate_upper):
    """Sharp marginal T lower bound; zero is an infimum when T must be positive."""
    g = engine.probability(gate_positive_lower, "gate_positive_lower")
    f = engine.probability(other_false_gate_upper, "other_false_gate_upper")
    beta = max(Fraction(0), (g - f) / (1 - f)) if f < 1 else Fraction(0)
    # With beta=0, this certifies only a closed-model endpoint; p is undefined
    # at T=0. The stated positive-T sequence below supplies the sharp infimum.
    witness = {"T": str(beta), "a": "1" if beta else str(g),
               "f": str(f) if beta else str(g), "g": str(g)}
    return {
        "eligible_fraction_lower_exact": str(beta),
        "gate_positive_lower_exact": str(g), "other_false_gate_upper_exact": str(f),
        "informative": bool(beta), "sharpness_scope": "gate_marginals_only",
        "lower_attained_for_positive_T": bool(beta),
        "closed_model_witness": witness,
        "positive_T_approach_if_zero": None if beta else "T=epsilon, a=f=gL, 0<epsilon<=1; g=gL",
        "witness_scope": "Gate mixture only; no joint gate/classifier feasibility certificate.",
        "target": "T=P(true_W_A_M_in_full_cohort); not gate_positive_PPV or retained_label_fraction",
    }


def eligibility_caps(engine, observed_upper, correct_call_lower, beta):
    beta = engine.probability(beta, "eligible_fraction_lower")
    # Multiplication first preserves the certified endpoints as exact rationals.
    lower = engine.route_values(correct_call_lower, "correct_call_lower")
    return engine.caps_from_bounds(observed_upper, dict(zip(engine.ROUTES, (beta * x for x in lower))))


def validate_contract(engine, doc, mode):
    expected = dict(CONTRACT, **(COUNT_CONTRACT if mode == "counts" else {}))
    unit_keys = ("endpoint_unit", "true_route_control_unit", "known_Other_control_unit") if mode == "counts" else ("endpoint_unit",)
    engine.mapping(doc.get("contract"), tuple(expected) + unit_keys, "contract")
    for key, value in expected.items():
        if doc["contract"][key] != value:
            raise ValueError(f"contract.{key} must be {value}")
    for key in unit_keys:
        if not isinstance(doc["contract"][key], str) or not doc["contract"][key].strip():
            raise ValueError(f"contract.{key} must name the actual unit")
    if doc.get("provenance") not in ("synthetic", "observed", "literature_transcription"):
        raise ValueError("Explicit provenance is required")


def result_header(doc):
    return {
        "schema_version": "eligibility-gate-bounds-1", "mode": doc["mode"],
        "provenance": doc["provenance"], "contract": doc["contract"],
        "contracts_are_assertions_not_programmatically_established": True,
        "dependencies": {"classification_SHA256": CLASSIFICATION_SHA256, "certified_CP_SHA256": CP_SHA256},
        "joint_gate_classifier_sharpness_claimed": False,
    }


def population_gate_bounds(engine, doc):
    engine.mapping(doc, ("mode", "provenance", "contract", "gate_positive_lower", "other_false_gate_upper"), "document")
    if doc["mode"] != "gate":
        raise ValueError("mode must be gate")
    validate_contract(engine, doc, "gate")
    result = result_header(doc)
    result["eligibility"] = gate_bound(engine, doc["gate_positive_lower"], doc["other_false_gate_upper"])
    result["interpretation"] = "Population gate marginal calculation only, without a confidence or joint Q feasibility claim."
    return result


def validate_counts(engine, doc):
    """Validate all inputs and work limits before doing confidence calculations."""
    engine.mapping(doc, ("mode", "provenance", "contract", "alpha", "contexts"), "document")
    if doc["mode"] != "counts":
        raise ValueError("mode must be counts")
    validate_contract(engine, doc, "counts")
    alpha = engine.rational(doc["alpha"], "alpha")
    if not Fraction(1, 10**12) <= alpha < 1:
        raise ValueError("alpha must be at least 1e-12 and below one")
    rows = doc["contexts"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= engine.MAX_CONTEXTS:
        raise ValueError(f"One to {engine.MAX_CONTEXTS} contexts are required")
    names, work = [], 0
    for row in rows:
        engine.mapping(row, ("id",) + engine.ARMS, "context")
        if not isinstance(row["id"], str) or not row["id"].strip():
            raise ValueError("Context identifiers must be nonempty strings")
        names.append(row["id"])
        for arm in engine.ARMS:
            item = row[arm]
            engine.mapping(item, ("observed_counts", "known_truth_controls", "gate_counts", "known_Other_controls"), arm)
            engine.mapping(item["observed_counts"], engine.LABELS, arm + ".observed_counts")
            total = engine.count(sum(engine.count(item["observed_counts"][r], arm + "." + r) for r in engine.LABELS), arm + ".total")
            work += 3 * total
            engine.mapping(item["known_truth_controls"], engine.ROUTES, arm + ".known_truth_controls")
            for route in engine.ROUTES:
                ctl = item["known_truth_controls"][route]
                engine.mapping(ctl, ("introduced", "correct"), arm + ".controls." + route)
                n = engine.count(ctl["introduced"], arm + ".introduced." + route)
                k = engine.count(ctl["correct"], arm + ".correct." + route)
                if k > n:
                    raise ValueError("Correct calls cannot exceed known introduced units")
                work += n
            for key in ("gate_counts", "known_Other_controls"):
                engine.mapping(item[key], ("tested", "positive"), arm + "." + key)
                n = engine.count(item[key]["tested"], arm + "." + key + ".tested")
                k = engine.count(item[key]["positive"], arm + "." + key + ".positive")
                if k > n:
                    raise ValueError("Gate positives cannot exceed tested units")
                if key == "gate_counts" and n != total:
                    raise ValueError("Gate tested count must equal the full W/A/M/U cohort denominator")
                work += n
    if len(set(names)) != len(names):
        raise ValueError("Context identifiers must be unique")
    if work > engine.MAX_CP_TRIAL_WORK:
        raise ValueError(f"Total CP trial work exceeds prototype limit {engine.MAX_CP_TRIAL_WORK}")
    return rows, alpha, work


def count_bounds(engine, cp, doc):
    rows, alpha, work = validate_counts(engine, doc)
    allocations = 16 * len(rows)  # 2 arms x (3 label UCB + 3 correct LCB + g LCB + f UCB).
    tail = alpha / allocations
    contexts = []
    for row in rows:
        out = {"id": row["id"]}
        for arm in engine.ARMS:
            item = row[arm]
            obs = item["observed_counts"]
            total = sum(obs.values())
            upper, lower, limits = {}, {}, {}
            for route in engine.ROUTES:
                control = item["known_truth_controls"][route]
                n, k = control["introduced"], control["correct"]
                upper[route], ocert = engine.certified_one_sided(cp, obs[route], total, tail, lower=False)
                lower[route], dcert = engine.certified_one_sided(cp, k, n, tail, lower=True)
                limits[route] = {"observed_upper": ocert, "correct_call_lower": dcert,
                                 "observed_successes": obs[route], "observed_trials": total,
                                 "control_successes": k, "control_trials": n}
            gate, other = item["gate_counts"], item["known_Other_controls"]
            gl, gcert = engine.certified_one_sided(cp, gate["positive"], gate["tested"], tail, lower=True)
            fu, fcert = engine.certified_one_sided(cp, other["positive"], other["tested"], tail, lower=False)
            eligibility = gate_bound(engine, gl, fu)
            beta = Fraction(eligibility["eligible_fraction_lower_exact"])
            bounds = engine.capped_simplex_bounds(eligibility_caps(engine, upper, lower, beta))
            bounds["range_kind"] = "conservative_count_confidence_outer_projection_with_eligibility_lower_bound"
            bounds["closure_witness_scope"] = "Cap outer set only; no full gate/classifier/count-confidence feasibility certificate."
            bounds["eligibility"] = eligibility
            bounds["marginal_limits"] = limits
            bounds["gate_limits"] = {
                "gate_positive_lower": gcert, "other_false_gate_upper": fcert,
                "gate_positive_successes": gate["positive"], "gate_trials": gate["tested"],
                "Other_positive_successes": other["positive"], "Other_trials": other["tested"],
            }
            out[arm] = bounds
        out["J"] = engine.ratio_interval(out["baseline"], out["selected"])
        contexts.append(out)
    result = result_header(doc)
    result["target"] = "J=Q(selected)/Q(baseline), Q(p)=pA^2/(pW*pM); p conditional on true full-cohort eligibility"
    result["contexts"] = contexts
    result["common_J"] = engine.common_intersection([row["J"] for row in contexts])
    if result["common_J"]["status"] == "compatible":
        result["common_J"].update(status="not_rejected", interpretation="Conservative outer intervals overlap; full joint feasibility or equal biological curvature is not established.")
    result["confidence"] = {
        "alpha_exact": str(alpha), "simultaneous_coverage_at_least_exact": str(1 - alpha),
        "one_sided_allocations": allocations, "per_endpoint_error_exact": str(tail),
        "between_component_independence_required": False, "finite_count_projection_claimed_sharp": False,
        "control_transport_error_included": False, "CP_trial_work": work,
    }
    result["reject_common_J"] = len(rows) >= 2 and result["common_J"]["separated"]
    result["decision_scope"] = "Finite-sample level-alpha test under the declared count, truth and transport premises. One context is descriptive; an incompatible cap set is unevaluable."
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--repository", type=Path, default=DEFAULT_REPOSITORY,
                        help="TMD repository containing the pinned classification_bounds dependency")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        engine, cp = load_engine(args.repository)
        # Bound the read itself, as well as the strict JSON parser's input.
        with args.input.open("rb") as source:
            raw = source.read(engine.MAX_INPUT_BYTES + 1)
        doc = engine.load_json(raw)
        mode = doc.get("mode") if isinstance(doc, dict) else None
        if mode == "gate":
            result = population_gate_bounds(engine, doc)
        elif mode == "counts":
            result = count_bounds(engine, cp, doc)
        else:
            raise ValueError("mode must be gate or counts")
        result["input_sha256"] = hashlib.sha256(raw).hexdigest()
        rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.write_text(rendered)
        else:
            print(rendered, end="")
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, f"Invalid input: {exc}\n")


if __name__ == "__main__":
    main()
