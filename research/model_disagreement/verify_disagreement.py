#!/usr/bin/env python3
"""Independently check the hypothetical context-pair note through frozen code.

Run from the repository root: python -B research/model_disagreement/verify_disagreement.py --repo .

Standard library only. Reads but does not modify repository files. All records
below are synthetic, including the training fixture copied from verify_design.py.
This is a finite implementation/algebra check, not biological evidence, a power
calculation, a calibrated hypothesis test, or a change to the frozen candidate.
"""

import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import runpy


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def close(actual, expected, message):
    check(math.isclose(actual, expected, rel_tol=2e-14, abs_tol=2e-14), message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def kl(p, q):
    return math.fsum(float(a) * math.log(float(a) / float(b)) for a, b in zip(p, q))


def validate(repo):
    source = repo / "research/prospective_design/verify_design.py"
    receipt = source.parent / "VERIFICATION_RECEIPT.json"
    note = repo / "research/model_disagreement/README.md"
    before = {str(p.relative_to(repo)): sha256(p) for p in (source, receipt, note)}

    # run_path loads source directly, without creating a repository __pycache__.
    candidate = runpy.run_path(str(source), run_name="disagreement_candidate")
    check(candidate["verify"]() == json.loads(receipt.read_text()),
          "Frozen owner's verification receipt differs from its implementation")

    # Unchanged synthetic training fixture from prospective_design/verify_design.py.
    # Target selected endpoints are deliberately absent from both target records.
    training = []
    for j in range(4):
        training.append({
            "baseline_counts": [30 + j, 20 + 2 * j, 10 + j],
            "recovery_baseline": [[20, 30], [22, 30], [19, 30]],
            "recovery_selected": [[18, 30], [24, 30], [17, 30]],
            "establishment": [[5 + j, 20], [7 + j, 20], [10 - j, 20]],
            "selected_counts": [15 + 3 * j, 18 + j, 17 - j],
        })
    targets = [{
        "baseline_counts": [1, 1, 1],
        "recovery_baseline": [[20, 30], [20, 30], [20, 30]],
        "recovery_selected": [[20, 30], [20, 30], [20, 30]],
        "establishment": [[20, 100], [a, 100], [20, 100]],
    } for a in (10, 80)]
    predictions = [candidate["build_predictors"](training, row) for row in targets]

    for name in ("restricted", "flexible", "supply_observation"):
        check(predictions[0]["probabilities"][name] == predictions[1]["probabilities"][name],
              f"Changing only target F_A changed {name}")
    for prediction in predictions:
        check(prediction["feature"] == 0.0, "Expected exactly zero target x")
        for p in prediction["probabilities"].values():
            check(all(math.isfinite(v) and v > 0 for v in p), "Invalid frozen prediction")
            close(math.fsum(p), 1.0, "Frozen prediction does not normalize")

    # Reconstruct the note's point probabilities using exact integer arithmetic.
    # A binary (k+1/2)/(n+1) point is (2k+1)/(2(n+1)).
    exact_f = [tuple(Fraction(2 * k + 1, 2 * (n + 1))
                     for k, n in row["establishment"]) for row in targets]
    exact_p = [tuple(f / sum(fs) for f in fs) for fs in exact_f]
    expected_p = [tuple(Fraction(k, d) for k in ks)
                  for ks, d in (((41, 21, 41), 103), ((41, 161, 41), 243))]
    check(exact_p == expected_p, "Exact smoothing does not give the published fractions")
    check(exact_p[0] != exact_p[1], "Supply-establishment vectors must differ")
    for j, prediction in enumerate(predictions):
        actual = prediction["probabilities"]["supply_establishment_observation"]
        for a, b in zip(actual, exact_p[j]):
            close(a, float(b), "Full forecast builder disagrees with exact fractions")
        theta = math.log(float(exact_f[j][1])) - 0.5 * (
            math.log(float(exact_f[j][0])) + math.log(float(exact_f[j][2])))
        close(candidate["contrast_theta"](actual, (1 / 3,) * 3), theta,
              "qstar-adjusted curvature does not equal z")
        close(candidate["direction_eta"](actual, (1 / 3,) * 3), 0.0,
              "qstar-adjusted tilt does not equal x")
    exact_j = [p[1] ** 2 / (p[0] * p[2]) for p in exact_p]
    check(exact_j == [Fraction(441, 1681), Fraction(25921, 1681)],
          "Exact qstar-adjusted contrast differs from the note")

    mean = tuple((exact_p[0][i] + exact_p[1][i]) / 2 for i in range(3))
    check(mean == (Fraction(7093, 25029), Fraction(10843, 25029), Fraction(7093, 25029)),
          "Exact mixture mean differs from the note")
    js = (kl(exact_p[0], mean) + kl(exact_p[1], mean)) / 2
    check(abs(js - 0.111666761661) < 0.5e-12, "Oracle loss does not round to the note")
    common_predictions = {
        "uniform": (1 / 3,) * 3,
        "arbitrary": (0.1, 0.7, 0.2),
        "restricted": predictions[0]["probabilities"]["restricted"],
        "flexible": predictions[0]["probabilities"]["flexible"],
        "oracle_mean": tuple(map(float, mean)),
    }
    decomposition = {}
    for name, r in common_predictions.items():
        loss = (kl(exact_p[0], r) + kl(exact_p[1], r)) / 2
        excess = kl(mean, r)
        close(loss, js + excess, f"KL mixture decomposition failed for {name}")
        check(loss >= js - 2e-14, f"Common prediction beat the hypothetical oracle bound: {name}")
        decomposition[name] = {"average_loss_nats": loss, "excess_over_bound_nats": excess}

    check(before == {str(p.relative_to(repo)): sha256(p) for p in (source, receipt, note)},
          "An inspected repository source changed during verification")
    return {
        "status": "PASS",
        "scope": "synthetic implementation and algebra checks only",
        "biological_observations": 0,
        "frozen_candidate_changed": False,
        "inspected_sha256": before,
        "checks": {
            "owner_stored_receipt_matches_recomputed_checks": True,
            "full_builder_equal_restricted_flexible_supply_predictions": True,
            "full_builder_matches_exact_supply_establishment_fractions": True,
            "exact_smoothed_F_and_J_and_mixture_fractions": True,
            "curvature_z_and_tilt_x_identity": True,
            "KL_decomposition_common_predictions_checked": len(common_predictions),
        },
        "exact_smoothed_F": [list(map(str, fs)) for fs in exact_f],
        "exact_supply_establishment_vectors": [list(map(str, p)) for p in exact_p],
        "exact_J": list(map(str, exact_j)),
        "exact_mean": list(map(str, mean)),
        "hypothetical_oracle_JS_nats": js,
        "full_builder_predictions": predictions,
        "hypothetical_loss_decomposition": decomposition,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2],
                        help="Root of the TMD repository (default: containing repository)")
    args = parser.parse_args()
    print(json.dumps(validate(args.repo.resolve()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
