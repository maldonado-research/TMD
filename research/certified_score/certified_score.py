#!/usr/bin/env python3
"""Certified rational confidence projection of frozen conditional-W/A/M log scores.

Original method implementation, Copyright (c) 2026 Ricardo Maldonado; MIT.
Standard-library only. No float enters an inferential decision. See README.md.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import re


ROUTES = ("W", "A", "M")
EXCLUDED = ("Other", "no_qualified_outcome", "unresolved_classification", "missing")
SCOPE = "observed_conditional_WAM_expected_log_score"
MAX_CONTEXTS = 16
MAX_COMPARATORS = 32
MAX_TRIALS = 500
MAX_CP_BITS = 64
MAX_LOG_TERMS = 64
MAX_LOG_BITS = 96
MAX_REPORT_BITS = 96
MAX_INPUT_BITS = 128
MAX_PROBABILITY_BITS = 64
MAX_LOG_ARGUMENT_BITS = 144  # Includes inverse tiny tail allocations in precision planning.
MAX_CP_WORK = 600_000
MAX_INPUT_BYTES = 1_000_000
RATIONAL_PATTERN = re.compile(r"[+-]?[0-9]+(?:/[0-9]+|\.[0-9]+)?\Z")


def integer(value, label, low=0, high=MAX_TRIALS):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{label} requires an integer in [{low},{high}], never a bool")
    return value


def rational(value, label="rational", bits=MAX_INPUT_BITS):
    """Fractions for internal use; JSON inputs must be bounded rational strings."""
    if isinstance(value, Fraction):
        result = value
    elif type(value) is str and len(value) <= 96 and RATIONAL_PATTERN.fullmatch(value):
        try:
            result = Fraction(value)
        except (ValueError, ZeroDivisionError) as exc:
            raise ValueError(f"Invalid {label}") from exc
    else:
        raise ValueError(f"{label} requires a rational string; floats/NaN/bools rejected")
    if max(abs(result.numerator).bit_length(), result.denominator.bit_length()) > bits:
        raise ValueError(f"{label} exceeds the {bits}-bit rational input cap")
    return result


def exact_keys(value, keys, label):
    if type(value) is not dict or set(value) != set(keys):
        raise ValueError(f"{label} requires exactly {sorted(keys)}")


def positive_triad(values, label):
    if type(values) is not list or len(values) != 3:
        raise ValueError(f"{label} requires exactly three W/A/M probabilities")
    result = tuple(rational(v, label, MAX_PROBABILITY_BITS) for v in values)
    if any(v <= 0 for v in result) or sum(result) != 1:
        raise ValueError(f"{label} must be strictly positive and sum to one exactly")
    return result


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def strict_json(raw):
    """Reject ambiguous duplicate keys and JSON's nonstandard NaN/Infinity extension."""
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON object key")
            result[key] = value
        return result
    def constant(_):
        raise ValueError("Nonstandard NaN/Infinity JSON constants rejected")
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


def plan_sha256(plan):
    """Integrity only: computing a hash does not prove pre-outcome registration."""
    return hashlib.sha256(canonical_bytes(plan)).hexdigest()


def validate_plan(plan):
    exact_keys(plan, {"alpha", "cp_bisection_bits", "log_terms", "log_fraction_bits",
                      "report_fraction_bits", "comparator_names", "contexts", "gates"}, "plan")
    alpha = rational(plan["alpha"], "alpha")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be strictly between zero and one")
    cp_bits = integer(plan["cp_bisection_bits"], "cp_bisection_bits", 1, MAX_CP_BITS)
    terms = integer(plan["log_terms"], "log_terms", 1, MAX_LOG_TERMS)
    log_bits = integer(plan["log_fraction_bits"], "log_fraction_bits", 1, MAX_LOG_BITS)
    report_bits = integer(plan["report_fraction_bits"], "report_fraction_bits", 1, MAX_REPORT_BITS)
    names = plan["comparator_names"]
    if (type(names) is not list or not 1 <= len(names) <= MAX_COMPARATORS
            or any(type(n) is not str or not n.strip() or len(n) > 100 for n in names)
            or len(set(names)) != len(names)):
        raise ValueError("Unique nonempty, bounded comparator names are mandatory")
    rows = plan["contexts"]
    if type(rows) is not list or not 1 <= len(rows) <= MAX_CONTEXTS:
        raise ValueError(f"One to {MAX_CONTEXTS} contexts required")
    parsed, ids = [], []
    for row in rows:
        exact_keys(row, {"id", "weight", "fixed_total_units", "tmd", "comparators"}, "context")
        name = row["id"]
        if type(name) is not str or not name.strip() or len(name) > 100 or name in ids:
            raise ValueError("Unique nonempty, bounded context ids required")
        ids.append(name)
        weight = rational(row["weight"], "context weight")
        if weight < 0:
            raise ValueError("Context weights must be nonnegative")
        total = integer(row["fixed_total_units"], "fixed_total_units", 1)
        tmd = positive_triad(row["tmd"], "TMD forecast")
        exact_keys(row["comparators"], names, "comparators")
        comparators = {n: positive_triad(row["comparators"][n], n) for n in names}
        parsed.append({"id": name, "weight": weight, "total": total,
                       "tmd": tmd, "comparators": comparators})
    if sum(row["weight"] for row in parsed) != 1:
        raise ValueError("Frozen context weights must sum to one exactly")
    # Use the pre-outcome full-frame maximum, not realized favorable counts.
    estimated_work = 6 * cp_bits * sum(row["total"] for row in parsed)
    if estimated_work > MAX_CP_WORK:
        raise ValueError(f"Plan exceeds exact CP work cap {MAX_CP_WORK}; uncertifiable, not a decision")
    gates = plan["gates"]
    exact_keys(gates, {"success_threshold", "failure_mode", "failure_threshold"}, "gates")
    success = rational(gates["success_threshold"], "success_threshold")
    mode = gates["failure_mode"]
    if mode == "disabled":
        if gates["failure_threshold"] is not None:
            raise ValueError("Disabled failure gate requires a null threshold")
        failure = None
    elif mode == "any_upper_lt_threshold":
        failure = rational(gates["failure_threshold"], "failure_threshold")
        if failure > success:
            raise ValueError("Failure threshold cannot exceed success threshold")
    else:
        raise ValueError("Unsupported failure gate")
    return {"alpha": alpha, "cp_bits": cp_bits, "terms": terms, "log_bits": log_bits,
            "report_bits": report_bits, "names": names, "rows": parsed,
            "success": success, "failure": failure, "estimated_cp_work": estimated_work}


def validate_document(doc):
    exact_keys(doc, {"schema_version", "scope", "provenance", "route_order", "assumptions",
                     "plan", "expected_plan_sha256", "outcomes"}, "document")
    if type(doc["schema_version"]) is not int or doc["schema_version"] != 1:
        raise ValueError("Unsupported schema version")
    if doc["scope"] != SCOPE or doc["route_order"] != list(ROUTES):
        raise ValueError("Only the declared observed conditional W/A/M estimand is supported")
    if doc["provenance"] not in ("synthetic", "observed"):
        raise ValueError("Explicit synthetic or observed provenance required")
    flags = {"independent_founder_units", "iid_conditional_multinomial_marginals_justified",
             "independent_training_and_calibration", "forecasts_weights_gates_precision_frozen",
             "fixed_stopping_no_interim_looks", "other_exclusion_and_missingness_rule_frozen",
             "complete_endpoint_ledger", "clusters_not_counted_as_independent_descendants"}
    text = {"count_law_justification", "founder_unit_definition", "sampling_and_conditioning_rule",
            "freeze_reference", "fixed_stopping_rule"}
    assumptions = doc["assumptions"]
    exact_keys(assumptions, flags | text, "assumptions")
    if any(assumptions[k] is not True for k in flags):
        raise ValueError("Every statistical design assertion must explicitly be true")
    if any(type(assumptions[k]) is not str or not assumptions[k].strip()
           or len(assumptions[k]) > 4000 for k in text):
        raise ValueError("Nonempty bounded measurement and frozen-design descriptions required")
    expected = doc["expected_plan_sha256"]
    if type(expected) is not str or not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ValueError("A frozen plan SHA256 is mandatory")
    if expected != plan_sha256(doc["plan"]):
        raise ValueError("Frozen plan integrity mismatch")
    parsed = validate_plan(doc["plan"])
    ids = [row["id"] for row in parsed["rows"]]
    exact_keys(doc["outcomes"], ids, "outcomes")
    for row in parsed["rows"]:
        out = doc["outcomes"][row["id"]]
        exact_keys(out, {"counts", "excluded_ledger"}, "outcome")
        counts = out["counts"]
        if type(counts) is not list or len(counts) != 3:
            raise ValueError("Exactly three explicit W/A/M counts required")
        counts = tuple(integer(k, "endpoint count") for k in counts)
        n = sum(counts)
        if n == 0:
            raise ValueError("No qualifying W/A/M endpoints: target not evaluable")
        exact_keys(out["excluded_ledger"], EXCLUDED, "excluded_ledger")
        excluded = {k: integer(out["excluded_ledger"][k], "excluded endpoint count") for k in EXCLUDED}
        if n + sum(excluded.values()) != row["total"]:
            raise ValueError("Complete endpoint ledger must match the frozen fixed total")
        row["counts"], row["n"], row["excluded"] = counts, n, excluded
    return parsed


def exact_binomial_tail(n, k, p, upper=True):
    """Exact rational P[Bin(n,p)>=k] or P[Bin(n,p)<=k]; integer recurrence."""
    integer(n, "binomial n", 1)
    integer(k, "binomial k", 0, n)
    if not isinstance(p, Fraction) or not 0 <= p <= 1 or type(upper) is not bool:
        raise ValueError("Exact tail requires a rational probability and boolean direction")
    if p == 0:
        return Fraction(int(k == 0) if upper else 1)
    if p == 1:
        return Fraction(1 if upper else int(k == n))
    u, d = p.numerator, p.denominator
    q = d - u
    if upper and n - k + 1 > k:
        start, stop, complement = 0, k - 1, True
    elif not upper and k + 1 > n - k:
        start, stop, complement = k + 1, n, True
    else:
        start, stop, complement = (k if upper else 0), (n if upper else k), False
    if stop < start:
        return Fraction(1)  # Complement of an empty tail.
    term = math.comb(n, start) * u**start * q**(n - start)
    total = term
    for j in range(start, stop):
        term, remainder = divmod(term * (n - j) * u, (j + 1) * q)
        if remainder:
            raise ArithmeticError("Exact binomial recurrence failed divisibility")
        total += term
    denominator = d**n
    if complement:
        total = denominator - total
    return Fraction(total, denominator)


@lru_cache(maxsize=4096, typed=True)
def cp_interval(n, k, tail, bits):
    """Outward dyadic CP endpoints, with exact root brackets of width 2^-bits."""
    integer(n, "CP n", 1)
    integer(k, "CP k", 0, n)
    integer(bits, "CP bits", 1, MAX_CP_BITS)
    if not isinstance(tail, Fraction) or not 0 < tail < Fraction(1, 2):
        raise ValueError("Exact per-tail error must be in (0,1/2)")
    def bracket(upper):
        lo, hi = Fraction(0), Fraction(1)
        for _ in range(bits):
            mid = (lo + hi) / 2
            value = exact_binomial_tail(n, k, mid, upper)
            if value == tail:
                return mid, mid
            if (value < tail) == upper:
                lo = mid
            else:
                hi = mid
        return lo, hi
    lower_root = (Fraction(0), Fraction(0)) if k == 0 else bracket(True)
    upper_root = (Fraction(1), Fraction(1)) if k == n else bracket(False)
    lo, hi = lower_root[0], upper_root[1]
    if not 0 <= lo <= hi <= 1:
        raise ArithmeticError("Invalid outward CP interval")
    return lo, hi, lower_root, upper_root


def dyadic_outer(value, bits, lower):
    """Round an exact rational outward; never convert through a binary float."""
    if not isinstance(value, Fraction) or type(lower) is not bool:
        raise ValueError("Outward rounding needs an exact rational and direction")
    integer(bits, "dyadic bits", 1, MAX_REPORT_BITS)
    numerator = value.numerator << bits
    denominator = value.denominator
    scaled = numerator // denominator if lower else -((-numerator) // denominator)
    return Fraction(scaled, 1 << bits)


def positive_series_log(r, terms):
    """ln(r) enclosure for 1<=r<=2 from the positive atanh series/remainder."""
    if not isinstance(r, Fraction) or not 1 <= r <= 2:
        raise ValueError("Reduced logarithm argument must be rational in [1,2]")
    integer(terms, "log terms", 1, MAX_LOG_TERMS)
    z = (r - 1) / (r + 1)
    square, power, total = z * z, z, Fraction(0)
    for j in range(terms):
        total += 2 * power / (2 * j + 1)
        power *= square
    remainder = 2 * power / ((2 * terms + 1) * (1 - square))
    return total, total + remainder


@lru_cache(maxsize=8192, typed=True)
def log_enclosure(x, terms=32, bits=64):
    """Certified rational enclosure of natural log(x), including signed range reduction."""
    if not isinstance(x, Fraction) or x <= 0:
        raise ValueError("Log argument must be a positive rational")
    if max(x.numerator.bit_length(), x.denominator.bit_length()) > MAX_LOG_ARGUMENT_BITS:
        raise ValueError("Log ratio exceeds the bounded prototype argument domain")
    integer(terms, "log terms", 1, MAX_LOG_TERMS)
    integer(bits, "log bits", 1, MAX_LOG_BITS)
    exponent = x.numerator.bit_length() - x.denominator.bit_length()
    scale = Fraction(1 << exponent) if exponent >= 0 else Fraction(1, 1 << -exponent)
    reduced = x / scale
    if reduced < 1:
        exponent -= 1
        reduced *= 2
    if not 1 <= reduced < 2:
        raise ArithmeticError("Logarithm range reduction failed")
    lo, hi = positive_series_log(reduced, terms)
    two_lo, two_hi = positive_series_log(Fraction(2), terms)
    if exponent >= 0:
        lo, hi = lo + exponent * two_lo, hi + exponent * two_hi
    else:
        lo, hi = lo + exponent * two_hi, hi + exponent * two_lo
    return dyadic_outer(lo, bits, True), dyadic_outer(hi, bits, False)


def exact_extreme(box, coefficients, maximum=False):
    """Greedy exact linear-program extremum over a bounded probability simplex."""
    if type(maximum) is not bool or len(box) != 3 or len(coefficients) != 3:
        raise ValueError("A W/A/M box and three exact coefficients required")
    for lo, hi in box:
        if not isinstance(lo, Fraction) or not isinstance(hi, Fraction) or not 0 <= lo <= hi <= 1:
            raise ValueError("Invalid rational probability box")
    if any(not isinstance(a, Fraction) for a in coefficients):
        raise ValueError("Exact rational score coefficients required")
    lower_sum, upper_sum = sum(lo for lo, _ in box), sum(hi for _, hi in box)
    if lower_sum > 1 or upper_sum < 1:
        raise ValueError("Empty box/simplex region: unevaluable, never a biological rejection")
    point = [lo for lo, _ in box]
    remaining = 1 - lower_sum
    for i in sorted(range(3), key=lambda j: coefficients[j], reverse=maximum):
        amount = min(remaining, box[i][1] - point[i])
        point[i] += amount
        remaining -= amount
    if remaining != 0 or sum(point) != 1:
        raise ArithmeticError("Exact simplex allocation failed")
    return sum(p * a for p, a in zip(point, coefficients)), tuple(point)


def score_projection(box, coefficients):
    if len(coefficients) != 3 or any(len(interval) != 2 for interval in coefficients):
        raise ValueError("Three exact logarithm intervals required")
    if any(not isinstance(x, Fraction) for interval in coefficients for x in interval):
        raise ValueError("Rational logarithm interval endpoints required")
    if any(lo > hi for lo, hi in coefficients):
        raise ValueError("Reversed logarithm enclosure")
    lo, lo_point = exact_extreme(box, [v[0] for v in coefficients])
    hi, hi_point = exact_extreme(box, [v[1] for v in coefficients], True)
    return lo, hi, lo_point, hi_point


def decide(bounds, success_threshold, failure_threshold):
    if not bounds or any(not isinstance(x, Fraction) for b in bounds for x in b):
        raise ValueError("Nonempty exact rational bounds required")
    if any(lo > hi for lo, hi in bounds) or not isinstance(success_threshold, Fraction):
        raise ValueError("Valid exact score intervals and threshold required")
    if failure_threshold is not None and (not isinstance(failure_threshold, Fraction)
                                         or failure_threshold > success_threshold):
        raise ValueError("Explicit compatible exact failure gate required")
    if all(lo > success_threshold for lo, _ in bounds):
        return "certified_success_at_declared_score_gate"
    if failure_threshold is not None and any(hi < failure_threshold for _, hi in bounds):
        return "certified_failure_at_declared_score_gate"
    return "inconclusive_at_declared_score_gate"


def coefficient_table(parsed):
    return {row["id"]: {
        name: tuple(log_enclosure(row["tmd"][i] / row["comparators"][name][i],
                                  parsed["terms"], parsed["log_bits"]) for i in range(3))
        for name in parsed["names"]} for row in parsed["rows"]}


def analyze(doc):
    parsed = validate_document(doc)
    c = len(parsed["rows"])
    tail = parsed["alpha"] / (2 * 3 * c)
    coefficients = coefficient_table(parsed)
    accumulated = {name: [Fraction(0), Fraction(0)] for name in parsed["names"]}
    contexts = []
    for row in parsed["rows"]:
        cells = [cp_interval(row["n"], k, tail, parsed["cp_bits"]) for k in row["counts"]]
        box = tuple((v[0], v[1]) for v in cells)
        comparisons = {}
        for name in parsed["names"]:
            coeff = coefficients[row["id"]][name]
            lo, hi, lower_point, upper_point = score_projection(box, coeff)
            accumulated[name][0] += row["weight"] * lo
            accumulated[name][1] += row["weight"] * hi
            comparisons[name] = {"coefficient_enclosures_exact": [[str(a), str(b)] for a, b in coeff],
                "score_interval_exact": [str(lo), str(hi)],
                "lower_extremizing_distribution_exact": [str(p) for p in lower_point],
                "upper_extremizing_distribution_exact": [str(p) for p in upper_point]}
        contexts.append({"id": row["id"], "weight_exact": str(row["weight"]),
            "qualifying_endpoints": row["n"], "fixed_total_units": row["total"],
            "excluded_ledger": row["excluded"],
            "probability_box_exact": [[str(lo), str(hi)] for lo, hi in box],
            "cp_root_brackets_exact": [
                {"lower": [str(v) for v in cell[2]], "upper": [str(v) for v in cell[3]]}
                for cell in cells], "comparisons": comparisons})
    final = {name: (dyadic_outer(bounds[0], parsed["report_bits"], True),
                    dyadic_outer(bounds[1], parsed["report_bits"], False))
             for name, bounds in accumulated.items()}
    decision = decide(list(final.values()), parsed["success"], parsed["failure"])
    return {"schema_version": 1, "method_status": "candidate_certified_rational_implementation",
        "scope": SCOPE, "provenance": doc["provenance"], "plan_sha256": doc["expected_plan_sha256"],
        "input_sha256": hashlib.sha256(canonical_bytes(doc)).hexdigest(),
        "alpha_exact": str(parsed["alpha"]), "count_coordinates": 3 * c,
        "per_tail_error_exact": str(tail), "simultaneous_coverage_lower_bound_exact": str(1 - parsed["alpha"]),
        "coverage_regime": "Unconditional over complete fixed-study sampling, conditional only on independently frozen forecast information. No coverage claim conditional on all qualifying totals being positive, their joint vector, report issuance or favorable gates. Zero qualifying counts issue no certificate.",
        "extra_comparator_bonferroni_division": False,
        "contexts": contexts,
        "weighted_score_intervals_exact": {name: [str(lo), str(hi)] for name, (lo, hi) in final.items()},
        "decision": decision,
        "success_threshold_exact": str(parsed["success"]),
        "failure_threshold_exact": None if parsed["failure"] is None else str(parsed["failure"]),
        "decision_basis": "Strict comparisons of outward rational endpoints; every declared comparator must pass success. Equality or overlap is inconclusive. Failure uses only its frozen optional gate.",
        "numerical_policy": {"cp_bisection_bits": parsed["cp_bits"], "log_terms": parsed["terms"],
            "log_fraction_bits": parsed["log_bits"], "report_fraction_bits": parsed["report_bits"],
            "estimated_cp_work": parsed["estimated_cp_work"], "maximum_cp_work": MAX_CP_WORK,
            "maximum_trials_per_context": MAX_TRIALS, "maximum_contexts": MAX_CONTEXTS,
            "maximum_comparators": MAX_COMPARATORS, "maximum_probability_input_bits": MAX_PROBABILITY_BITS},
        "claim_limits": ["All coverage and decisions are conditional on the asserted count law, frozen design and independent training/calibration; declarations and hashes do not authenticate them.",
            "Only the realized rational frozen forecasts are evaluated. Rationalizing floating exponent/ridge predictions defines that forecast; it does not certify the ideal real-number model.",
            "Other/no-qualified/unresolved/missing endpoints are reported but excluded from this conditional estimand.",
            "No latent biological probability, causal mechanism, inheritance law, power, registration, new theorem or biological discovery is established.",
            "Synthetic data are verification, never observations. No automatic publication or biological inference is performed."]}


def precision_plan(plan, half_width_target, shares):
    """Pre-outcome worst-case CP score-width guide, not effect estimation or power."""
    parsed = validate_plan(plan)
    target = rational(half_width_target, "half_width_target")
    if target <= 0:
        raise ValueError("A positive rational precision target required")
    exact_keys(shares, [r["id"] for r in parsed["rows"]], "precision shares")
    fractions = {name: rational(value, "precision share") for name, value in shares.items()}
    if any(v <= 0 for v in fractions.values()) or sum(fractions.values()) != 1:
        raise ValueError("Strictly positive frozen precision shares must sum to one exactly")
    table = coefficient_table(parsed)
    tail = parsed["alpha"] / (6 * len(parsed["rows"]))
    # Hoeffding applied to the CP defining tails gives radius <= sqrt(L/(2n)).
    _, l_upper = log_enclosure(1 / tail, parsed["terms"], parsed["log_bits"])
    ranges, widths = {}, {}
    for row in parsed["rows"]:
        coeff = table[row["id"]]
        ranges[row["id"]] = max(max(b for _, b in v) - min(a for a, _ in v) for v in coeff.values())
        widths[row["id"]] = max(b - a for v in coeff.values() for a, b in v)
    cp_pad = Fraction(1, 1 << parsed["cp_bits"])
    report_pad = Fraction(1, 1 << parsed["report_bits"])
    finite_precision = report_pad + sum(row["weight"] *
        (ranges[row["id"]] * cp_pad + widths[row["id"]] / 2) for row in parsed["rows"])
    residual = target - finite_precision
    if residual <= 0:
        raise ValueError("Requested width cannot be certified at the frozen numeric precision")
    required = {}
    for row in parsed["rows"]:
        weighted_range = row["weight"] * ranges[row["id"]]
        quotient = l_upper * weighted_range**2 / (2 * (residual * fractions[row["id"]])**2)
        n = max(1, -(-quotient.numerator // quotient.denominator))
        required[row["id"]] = {"minimum_qualifying_endpoints": n,
            "weighted_range_upper_exact": str(weighted_range),
            "supported_by_trial_cap": n <= MAX_TRIALS}
    # Work depends on any later changed/frozen full-frame plan, not only these minima.
    return {"schema_version": 1, "status": "pre_outcome_deterministic_precision_guidance",
        "plan_sha256": plan_sha256(plan), "half_width_target_exact": str(target),
        "log_inverse_tail_upper_exact": str(l_upper),
        "finite_precision_half_width_allowance_exact": str(finite_precision),
        "qualifying_sample_requirements": required,
        "guarantee": "If each context supplies at least its listed qualifying count, its CP interval and the stated frozen rational predictors are used, the final projected interval half-width is at most the target for every declared comparator and every possible such count vector.",
        "limits": ["Pre-outcome arithmetic guidance only; no observations enter. It does not calculate power or guarantee a score clears a threshold.",
            "Fixed total founder units need not deliver the required qualifying endpoints. A scientifically justified prospective sampling/stopping design must address exclusions without adding interim looks.",
            "Requirements beyond prototype trial/work caps need an independently reviewed implementation and new frozen numerical plan before unblinding.",
            "Shares and precision must be selected independently of held-out outcomes. Biological fields in the R3 registry remain unresolved."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--precision-target", help="Pre-outcome rational interval half-width target")
    parser.add_argument("--precision-shares", type=Path, help="JSON context/rational-share map")
    args = parser.parse_args()
    try:
        if args.input.stat().st_size > MAX_INPUT_BYTES:
            raise ValueError("Input exceeds bounded prototype byte limit")
        raw = args.input.read_bytes()
        if len(raw) > MAX_INPUT_BYTES:
            raise ValueError("Input exceeds bounded prototype byte limit")
        doc = strict_json(raw)
        if args.precision_target is not None:
            if args.precision_shares is None:
                raise ValueError("Precision planning requires explicitly frozen shares")
            if args.precision_shares.stat().st_size > MAX_INPUT_BYTES:
                raise ValueError("Precision shares exceed prototype byte limit")
            result = precision_plan(doc["plan"], args.precision_target,
                                    strict_json(args.precision_shares.read_text()))
        elif args.precision_shares is not None:
            raise ValueError("Precision shares without target are unsupported")
        else:
            result = analyze(doc)
        encoded = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
        if args.output:
            args.output.write_text(encoded)
        else:
            print(encoded, end="")
    except (ValueError, TypeError, KeyError, ArithmeticError, OSError, RecursionError) as exc:
        parser.exit(2, f"Unevaluable input or unsupported numeric domain: {exc}\n")


if __name__ == "__main__":
    main()
