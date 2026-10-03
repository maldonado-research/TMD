#!/usr/bin/env python3
"""Synthetic, floating mathematical verification; no certified inference or biology.

MIT under the project terms. Uses Python's standard library only.
Run --check to compare regenerated results with VERIFICATION_RECEIPT.json.
"""

import argparse
import itertools
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
S = (1, 0, -1)


def normalize(values):
    if any(not math.isfinite(x) or x <= 0 for x in values):
        raise ValueError("Prediction inputs must be finite and strictly positive")
    total = math.fsum(values)
    return tuple(x / total for x in values)


def softmax(logweights):
    maximum = max(logweights)
    return normalize([math.exp(x - maximum) for x in logweights])


def forecast(q, theta, eta):
    return softmax([math.log(q[i]) + theta * (i == 1) + eta * S[i]
                    for i in range(3)])


def contrast_theta(p, q):
    ell = [math.log(p[i] / q[i]) for i in range(3)]
    return ell[1] - (ell[0] + ell[2]) / 2


def direction_eta(p, q):
    return (math.log(p[0] / q[0]) - math.log(p[2] / q[2])) / 2


def smooth_triad(counts):
    if len(counts) != 3 or any(type(k) is not int or k < 0 for k in counts):
        raise ValueError("Three nonnegative integer triad counts are required")
    n = sum(counts)
    if n == 0:
        raise ValueError("An empty measurement frame cannot be repaired by smoothing")
    return tuple((k + 0.5) / (n + 1.5) for k in counts)


def smooth_binary(k, n):
    if type(k) is not int or type(n) is not int or n <= 0 or not 0 <= k <= n:
        raise ValueError("A positive known binary denominator is required")
    return (k + 0.5) / (n + 1)


def ridge(x, y, penalty=0.01):
    if len(x) != len(y) or not x or penalty <= 0:
        raise ValueError("Matched nonempty training vectors and positive penalty required")
    if not all(math.isfinite(z) for z in (*x, *y)):
        raise ValueError("Missing/nonfinite calibration features block fitting")
    xbar, ybar = math.fsum(x) / len(x), math.fsum(y) / len(y)
    sxx = math.fsum((z - xbar) ** 2 for z in x)
    sxy = math.fsum((x[i] - xbar) * (y[i] - ybar) for i in range(len(x)))
    slope = sxy / (sxx + penalty)
    return ybar - slope * xbar, slope


def build_predictors(training, target):
    """Operational point predictions; callers must authenticate all frames first."""
    def independent_inputs(row):
        for key in ("recovery_baseline", "recovery_selected", "establishment"):
            if len(row[key]) != 3:
                raise ValueError("Every independent assay must have exactly three route cells")
        baseline = smooth_triad(row["baseline_counts"])
        d0 = [smooth_binary(*cell) for cell in row["recovery_baseline"]]
        d1 = [smooth_binary(*cell) for cell in row["recovery_selected"]]
        f = [smooth_binary(*cell) for cell in row["establishment"]]
        qstar = normalize([baseline[i] * d1[i] / d0[i] for i in range(3)])
        x = math.log(f[0] / f[2]) / 2
        return qstar, f, x

    qstar, f, xnew = independent_inputs(target)
    theta_values, eta_values, x_values, flexible_y = [], [], [], [[], []]
    for row in training:
        q, _, x = independent_inputs(row)
        t = smooth_triad(row["selected_counts"])
        theta_values.append(contrast_theta(t, q))
        eta_values.append(direction_eta(t, q))
        x_values.append(x)
        for j, i in enumerate((1, 2)):
            flexible_y[j].append(math.log(t[i] / t[0]) - math.log(q[i] / q[0]))
    if not training:
        raise ValueError("Independent training contexts required")
    theta = math.fsum(theta_values) / len(theta_values)
    beta0, beta1 = ridge(x_values, eta_values)
    eta = beta0 + beta1 * xnew
    flexible_logits = [0.0]
    for y in flexible_y:
        intercept, slope = ridge(x_values, y)
        flexible_logits.append(intercept + slope * xnew)
    return {
        "theta": theta, "eta": eta, "eta_coefficients": [beta0, beta1],
        "feature": xnew,
        "probabilities": {
            "restricted": forecast(qstar, theta, eta),
            "supply_observation": qstar,
            "supply_establishment_observation": normalize([qstar[i] * f[i] for i in range(3)]),
            "flexible": softmax([math.log(qstar[i]) + flexible_logits[i] for i in range(3)])
        }
    }


def conditional_count_distribution(n, difference, q, theta, eta):
    p = forecast(q, theta, eta)
    terms = []
    for w in range(n + 1):
        m = w - difference
        a = n - w - m
        if m < 0 or a < 0:
            continue
        counts = (w, a, m)
        logmass = math.lgamma(n + 1) - math.fsum(math.lgamma(k + 1) for k in counts)
        logmass += math.fsum(counts[i] * math.log(p[i]) for i in range(3))
        terms.append((counts, logmass))
    if not terms:
        raise ValueError("Impossible conditioned count difference")
    probs = softmax([v for _, v in terms])
    return {counts: probs[i] for i, (counts, _) in enumerate(terms)}


def binomial_mass(n, k, p):
    if p == 0:
        return float(k == 0)
    if p == 1:
        return float(k == n)
    return math.exp(math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
                    + k * math.log(p) + (n - k) * math.log1p(-p))


def cp_interval(n, k, alpha):
    """Floating solution of exact CP defining equations, not certified endpoints."""
    if type(n) is not int or type(k) is not int or n <= 0 or not 0 <= k <= n or not 0 < alpha < 1:
        raise ValueError("Invalid binomial frame/error allocation")
    tail = alpha / 2
    def root(upper_tail):
        lo, hi = 0.0, 1.0
        for _ in range(80):
            middle = (lo + hi) / 2
            if upper_tail:
                value = math.fsum(binomial_mass(n, j, middle) for j in range(k, n + 1))
                if value < tail:
                    lo = middle
                else:
                    hi = middle
            else:
                value = math.fsum(binomial_mass(n, j, middle) for j in range(k + 1))
                if value > tail:
                    lo = middle
                else:
                    hi = middle
        return (lo + hi) / 2
    return (0.0 if k == 0 else root(True), 1.0 if k == n else root(False))


def score_bounds(box, coefficients):
    if len(box) != len(coefficients) or not box:
        raise ValueError("Matched nonempty probability boxes/coefficient vectors required")
    if any(not (0 <= lo <= hi <= 1) for lo, hi in box):
        raise ValueError("Invalid probability interval")
    if any(not math.isfinite(c) for c in coefficients):
        raise ValueError("Frozen score coefficients must be finite")
    if math.fsum(lo for lo, _ in box) > 1 or math.fsum(hi for _, hi in box) < 1:
        raise ValueError("Box/simplex intersection is empty; analysis unevaluable")
    def extreme(reverse):
        p = [lo for lo, _ in box]
        remaining = 1 - math.fsum(p)
        for i in sorted(range(len(p)), key=lambda j: coefficients[j], reverse=reverse):
            moved = min(max(remaining, 0.0), box[i][1] - p[i])
            p[i] += moved
            remaining -= moved
        if abs(remaining) > 1e-10:
            raise ValueError("Numeric probability allocation failed")
        return math.fsum(p[i] * coefficients[i] for i in range(len(p)))
    return extreme(False), extreme(True)


def explicit_vertices(box):
    vertices = []
    for free in range(3):
        fixed = [i for i in range(3) if i != free]
        for ends in itertools.product((0, 1), repeat=2):
            p = [0.0] * 3
            for j, i in enumerate(fixed):
                p[i] = box[i][ends[j]]
            p[free] = 1 - sum(p)
            if box[free][0] - 1e-12 <= p[free] <= box[free][1] + 1e-12:
                vertices.append(p)
    return vertices


def assert_close(a, b, tolerance=2e-11):
    if not math.isclose(a, b, rel_tol=tolerance, abs_tol=tolerance):
        raise AssertionError((a, b))


def verify():
    thetas = (-1.0, -0.5, 0.0, math.log(1.5), 0.5, 1.0, 2.0)
    etas = (-2.0, -1.0, 0.0, 0.2, 1.0, 2.0)
    baselines = [normalize([j + 1, ((j * 5) % 13) + 1, ((j * 7) % 17) + 1]) for j in range(12)]
    model_checks = 0
    for q, theta, eta in itertools.product(baselines, thetas, etas):
        p = forecast(q, theta, eta)
        quadratic = softmax([math.log(q[i]) - theta * S[i] ** 2 + eta * S[i] for i in range(3)])
        for a, b in zip(p, quadratic):
            assert_close(a, b)
        assert_close(contrast_theta(p, q), theta)
        assert_close(direction_eta(p, q), eta)
        reconstructed = forecast(q, contrast_theta(p, q), direction_eta(p, q))
        for a, b in zip(p, reconstructed):
            assert_close(a, b)
        model_checks += 1

    conditional_checks = 0
    for q, theta, difference in itertools.product(baselines[:3], (-0.5, 0, 0.5), (-8, -4, 0, 4, 8)):
        reference = conditional_count_distribution(10, difference, q, theta, 0)
        for eta in (-2, -1, 1, 2):
            result = conditional_count_distribution(10, difference, q, theta, eta)
            assert result.keys() == reference.keys()
            for count in reference:
                assert_close(result[count], reference[count])
            conditional_checks += 1
    assert len(conditional_count_distribution(3, 3, baselines[0], 0, 0)) == 1

    uniform = (1 / 3,) * 3
    pooled = tuple((a + b) / 2 for a, b in zip(forecast(uniform, 0, 1), forecast(uniform, 0, -1)))
    pooled_theta = contrast_theta(pooled, uniform)
    assert_close(pooled_theta, -math.log(math.cosh(1)))
    recovery = normalize([uniform[i] * (0.6, 0.9, 0.6)[i] for i in range(3)])
    assert_close(contrast_theta(recovery, uniform), math.log(1.5))
    equal_j_different_probabilities = normalize([0.9, 0.6, 0.4])
    assert_close(contrast_theta(equal_j_different_probabilities, uniform), 0)
    assert max(abs(a - b) for a, b in zip(equal_j_different_probabilities, uniform)) > 0.1
    weak = forecast(uniform, math.log(1.5), 0)
    weak_oracle_gain = math.fsum(weak[i] * math.log(weak[i] / uniform[i]) for i in range(3))
    assert weak_oracle_gain < 0.02

    # Exact enumeration of a finite multinomial example checks the probability
    # law and allocation. The computed floating interval endpoints are not certified.
    n, alpha, true_p = 12, 0.05, (0.1, 0.2, 0.7)
    intervals = {k: cp_interval(n, k, alpha / 3) for k in range(n + 1)}
    coverage_terms, mass_terms = [], []
    for w in range(n + 1):
        for a in range(n - w + 1):
            counts = (w, a, n - w - a)
            logmass = math.lgamma(n + 1) - math.fsum(math.lgamma(k + 1) for k in counts)
            logmass += math.fsum(counts[i] * math.log(true_p[i]) for i in range(3))
            mass = math.exp(logmass)
            mass_terms.append(mass)
            if all(intervals[counts[i]][0] <= true_p[i] <= intervals[counts[i]][1] for i in range(3)):
                coverage_terms.append(mass)
    assert_close(math.fsum(mass_terms), 1)
    finite_example_coverage = math.fsum(coverage_terms)
    assert finite_example_coverage >= 1 - alpha
    assert intervals[0][0] == 0 and intervals[n][1] == 1

    score_checks = 0
    boxes = [((0.0, 0.6), (0.1, 0.8), (0.0, 0.8)),
             ((0.1, 0.5), (0.2, 0.6), (0.1, 0.7)),
             ((0.2, 0.2), (0.1, 0.5), (0.3, 0.7))]
    tmd = (0.25, 0.5, 0.25)
    competitors = [(1 / 3,) * 3, (0.5, 0.3, 0.2), (0.2, 0.3, 0.5)]
    for box, competitor in itertools.product(boxes, competitors):
        coefficients = [math.log(tmd[i] / competitor[i]) for i in range(3)]
        lo, hi = score_bounds(box, coefficients)
        vals = [math.fsum(p[i] * coefficients[i] for i in range(3)) for p in explicit_vertices(box)]
        assert_close(lo, min(vals))
        assert_close(hi, max(vals))
        score_checks += 1
    for box in [((0.6, 0.8),) * 3, ((0, 0.2),) * 3,
                ((1 / 3 + 1e-13, 0.5),) * 3]:
        try:
            score_bounds(box, (1, 0, -1))
        except ValueError:
            pass
        else:
            raise AssertionError("An empty probability region was accepted")

    # Training/target assay fixture is synthetic and uses one known denominator
    # per cell. No held-out selected outcomes enter build_predictors.
    training = []
    for j in range(4):
        training.append({
            "baseline_counts": [30 + j, 20 + 2 * j, 10 + j],
            "recovery_baseline": [[20, 30], [22, 30], [19, 30]],
            "recovery_selected": [[18, 30], [24, 30], [17, 30]],
            "establishment": [[5 + j, 20], [7 + j, 20], [10 - j, 20]],
            "selected_counts": [15 + 3 * j, 18 + j, 17 - j]
        })
    target = {
        "baseline_counts": [33, 26, 12],
        "recovery_baseline": [[20, 30], [22, 30], [19, 30]],
        "recovery_selected": [[18, 30], [24, 30], [17, 30]],
        "establishment": [[9, 20], [8, 20], [6, 20]]
    }
    prediction = build_predictors(training, target)
    for p in prediction["probabilities"].values():
        assert min(p) > 0
        assert_close(math.fsum(p), 1)
    assert build_predictors(training, dict(target, selected_counts=[999, 0, 0])) == prediction
    target_baseline = smooth_triad(target["baseline_counts"])
    target_qstar = normalize([
        target_baseline[i] * smooth_binary(*target["recovery_selected"][i]) /
        smooth_binary(*target["recovery_baseline"][i]) for i in range(3)])
    assert_close(direction_eta(prediction["probabilities"]["flexible"], target_qstar), prediction["eta"])
    theta_cells, x_cells = [], []
    for row in training:
        b = smooth_triad(row["baseline_counts"])
        q = normalize([b[i] * smooth_binary(*row["recovery_selected"][i]) /
                       smooth_binary(*row["recovery_baseline"][i]) for i in range(3)])
        f = [smooth_binary(*cell) for cell in row["establishment"]]
        theta_cells.append(contrast_theta(smooth_triad(row["selected_counts"]), q))
        x_cells.append(math.log(f[0] / f[2]) / 2)
    theta_intercept, theta_slope = ridge(x_cells, theta_cells)
    assert_close(contrast_theta(prediction["probabilities"]["flexible"], target_qstar),
                 theta_intercept + theta_slope * prediction["feature"])
    assert ridge([1, 1], [2, 4]) == (3, 0)
    for call in (lambda: smooth_triad([0, 0, 0]), lambda: smooth_binary(0, 0),
                 lambda: ridge([float("nan")], [0]),
                 lambda: score_bounds([(0, 1)] * 3, [float("nan"), 0, 0])):
        try:
            call()
        except ValueError:
            pass
        else:
            raise AssertionError("An inadmissible measurement was repaired silently")

    def rounded(value):
        if isinstance(value, float):
            return round(value, 12)
        if isinstance(value, dict):
            return {k: rounded(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [rounded(v) for v in value]
        return value

    return rounded({
        "schema_version": 1,
        "round_id": "R000003",
        "verification_kind": "synthetic_floating_mathematical_checks",
        "biological_observations": 0,
        "new_theorem_or_priority_claim": False,
        "certified_score_decision_engine": False,
        "registered_experiment": False,
        "checks": {
            "algebra_J_and_saturated_reconstruction_cases": model_checks,
            "conditional_eta_cancellation_cases": conditional_checks,
            "conditional_degenerate_support_checked": True,
            "pooling_symmetry_case_checked": True,
            "recovery_artifact_and_same_J_different_probabilities_checked": True,
            "score_projection_explicit_vertex_cases": score_checks,
            "empty_probability_regions_rejected": True,
            "raw_zero_count_endpoints_preserved": True,
            "finite_multinomial_coverage_example_checked": True,
            "frozen_target_prediction_and_missing_denominator_guards_checked": True,
            "nonfinite_score_inputs_rejected": True,
            "flexible_predictor_same_eta_feature_varying_theta_identity_checked": True
        },
        "illustrative_values": {
            "pooled_theta_at_uniform_q_theta0_eta_plusminus1": pooled_theta,
            "recovery_artifact_theta": math.log(1.5),
            "recovery_artifact_J": 2.25,
            "weak_oracle_gain_nats": weak_oracle_gain,
            "finite_multinomial_CP_Bonferroni_coverage": finite_example_coverage,
            "synthetic_frozen_prediction": prediction
        }
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    result = verify()
    path = ROOT / "VERIFICATION_RECEIPT.json"
    if args.check:
        if json.loads(path.read_text()) != result:
            raise SystemExit("Receipt differs from recomputed mathematical checks")
        print("PASS: synthetic mathematical checks and stored receipt agree")
    elif args.write_receipt:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print("Wrote synthetic verification receipt")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
