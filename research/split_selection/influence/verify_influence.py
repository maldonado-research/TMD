"""Independent product-probability and subset-recursion checks for the archived peach comparison."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product
import json
from math import isclose, prod
from pathlib import Path


def one_side(depth, other, marked):
    if marked > depth:
        return Fraction()
    return prod(Fraction(depth - i, depth + other - i) for i in range(marked))


def check_number(actual, reference):
    assert isclose(actual, float(reference), rel_tol=5e-6, abs_tol=5.01e-9)
    if reference != 0:
        assert actual * reference > 0


def check_subsets(labels, data, result):
    # Keep the minimum residual over groups processed, by number removed and whether
    # the retained records include at least one non-forced allocation.
    dp = {(0, False): Fraction()}
    contributions = {}
    for label in labels:
        rows = data[label]
        score = sum((obs - p for _, _, p, obs in rows), Fraction())
        contributions[label] = score
        informative = any(0 < p < 1 for _, _, p, _ in rows)
        after = {}
        for (removed, useful), value in dp.items():
            for key, residual in [((removed, useful or informative), value + score),
                                  ((removed + 1, useful), value)]:
                if key not in after or residual < after[key]:
                    after[key] = residual
        dp = after
    best_k = min(k for (k, good), v in dp.items() if good and v <= 0)
    report = result["minimum_groups_to_erase_excess_retaining_informative_cells"]
    assert best_k == len(set(report["witness"])) == report["groups_removed"]
    check_number(report["retained"]["excess"], dp[best_k, True])
    check_number(report["smallest_excess_after_one_fewer_removal"], dp[best_k - 1, True])
    check_number(report["retained"]["excess"], sum(val for g, val in contributions.items() if g not in report["witness"]))
    all_loo = [sum(contributions.values()) - score for score in contributions.values()]
    check_number(result["minimum_leave_one_out_excess"], min(all_loo))
    check_number(result["maximum_leave_one_out_excess"], max(all_loo))


def check(profile, result, previous):
    rows = []
    actual = Counter()
    for tissue, site, a, b, k, obs in profile["eligible"]:
        p = one_side(a, b, k) + one_side(b, a, k)
        assert 0 <= p <= 1 and (p > 0 or not obs) and (p < 1 or obs)
        rows.append((tissue, site, p, obs))
        actual[min(a, b), max(a, b), k, obs] += 1
    assert len({(t, s) for t, s, _, _ in rows}) == len(rows) == 64
    if previous is not None:
        expected = {tuple(row[:-1]): row[-1] for row in previous["positive_profiles"] if row[2] >= 2}
        assert expected == actual
    organs = profile["organ_by_tissue"]
    sites = profile["other_library_evidence_by_site"]
    for threshold, positives in [(1, 1), (2, 1), (1, 2), (5, 1)]:
        keep = {s for s in sites if sites[s][0] >= threshold and sites[s][1] >= positives}
        source = result["support_in_30_other_flower_libraries"][f"max_alt_ge_{threshold}_and_positive_libraries_ge_{positives}"]
        for mask, key in [(keep, "qualifying"), (set(sites) - keep, "complement")]:
            subset = [r for r in rows if r[1] in mask]
            r = source[key]
            assert r["sites"] == len(mask) and r["eligible"] == len(subset)
            assert r["observed_one_sided"] == sum(x[-1] for x in subset)
            check_number(r["expected_one_sided"], sum(x[2] for x in subset))
    for restricted, level in product((False, True), ("site", "tissue", "organ")):
        scope = {s for s, v in sites.items() if not restricted or v[0] >= 5}
        labels = {"site": scope, "tissue": set(organs), "organ": set(organs.values())}[level]
        data = defaultdict(list)
        for row in rows:
            tissue, site, _, _ = row
            if site in scope:
                data[{"site": site, "tissue": tissue, "organ": organs[tissue]}[level]].append(row)
        group_set = "deletions_at_sites_with_five_reads_in_another_library" if restricted else "group_deletions"
        check_subsets(labels, data, result[group_set][level])
    print("Verified 64 allocation profiles, eight outside-support strata and six group-deletion optimizations.")


if __name__ == "__main__":
    root = Path(__file__).parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--previous", type=Path, help="prior archive's allocation_profiles.json for a cross-check")
    previous = parser.parse_args().previous
    check(json.loads((root / "influence_profiles.json").read_bytes()), json.loads((root / "influence_result.json").read_bytes()),
          json.loads(previous.read_bytes()) if previous else None)
