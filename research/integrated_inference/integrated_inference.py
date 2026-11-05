#!/usr/bin/env python3
"""One prespecified error budget from maximum calibration through common J.

Thin standard-library integration of unchanged, hash-pinned TMD routines.
Copyright (c) 2026 Ricardo Maldonado. MIT.
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
PINS = {
    "threshold_calibration": ("research/threshold_calibration/threshold_calibration.py", "4256ca07cdd4d6e597c4ed2eda28926917e428391aa05710b2f5b962eb616c0b"),
    "eligibility_gate_bounds": ("research/eligibility_gate_bounds/eligibility_gate_bounds.py", "5c5645e83b3f38ecfb8e196bb5332a555ef752ffab42d4315b6ce7ebbf5d2f6f"),
    "classification_bounds": ("research/classification_bounds/classification_bounds.py", "66996adfd4f90bccf7315a82022d6b96d390378f4be781f992e7229058bfb368"),
    "certified_CP": ("research/classification_bounds/sources/boundary_confidence.py", "23feb7547d481fc4d361b25da28fe9d46d79be2f9fe66376f9c9ca85c069c79d"),
}
CONTRACT = {
    "cohort": "full_cohort_before_gate_selection_true_W_A_M_or_Other",
    "eligibility": "frozen_independent_truth_definition_W_A_M_versus_Other",
    "observation": "one_W_A_M_U_label_per_full_cohort_unit_gate_failures_and_unresolved_retained_as_U",
    "target": "strictly_positive_W_A_M_composition_conditional_on_true_eligibility_T_positive",
    "classifier": "arbitrary_by_arm_and_context_unrestricted_Other_column",
    "endpoint_sampling": "conditional_on_all_training_and_calibration_fixed_denominator_binomial_label_and_gate_marginals",
    "control_sampling": "conditional_on_all_training_and_calibration_fixed_known_truth_denominator_binomial_correct_call_marginals",
    "correct_call_pipeline": "full_learned_gate_and_label_pipeline_frozen_before_future_truth_control_evaluation",
    "correct_call_transport": "native_eligible_correct_call_probability_at_least_true_route_control_probability_for_each_frozen_pipeline",
    "false_gate_transport": "native_Other_tail_at_most_calibration_control_tail_pointwise_at_every_possible_learned_threshold",
    "training": "calibration_score_laws_iid_conditional_on_independent_training_for_each_training_result",
    "design": "all_contexts_denominators_rules_pipeline_definitions_alpha_and_budget_share_fixed_before_calibration",
    "chronology": "all_training_and_calibration_complete_then_freeze_then_independent_future_cohort_and_truth_controls",
}
DESCRIPTIONS = ("endpoint_unit", "true_route_control_unit", "conditional_sampling_justification")
PROVENANCE_KEYS = ("calibration_record", "future_cohort_record", "truth_control_record", "frozen_pipeline_record")


def load_dependencies(repository=DEFAULT_REPOSITORY):
    """Check every source before import; do not write bytecode in the repository."""
    paths = {}
    for name, (relative, expected) in PINS.items():
        path = Path(repository) / relative
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"{name} dependency hash mismatch")
        paths[name] = path
    saved, modules = sys.dont_write_bytecode, {}
    sys.dont_write_bytecode = True
    try:
        for name in ("threshold_calibration", "eligibility_gate_bounds", "classification_bounds"):
            spec = importlib.util.spec_from_file_location("integrated_pinned_" + name, paths[name])
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            modules[name] = module
        engine = modules["classification_bounds"]
        for name in ("threshold_calibration", "eligibility_gate_bounds"):
            if (modules[name].CLASSIFICATION_SHA256 != PINS["classification_bounds"][1]
                    or modules[name].CP_SHA256 != PINS["certified_CP"][1]):
                raise ValueError("Dependency declaration mismatch")
        if engine.CP_SHA256 != PINS["certified_CP"][1]:
            raise ValueError("Certified CP declaration mismatch")
        cp = engine.load_cp()
    finally:
        sys.dont_write_bytecode = saved
    return engine, cp, modules["threshold_calibration"], modules["eligibility_gate_bounds"]


def canonical_digest(plan):
    raw = json.dumps(plan, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip() or len(value) > 4096:
        raise ValueError(f"{label} must be a nonempty string of at most 4096 characters")


def validate_plan(engine, threshold, plan):
    engine.mapping(plan, ("schema_version", "alpha", "calibration_error_share", "contract", "contexts"), "plan")
    if plan["schema_version"] != "integrated-plan-1":
        raise ValueError("Unsupported plan schema")
    engine.mapping(plan["contract"], tuple(CONTRACT) + DESCRIPTIONS, "plan.contract")
    for key, expected in CONTRACT.items():
        if plan["contract"][key] != expected:
            raise ValueError(f"plan.contract.{key} must be {expected}")
    for key in DESCRIPTIONS:
        nonempty(plan["contract"][key], "plan.contract." + key)
    alpha = engine.probability(plan["alpha"], "alpha")
    share = engine.probability(plan["calibration_error_share"], "calibration_error_share")
    if not 0 < alpha < 1 or not 0 < share < 1:
        raise ValueError("alpha and calibration_error_share must lie strictly between zero and one")
    rows = plan["contexts"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= engine.MAX_CONTEXTS:
        raise ValueError(f"One to {engine.MAX_CONTEXTS} planned contexts required")
    gamma, eta = alpha * share / (2 * len(rows)), alpha * (1 - share) / (14 * len(rows))
    # Match the bounded numerical domain of the threshold utility. The stricter
    # per-component floor also prevents arbitrarily tiny future-count tails.
    if min(gamma, eta) < Fraction(1, 10**12):
        raise ValueError("Each derived component error must be at least 1e-12")
    names, work = [], 0
    for row in rows:
        engine.mapping(row, ("id",) + engine.ARMS, "planned context")
        nonempty(row["id"], "context.id")
        names.append(row["id"])
        for arm in engine.ARMS:
            item = engine.mapping(row[arm], ("pipeline_id", "calibration", "future_cohort_tested", "true_route_control_introduced"), arm)
            nonempty(item["pipeline_id"], arm + ".pipeline_id")
            cal = engine.mapping(item["calibration"], ("rule", "tested", "contract"), arm + ".calibration")
            # Validate a symbolic maximum using the pinned threshold schema;
            # the actual maximum belongs only in the later observation record.
            summary = {"tested": cal["tested"], "maximum": 0}
            if cal["rule"] == "inclusive_maximum":
                summary["maximum_multiplicity"] = 1
            threshold.validate(engine, {"rule": cal["rule"], "provenance": "synthetic", "contract": cal["contract"],
                                        "gamma": gamma, "control_summary": summary})
            n = engine.count(item["future_cohort_tested"], arm + ".future_cohort_tested")
            ctl = engine.mapping(item["true_route_control_introduced"], engine.ROUTES, arm + ".true_route_control_introduced")
            work += cal["tested"] + 4 * n
            work += sum(engine.count(ctl[r], arm + ".true_route_control_introduced." + r) for r in engine.ROUTES)
    if len(set(names)) != len(names):
        raise ValueError("Planned context identifiers must be unique")
    if work > engine.MAX_CP_TRIAL_WORK:
        raise ValueError(f"Total CP trial work exceeds prototype limit {engine.MAX_CP_TRIAL_WORK}")
    return {"alpha_exact": str(alpha), "calibration_error_share_exact": str(share),
            "calibration_family_error_exact": str(alpha * share), "count_family_error_exact": str(alpha * (1 - share)),
            "calibration_components": 2 * len(rows), "per_calibration_error_exact": str(gamma),
            "count_components": 14 * len(rows), "per_count_endpoint_error_exact": str(eta),
            "global_error_bound_exact": str(2 * len(rows) * gamma + 14 * len(rows) * eta),
            "simultaneous_coverage_at_least_exact": str(1 - alpha), "CP_trial_work": work}


def validate_records(engine, threshold, plan, records, allocation):
    engine.mapping(records, ("schema_version", "provenance", "plan_sha256", "contexts"), "observations")
    if records["schema_version"] != "integrated-observations-1":
        raise ValueError("Unsupported observation schema")
    if records["provenance"] not in ("synthetic", "observed", "literature_transcription"):
        raise ValueError("Explicit observation provenance required")
    if records["plan_sha256"] != canonical_digest(plan):
        raise ValueError("Observation plan hash mismatch")
    rows = records["contexts"]
    if not isinstance(rows, list) or len(rows) != len(plan["contexts"]):
        raise ValueError("Observation contexts must match the full planned family")
    for planned, row in zip(plan["contexts"], rows):
        engine.mapping(row, ("id",) + engine.ARMS, "observed context")
        if row["id"] != planned["id"]:
            raise ValueError("Observed contexts must follow the complete planned context order")
        for arm in engine.ARMS:
            fixed = planned[arm]
            item = engine.mapping(row[arm], ("pipeline_id", "calibration_summary", "observed_counts", "gate_counts", "known_truth_controls", "provenance"), arm)
            if item["pipeline_id"] != fixed["pipeline_id"]:
                raise ValueError("Frozen pipeline identifier differs from plan")
            engine.mapping(item["provenance"], PROVENANCE_KEYS, arm + ".provenance")
            for key in PROVENANCE_KEYS:
                nonempty(item["provenance"][key], arm + ".provenance." + key)
            cal = fixed["calibration"]
            threshold.validate(engine, {"rule": cal["rule"], "provenance": records["provenance"], "contract": cal["contract"],
                                        "gamma": allocation["per_calibration_error_exact"], "control_summary": item["calibration_summary"]})
            if item["calibration_summary"]["tested"] != cal["tested"]:
                raise ValueError("Observed calibration denominator differs from plan")
            observed = engine.mapping(item["observed_counts"], engine.LABELS, arm + ".observed_counts")
            total = sum(engine.count(observed[r], arm + "." + r) for r in engine.LABELS)
            if total != fixed["future_cohort_tested"]:
                raise ValueError("W/A/M/U counts must retain the entire planned future cohort")
            gate = engine.mapping(item["gate_counts"], ("tested", "positive"), arm + ".gate_counts")
            gn, gk = (engine.count(gate[k], arm + ".gate_counts." + k) for k in ("tested", "positive"))
            if gn != total or gk > gn:
                raise ValueError("Gate and label counts must use the same full cohort denominator")
            if sum(observed[r] for r in engine.ROUTES) > gk:
                raise ValueError("Every gate failure must remain U; non-U labels cannot exceed gate positives")
            controls = engine.mapping(item["known_truth_controls"], engine.ROUTES, arm + ".known_truth_controls")
            for route in engine.ROUTES:
                ctl = engine.mapping(controls[route], ("introduced", "correct"), arm + ".controls." + route)
                n, k = (engine.count(ctl[key], arm + ".controls." + route + "." + key) for key in ("introduced", "correct"))
                if n != fixed["true_route_control_introduced"][route] or k > n:
                    raise ValueError("True-route control counts violate the planned denominator")
    return rows


def infer(engine, cp, threshold, eligibility, plan, records):
    allocation = validate_plan(engine, threshold, plan)
    rows = validate_records(engine, threshold, plan, records, allocation)
    eta = Fraction(allocation["per_count_endpoint_error_exact"])
    contexts = []
    for fixed, row in zip(plan["contexts"], rows):
        out = {"id": row["id"]}
        for arm in engine.ARMS:
            item, cal = row[arm], fixed[arm]["calibration"]
            calibration = threshold.calibrate(engine, cp, {
                "rule": cal["rule"], "provenance": records["provenance"], "contract": cal["contract"],
                "gamma": allocation["per_calibration_error_exact"], "control_summary": item["calibration_summary"]})
            upper, lower, limits = {}, {}, {}
            total = fixed[arm]["future_cohort_tested"]
            for route in engine.ROUTES:
                ctl = item["known_truth_controls"][route]
                upper[route], ucert = engine.certified_one_sided(cp, item["observed_counts"][route], total, eta, lower=False)
                lower[route], lcert = engine.certified_one_sided(cp, ctl["correct"], ctl["introduced"], eta, lower=True)
                limits[route] = {"observed_upper": ucert, "correct_call_lower": lcert,
                                 "observed_successes": item["observed_counts"][route], "observed_trials": total,
                                 "control_successes": ctl["correct"], "control_trials": ctl["introduced"]}
            gate = item["gate_counts"]
            gl, gcert = engine.certified_one_sided(cp, gate["positive"], gate["tested"], eta, lower=True)
            bound = eligibility.gate_bound(engine, gl, calibration["control_false_gate_upper_exact"])
            beta = Fraction(bound["eligible_fraction_lower_exact"])
            result = engine.capped_simplex_bounds(eligibility.eligibility_caps(engine, upper, lower, beta))
            result.update(range_kind="conservative_joint_error_budget_outer_projection",
                          closure_witness_scope="Cap outer set only; no full joint gate/classifier/count-confidence feasibility certificate.",
                          calibration=calibration, eligibility=bound, marginal_limits=limits,
                          gate_positive_lower=gcert, pipeline_id=item["pipeline_id"], provenance=item["provenance"],
                          observed_counts=dict(item["observed_counts"]), gate_counts=dict(gate))
            out[arm] = result
        out["J"] = engine.ratio_interval(out["baseline"], out["selected"])
        contexts.append(out)
    common = engine.common_intersection([row["J"] for row in contexts])
    if common["status"] == "compatible":
        common.update(status="not_rejected", interpretation="Outer intervals overlap; full joint feasibility or equal biological curvature is not established.")
    return {
        "schema_version": "integrated-inference-1", "provenance": records["provenance"],
        "plan_sha256": canonical_digest(plan), "contract": plan["contract"],
        "hash_scope": "Content integrity only; not registration, chronology, truth, transport or sampling validation.",
        "contracts_and_records_are_assertions_not_programmatically_established": True,
        "target": "J=Q(selected)/Q(baseline), Q=pA^2/(pW*pM); p conditional on true full-cohort eligibility",
        "confidence": dict(allocation, count_coverage_conditional_on_all_training_and_calibration_required=True,
                           calibration_coverage_marginal_over_calibration_not_conditional_on_observed_threshold=True,
                           between_component_independence_required=False, transport_estimation_error_included=False),
        "contexts": contexts, "common_J": common,
        "reject_common_J": len(contexts) >= 2 and common["separated"],
        "decision_scope": "Level-alpha common-J rejection under all declared premises; one context descriptive; incompatible caps unevaluable.",
        "joint_gate_classifier_sharpness_claimed": False,
        "native_parameter_authentication_performed": False,
        "registry_changes_performed": False,
        "dependencies": {name + "_SHA256": entry[1] for name, entry in PINS.items()},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("observations", type=Path, nargs="?")
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--plan-only", action="store_true", help="Validate fixed design and print its digest/budget without observations; does not register it")
    parser.add_argument("--repository", type=Path, default=DEFAULT_REPOSITORY)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        engine, cp, threshold, eligibility = load_dependencies(args.repository)
        def read(path):
            with path.open("rb") as stream:
                raw = stream.read(engine.MAX_INPUT_BYTES + 1)
            return raw, engine.load_json(raw)
        plan_raw, plan = read(args.plan)
        allocation = validate_plan(engine, threshold, plan)
        if args.plan_only:
            if args.observations is not None:
                raise ValueError("Plan-only mode does not accept observation data")
            result = {"schema_version": "integrated-plan-check-1", "plan_sha256": canonical_digest(plan), "allocation": allocation,
                      "scope": "Content integrity and declared design check only; no registration or chronology proof, and no observed calibration."}
        else:
            if args.observations is None:
                raise ValueError("Observation input is required unless --plan-only is selected")
            raw, records = read(args.observations)
            result = infer(engine, cp, threshold, eligibility, plan, records)
            result["observation_file_sha256"] = hashlib.sha256(raw).hexdigest()
        result["plan_file_sha256"] = hashlib.sha256(plan_raw).hexdigest()
        rendered = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
        if args.output:
            args.output.write_text(rendered)
        else:
            print(rendered, end="")
    except (ValueError, OSError, KeyError, TypeError, ArithmeticError) as exc:
        parser.exit(2, f"Invalid input or unsupported numerical domain: {exc}\n")


if __name__ == "__main__":
    main()
