"""Verify the paired tables by matching marginals and the classifier ceilings by exhaustive rules."""
import argparse
import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

CATEGORIES = ("W", "A", "M", "unmatched")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_matching(section):
    """Permute smooth categories over fixed wrinkly margins, testing all aggregate constraints."""
    margins = section["clones_by_phenotype_and_recorded_family"]
    wrinkly = tuple(Counter(margins["wrinkly"]).elements())
    smooth = tuple(Counter(margins["smooth"]).elements())
    require(len(wrinkly) == len(smooth) == section["parents"], "Invalid pair count.")
    require(section["pairs_with_any_recorded_family"]["both"]
            == sum(section["paired_clones_with_same_recorded_family"].values()),
            "Different double matches prevent the requested reconstruction.")
    possibilities = set()
    for assignment in set(itertools.permutations(smooth)):
        pairs = tuple(sorted(zip(wrinkly, assignment)))
        same = Counter(x for x, y in pairs if x == y and x != "unmatched")
        status = Counter()
        for x, y in pairs:
            statuses = {(True, True): "both", (False, False): "neither",
                        (True, False): "wrinkly_only", (False, True): "smooth_only"}
            status[statuses[(x != "unmatched", y != "unmatched")]] += 1
        if same == Counter(section["paired_clones_with_same_recorded_family"]) and (
            status == Counter(section["pairs_with_any_recorded_family"])
        ):
            possibilities.add(pairs)
    require(len(possibilities) == 1, "Cross-category table is not uniquely determined.")
    return next(iter(possibilities))


def verify_description(pairs, section):
    require(len(pairs) == section["parent_pairs"], "Parent count differs.")
    require(sum(x == y for x, y in pairs) == section["same_category_pairs"], "Agreement count differs.")
    counts = Counter(pairs)
    require([[counts[x, y] for y in CATEGORIES] for x in CATEGORIES] ==
            section["cross_category_counts"], "Cross-category matrix differs.")
    for label in CATEGORIES:
        indicators = Counter((x == label, y == label) for x, y in pairs)
        require([indicators[b] for b in ((True, True), (True, False), (False, True), (False, False))]
                == section["paired_binary_counts"][label], "Paired binary table differs.")


def exhaustive(records_by_parent, inputs):
    """Fit every deterministic rule, keeping whole pairs together for every holdout."""
    predictors = {key: i for i, key in enumerate(inputs)}
    correct_by_rule = []
    for rule in itertools.product((False, True), repeat=len(predictors)):
        correct_by_pair = [sum(rule[predictors[key]] == truth for key, truth in pair)
                           for pair in records_by_parent]
        correct_by_rule.append(correct_by_pair)
    totals = [sum(scores) for scores in correct_by_rule]
    held_score = Fraction(0)
    for i in range(len(records_by_parent)):
        training = [n - scores[i] for n, scores in zip(totals, correct_by_rule)]
        best = max(training)
        tie_scores = [scores[i] for n, scores in zip(training, correct_by_rule) if n == best]
        # Uniform averaging across training maximizers gives half credit on each tied or absent key.
        held_score += Fraction(sum(tie_scores), len(tie_scores))
    return max(totals), held_score, len(correct_by_rule)


def check_score(score, actual, size):
    require(size == actual["records"] and score == Fraction(actual["correct"]), "Score differs.")
    require(score / Fraction(size) == Fraction(actual["accuracy"]), "Accuracy differs.")
    require(size - score == Fraction(actual["shortfall_from_perfect_records"]), "Shortfall differs.")
    require((size - score) / Fraction(size) == Fraction(actual["shortfall_from_perfect_fraction"]),
            "Shortfall fraction differs.")


def verify(source, result):
    require(result["category_order"] == list(CATEGORIES), "Dimension order differs.")
    arms = {}
    for arm, section in source["arms"].items():
        pairs = unique_matching(section)
        arms[arm] = pairs
        by_context = result["by_recorded_context"][arm]
        verify_description(pairs, by_context)
        points = [((w, True), (s, False)) for w, s in pairs]
        best, loo, _ = exhaustive(points, CATEGORIES)
        check_score(best, by_context["apparent_ceiling"], 2 * len(pairs))
        require(loo == Fraction(by_context["leave_one_pair_out_expected_correct"]), "Arm holdout differs.")
    pooled = tuple(sorted(pair for pairs in arms.values() for pair in pairs))
    require(unique_matching(source["paired_roster_totals"]) == pooled, "Pooled receipt differs.")
    verify_description(pooled, result["pooled"])
    pooled_inputs = [((w, True), (s, False)) for w, s in pooled]
    context_inputs = [(((arm, w), True), ((arm, s), False))
                      for arm, pairs in arms.items() for w, s in pairs]
    rule_counts = {}
    for key, observations, inputs in (
        ("category_only", pooled_inputs, CATEGORIES),
        ("category_and_context", context_inputs, itertools.product(arms, CATEGORIES)),
    ):
        best, loo, n_rules = exhaustive(observations, inputs)
        rule_counts[key] = n_rules
        check_score(best, result["apparent_ceiling"][key], 2 * len(pooled))
        check_score(loo, result["leave_one_parent_out_retrospective_majority"][key], 2 * len(pooled))
    return {"verified": True, "rule_maps_enumerated": rule_counts, "whole_parent_holdouts": len(pooled),
            "unique_pair_table_per_context_and_pooled": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("result", type=Path)
    args = parser.parse_args()
    raw = args.receipt.read_bytes()
    result = json.loads(args.result.read_bytes())
    require(hashlib.sha256(raw).hexdigest() == result["aggregate_receipt_sha256"], "Receipt hash differs.")
    print(json.dumps(verify(json.loads(raw), result), indent=2))
