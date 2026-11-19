"""Measure sensitivity of the peach allocation excess to group deletions and outside support."""
import argparse
from collections import defaultdict
from fractions import Fraction
import json
from math import comb
from pathlib import Path


def rounded(number):
    value = float(number)
    return float(f"{value:.6g}") if 0 < abs(value) < 0.000000005 else round(value, 8)


def summarize(records):
    expected = sum((q for _, _, q, _ in records), Fraction())
    observed = sum(one_side for _, _, _, one_side in records)
    return {"eligible": len(records), "observed_one_sided": observed, "expected_one_sided": rounded(expected),
            "excess": rounded(observed - expected)}


def deletion_summary(groups, include_contributions=True):
    total = sum((int(obs) - p for rows in groups.values() for _, _, p, obs in rows), Fraction())
    scores = {name: sum((int(obs) - q for _, _, q, obs in rows), Fraction()) for name, rows in groups.items()}
    ordered = sorted(groups, key=lambda name: (-scores[name], name))
    # The best size-k deletion removes the k largest additive contributions. Ties are alphabetical.
    if total <= 0:
        raise ValueError("Deletion analysis expects a positive initial excess")
    minimum = None
    for k in range(1, len(ordered)):
        # Reserve a group with an informative observation. For a fixed reserve the best
        # deletion is the top k among all other groups, by additivity.
        best = None
        for reserve in ordered:
            if not any(0 < row[2] < 1 for row in groups[reserve]):
                continue
            removed = tuple(g for g in ordered if g != reserve)[:k]
            excess = total - sum(scores[g] for g in removed)
            if best is None or (excess, removed) < best:
                best = (excess, removed)
        if best is None:
            break
        excess, removed = best
        if excess <= 0:
            kept = [r for g in groups if g not in removed for r in groups[g]]
            minimum = {"groups_removed": k, "witness": list(removed),
                       "smallest_excess_after_one_fewer_removal": rounded(previous if k > 1 else total),
                       "retained": summarize(kept)}
            break
        previous = excess
    result = {
        "total_groups": len(groups), "groups_with_eligible_rows": sum(bool(v) for v in groups.values()),
        "positive_negative_zero_group_counts": [sum(s * sign > 0 for s in scores.values()) for sign in (1, -1)]
                                              + [sum(s == 0 for s in scores.values())],
        "positive_group_excess_sum": rounded(sum(s for s in scores.values() if s > 0)),
        "negative_group_excess_sum": rounded(sum(s for s in scores.values() if s < 0)),
        "minimum_leave_one_out_excess": rounded(total - scores[ordered[0]]),
        "maximum_leave_one_out_excess": rounded(total - scores[ordered[-1]]),
        "minimum_groups_to_erase_excess_retaining_informative_cells": minimum,
    }
    if include_contributions:
        result["group_contributions"] = {key: summarize(groups[key]) for key in sorted(groups)}
    return result


def analyze(profile):
    organs = profile["organ_by_tissue"]
    evidence = profile["other_library_evidence_by_site"]
    site_groups = {site: [] for site in evidence}
    tissues = {tissue: [] for tissue in organs}
    organ_groups = defaultdict(list)
    records = []
    for tissue, site, a, b, k, obs in profile["eligible"]:
        q = Fraction(comb(a, k) + comb(b, k), comb(a + b, k))
        record = (tissue, site, q, obs)
        records.append(record)
        tissues[tissue].append(record)
        organ_groups[organs[tissue]].append(record)
        site_groups[site].append(record)
    filters = {}
    for min_count, min_libraries in [(1, 1), (2, 1), (1, 2), (5, 1)]:
        sites = {site for site, (max_alt, n_libs) in evidence.items()
                 if max_alt >= min_count and n_libs >= min_libraries}
        partitions = {}
        for name, subset in [("qualifying", sites), ("complement", set(evidence) - sites)]:
            kept = [row for row in records if row[1] in subset]
            partitions[name] = {"sites": len(subset), "eligible_sites": len({r[1] for r in kept}), **summarize(kept)}
        filters[f"max_alt_ge_{min_count}_and_positive_libraries_ge_{min_libraries}"] = partitions
    outside_five = {site for site, (largest, _) in evidence.items() if largest >= 5}
    restricted = {}
    for label, groups in [("site", site_groups), ("tissue", tissues), ("organ", organ_groups)]:
        retained = {g: [r for r in rows if r[1] in outside_five] for g, rows in groups.items()
                    if label != "site" or g in outside_five}
        restricted[label] = deletion_summary(retained, include_contributions=False)
    return {
        "selection": "Flower #2 split-tissue comparisons with at least two pooled alternate reads.",
        "full": summarize(records),
        "group_deletions": {name: deletion_summary(groups) for name, groups in
                            [("site", site_groups), ("tissue", tissues), ("organ", organ_groups)]},
        "support_in_30_other_flower_libraries": filters,
        "deletions_at_sites_with_five_reads_in_another_library": restricted,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profiles", type=Path, nargs="?", default=Path(__file__).with_name("influence_profiles.json"))
    print(json.dumps(analyze(json.loads(parser.parse_args().profiles.read_bytes())), indent=2))
