#!/usr/bin/env python3
"""Offline source-anchor and exact counterexample audit. Original code: MIT."""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
SOURCE_BYTES = 126193
SOURCE_SHA256 = "8e86d14d30a55fa672ec950379d03a7d3b57df2ece2ea297f2b5720fb09c7cb4"


def verify(source_path):
    passed = []

    def check(condition, label):
        if not condition:
            raise ValueError(label)
        passed.append(label)

    names = ("CLASSIFICATION_COUNTEREXAMPLE.json", "SLST_SOURCE_REVIEW.json")
    raw = {name: (HERE / name).read_bytes() for name in names}
    record, source_review = (json.loads(raw[name]) for name in names)
    matrix = ((F(1, 2), F(0), F(0)), (F(1, 2), F(1), F(0)), (F(0), F(0), F(1)))
    baseline, selected = (F(1, 3),) * 3, (F(4, 7), F(2, 7), F(1, 7))

    def observed(vector):
        return tuple(sum(matrix[j][i] * vector[i] for i in range(3)) for j in range(3))

    def normalize(vector):
        return tuple(v / sum(vector) for v in vector)

    def contrast(p, q):
        return p[1] ** 2 * q[0] * q[2] / (p[0] * p[2] * q[1] ** 2)

    def recovery_factor(r0, r1):
        u = tuple(a / b for a, b in zip(r1, r0))
        return u[1] ** 2 / (u[0] * u[2])

    call = tuple(sum(matrix[j][i] for j in range(3)) for i in range(3))
    correct = tuple(matrix[i][i] for i in range(3))
    b_obs, p_obs = observed(baseline), observed(selected)
    gold = lambda vector: normalize(tuple(vector[i] * correct[i] for i in range(3)))
    dropout = F(3, 5)
    expected = {
        "biological_J_context1": str(contrast(baseline, baseline)),
        "biological_J_context2": str(contrast(selected, baseline)),
        "same_confusion_matrix_all_phases_and_contexts": [list(map(str, row)) for row in matrix],
        "observed_baseline_both_contexts": list(map(str, b_obs)),
        "observed_selected_context2": list(map(str, p_obs)),
        "observed_J_context1": str(contrast(b_obs, b_obs)),
        "observed_J_context2": str(contrast(p_obs, b_obs)),
        "physical_recovery_all_one": all(v == 1 for v in call),
        "classification_is_not_phase_specific_diagonal_recovery": any(matrix[j][i] for j in range(3) for i in range(3) if j != i),
        "total_callable_probability_by_true_route": list(map(str, call)),
        "correctly_assigned_probability_by_true_route": list(map(str, correct)),
        "both_phase_ratio_vectors_equal_one": all(v / v == 1 for v in call + correct),
        "recovery_only_t_from_total_callability": str(recovery_factor(call, call) / recovery_factor(call, call)),
        "recovery_only_t_from_diagonal_correct_call_rates": str(recovery_factor(correct, correct) / recovery_factor(correct, correct)),
        "additional_route_independent_callable_fraction_example": str(dropout),
        "route_independent_dropout_preserves_conditional_observed_probabilities": all(normalize(tuple(dropout * z for z in v)) == v for v in (b_obs, p_obs)),
    }
    required = set(list(expected)[:7])
    for key, value in expected.items():
        if key in required or key in record:
            check(record.get(key) == value, "counterexample:" + key)
    if "if_gold_standard_excludes_wrong_route_calls" in record:
        gold_record = record["if_gold_standard_excludes_wrong_route_calls"]
        for key, value in {"baseline": list(map(str, gold(baseline))), "selected_context2": list(map(str, gold(selected))), "observed_J_context2": str(contrast(gold(selected), gold(baseline)))}.items():
            check(gold_record.get(key) == value, "adjudication:" + key)
    check(contrast(selected, baseline) == 1 and contrast(p_obs, b_obs) == F(16, 9), "exact_classification_counterexample")

    source_result = {"status": "UNRUN_SOURCE_NOT_SUPPLIED", "anchors_checked": 0}
    if source_path is not None:
        source = source_path.read_bytes()
        digest = hashlib.sha256(source).hexdigest()
        check(len(source) == SOURCE_BYTES and digest == SOURCE_SHA256, "source_bytes_and_sha256")
        check(source_review["source"]["bytes"] == SOURCE_BYTES and source_review["source"]["sha256"] == SOURCE_SHA256, "source_review_matches_pinned_identity")
        root = ET.fromstring(source)
        anchors = source_review["checks"]
        check(len(anchors) == 8 and len({a["id"] for a in anchors}) == 8, "eight_distinct_source_anchors")
        for anchor in anchors:
            section = root.find(".//sec[@id='" + anchor["section_id"] + "']")
            check(section is not None, "source_section:" + anchor["id"])
            text = " ".join(" ".join(section.itertext()).split())
            check(anchor["anchor"] in text, "source_anchor:" + anchor["id"])
        source_result = {"status": "PASS", "bytes": len(source), "sha256": digest, "anchors_checked": len(anchors)}
    return {"status": "PASS" if source_path else "PASS_COUNTEREXAMPLE_SOURCE_UNRUN", "counterexample": "PASS", "source": source_result, "checks_passed": passed, "check_count": len(passed), "input_sha256": {name: hashlib.sha256(data).hexdigest() for name, data in raw.items()}, "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "scope": "Exact synthetic arithmetic and source identity/text anchors only; no empirical recovery bound, biological validation, raw-data reanalysis or source fetch."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slst-source", type=Path, help="Optional previously acquired full JATS XML; never fetched.")
    parser.add_argument("--output", type=Path, help="Receipt destination; otherwise print JSON.")
    args = parser.parse_args()
    try:
        result = verify(args.slst_source)
        text = json.dumps(result, indent=2) + "\n"
        if args.output:
            args.output.write_text(text)
        else:
            print(text, end="")
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as error:
        # Do not expose source bodies or caller-supplied filesystem paths.
        print("Verification failed: " + type(error).__name__, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
