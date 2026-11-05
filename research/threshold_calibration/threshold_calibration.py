#!/usr/bin/env python3
"""Selection-aware false-gate certificates for a fixed-score sample maximum.

Standard-library wrapper of pinned certified CP endpoints. The inferential
justification is an order-statistic argument, not fixed-gate binomial sampling.
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
CLASSIFICATION_SHA256 = "66996adfd4f90bccf7315a82022d6b96d390378f4be781f992e7229058bfb368"
CP_SHA256 = "23feb7547d481fc4d361b25da28fe9d46d79be2f9fe66376f9c9ca85c069c79d"
CONTRACT = {
    "truth": "control_units_known_Other_independently_of_scores",
    "sampling": "fixed_positive_n_iid_scalar_scores_from_one_control_population",
    "score_pipeline": "entire_score_pipeline_fixed_independently_of_calibration_data",
    "design": "n_score_pipeline_maximum_rule_comparator_and_gamma_fixed_before_calibration",
    "summary": "maximum_and_if_required_multiplicity_over_all_n_controls_no_omissions",
    "deployment": "same_fixed_score_pipeline_and_realized_threshold_frozen_for_independent_future_units",
}
RULES = ("strict_maximum", "inclusive_maximum")


def load_engine(repository=DEFAULT_REPOSITORY):
    """Check the original dependency bytes and avoid writes to their tree."""
    path = Path(repository) / "research" / "classification_bounds" / "classification_bounds.py"
    if hashlib.sha256(path.read_bytes()).hexdigest() != CLASSIFICATION_SHA256:
        raise ValueError("Classification dependency hash mismatch")
    saved = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location("pinned_threshold_classification", path)
        engine = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(engine)
        if engine.CP_SHA256 != CP_SHA256:
            raise ValueError("Certified CP dependency declaration mismatch")
        cp = engine.load_cp()
    finally:
        sys.dont_write_bytecode = saved
    return engine, cp


def validate(engine, doc):
    engine.mapping(doc, ("rule", "provenance", "contract", "gamma", "control_summary"), "document")
    rule = doc["rule"]
    if rule not in RULES:
        raise ValueError("rule must be strict_maximum or inclusive_maximum")
    if doc["provenance"] not in ("synthetic", "observed", "literature_transcription"):
        raise ValueError("Explicit provenance is required")
    descriptions = ("control_unit", "control_population", "score_definition")
    engine.mapping(doc["contract"], tuple(CONTRACT) + descriptions, "contract")
    for key, expected in CONTRACT.items():
        if doc["contract"][key] != expected:
            raise ValueError(f"contract.{key} must be {expected}")
    for key in descriptions:
        if not isinstance(doc["contract"][key], str) or not doc["contract"][key].strip():
            raise ValueError(f"contract.{key} must be a nonempty description")
    gamma = engine.rational(doc["gamma"], "gamma")
    if not Fraction(1, 10**12) <= gamma < 1:
        raise ValueError("gamma must be at least 1e-12 and below one")
    keys = ("tested", "maximum") + (("maximum_multiplicity",) if rule == "inclusive_maximum" else ())
    summary = engine.mapping(doc["control_summary"], keys, "control_summary")
    n = engine.count(summary["tested"], "control_summary.tested")
    if not n:
        raise ValueError("An observed maximum requires at least one control")
    maximum = engine.rational(summary["maximum"], "control_summary.maximum")
    k = 0
    if rule == "inclusive_maximum":
        k = engine.count(summary["maximum_multiplicity"], "control_summary.maximum_multiplicity")
        if not 1 <= k <= n:
            raise ValueError("Maximum multiplicity must be an integer from one to tested")
    return n, maximum, k, gamma


def calibrate(engine, cp, doc):
    n, maximum, k, gamma = validate(engine, doc)
    upper, endpoint = engine.certified_one_sided(cp, k, n, gamma, lower=False)
    strict = doc["rule"] == "strict_maximum"
    return {
        "schema_version": "threshold-calibration-1",
        "rule": doc["rule"], "provenance": doc["provenance"], "contract": doc["contract"],
        "contracts_and_control_summary_are_assertions_not_programmatically_established": True,
        "control_summary": dict(doc["control_summary"], maximum=str(maximum)),
        "frozen_gate": {"score_comparator": ">" if strict else ">=", "threshold_exact": str(maximum)},
        "target": "P(future_control_score > realized_maximum | calibration_sample)" if strict else
                  "P(future_control_score >= realized_maximum | calibration_sample)",
        "control_false_gate_upper_exact": str(upper),
        "confidence": {
            "one_sided_error_exact": str(gamma),
            "coverage_at_least_exact": str(1 - gamma),
            "coverage_scope": "marginal_over_repeated_calibration_samples_not_conditional_on_maximum_or_multiplicity",
            "sampling_basis": "strict_maximum_order_statistic" if strict else "inclusive_maximum_quantile_containment",
        },
        "numerical_endpoint": {
            "kernel": "certified_one_sided_CP_upper",
            "equivalent_k": k, "n": n, "endpoint": endpoint,
            "equivalent_k_is_not_a_fixed_gate_binomial_success_count": True,
        },
        "dependencies": {"classification_SHA256": CLASSIFICATION_SHA256, "certified_CP_SHA256": CP_SHA256},
        "native_false_gate_upper": None,
        "native_transfer": "Requires separately justified native_Other_tail_at_realized_threshold <= control_tail; not established here.",
        "interpretation": "Selection-aware maximum-threshold calibration under declared premises; no native value, eligibility estimate or biological validation is supplied.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--repository", type=Path, default=DEFAULT_REPOSITORY)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        engine, cp = load_engine(args.repository)
        with args.input.open("rb") as source:
            raw = source.read(engine.MAX_INPUT_BYTES + 1)
        doc = engine.load_json(raw)
        result = calibrate(engine, cp, doc)
        result["input_sha256"] = hashlib.sha256(raw).hexdigest()
        rendered = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
        if args.output:
            args.output.write_text(rendered)
        else:
            print(rendered, end="")
    except (ValueError, OSError, KeyError, TypeError, ArithmeticError) as exc:
        parser.exit(2, f"Invalid input or unsupported numerical domain: {exc}\n")


if __name__ == "__main__":
    main()
