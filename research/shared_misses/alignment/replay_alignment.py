"""Compare matched split-tissue calls with alternate within-organ pairings in one flower."""
import argparse
import hashlib
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import permutations
import json
from math import factorial, prod
from pathlib import Path

from openpyxl import load_workbook


WORKBOOKS = {
    "S1": ("015", "ae7b0fabfb402c26518c49fef0a5e7a47ac0d2383a6168085fbee27e4d201227"),
    "S2": ("016", "b101c5288f34ca8853d2dd8592b1fd80e1ea4347a96dc049913693ca79302fa4"),
    "S5": ("019", "a37bcda6a357e779840974bd8cf51bb526db863bb689013eac02f28c076e4394"),
}


def read_table(path, key):
    if hashlib.sha256(path.read_bytes()).hexdigest() != WORKBOOKS[key][1]:
        raise ValueError(f"Source {key} checksum differs")
    book = load_workbook(path, read_only=True, data_only=True)
    try:
        return list(book[f"{key}_Table"].values)
    finally:
        book.close()


def read_pairs(s1, s2, s5):
    field = {name: s1[2].index(name) for name in ("Sample_ID", "Group", "Unit", "SplitSample")}
    groups = {}
    for row in s1[3:]:
        group, pair = row[field["Group"]], row[field["SplitSample"]]
        if not str(group).startswith("Flower#2_") or not str(pair).startswith("Pair"):
            continue
        key = row[field["Sample_ID"]]
        if key in groups:
            raise ValueError("Duplicate split sample in S1")
        groups[key] = (group.removeprefix("Flower#2_"), row[field["Unit"]], pair)
    if s2[4][5:7] != ("Ref", "Alt") or s5[3][:3] != ("Pair", "Subsample", "Name"):
        raise ValueError("Source headers differ")
    key_rows = [r for r in s2[5:] if r[1] == "Flower#2"]
    states = {r[0]: r[5:7] for r in key_rows}
    sites = [i for i in s5[3][3:] if i]
    if len(key_rows) != 37 or len(sites) != 37 or set(sites) != states.keys():
        raise ValueError("Candidate IDs differ between S2 and S5")
    by_pair = defaultdict(dict)
    seen = set()
    for row in s5[4:]:
        pair, split, name = row[:3]
        if split not in ("a", "b"):
            continue
        organ, unit, expected_pair = groups[name]
        if pair != expected_pair or name in seen or split in by_pair[pair]:
            raise ValueError("Ambiguous S1–S5 pairing")
        profile = set()
        for site, value in zip(sites, row[3:3 + len(sites)]):
            ref, alt = states[site]
            if value not in (ref, alt) or ref == alt:
                raise ValueError("Unrecognized call")
            if value == alt:
                profile.add(site)
        by_pair[pair][split] = (organ, unit, profile)
        seen.add(name)
    if seen != groups.keys() or len(by_pair) != 20:
        raise ValueError("S1 and S5 split-tissue frames differ")
    rows = []
    for members in by_pair.values():
        first, second = members["a"], members["b"]
        if first[:2] != second[:2]:
            raise ValueError("Pair spans tissue units")
        rows.append((*first[:2], first[2], second[2]))
    return rows


def convolve(x, y):
    totals = Counter()
    for i, ni in x.items():
        for j, nj in y.items():
            totals[i + j] += ni * nj
    return totals


def group_distribution(profiles):
    """Permute entire labeled B profiles and retain multiplicities even for identical profiles."""
    n = len(profiles)
    scores = [[len(a & b) for _, b in profiles] for a, _ in profiles]
    observed = sum(scores[i][i] for i in range(n))
    hist = Counter()
    unchanged = Counter()
    highest = -1
    for assignment in permutations(range(n)):
        score = sum(scores[i][j] for i, j in enumerate(assignment))
        hist[score] += 1
        if score > highest:
            highest = score
            unchanged.clear()
        if score == highest:
            unchanged[sum(i == j for i, j in enumerate(assignment))] += 1
    return observed, hist, unchanged


def alignment(rows, by_unit):
    groups = defaultdict(list)
    for organ, unit, a, b in rows:
        key = (organ, unit) if by_unit else organ
        groups[key].append((a, b))
    totals = Counter({0: 1})
    unchanged = Counter({0: 1})
    identity = 0
    for profiles in groups.values():
        observed, hist, max_matches = group_distribution(profiles)
        totals = convolve(totals, hist)
        unchanged = convolve(unchanged, max_matches)
        identity += observed
    n = sum(totals.values())
    above = sum(count for score, count in totals.items() if score >= identity)
    sizes = [len(pairs) for pairs in groups.values()]
    if n != prod(factorial(size) for size in sizes) or sum(unchanged.values()) != totals[max(totals)]:
        raise ValueError("Alignment frequency check failed")
    return {
        "group_sizes": sorted(sizes), "labeled_reassignments": n,
        "recorded_pairing_double_positives": identity,
        "minimum": min(totals), "maximum": max(totals),
        "mean": str(Fraction(sum(score * count for score, count in totals.items()), n)),
        "at_least_observed": above, "reference_fraction": str(Fraction(above, n)),
        "score_counts": dict(sorted(totals.items())),
        "correct_pair_counts_among_maximizers": dict(sorted(unchanged.items())),
    }


def replay(s1_path, s2_path, s5_path):
    rows = read_pairs(read_table(s1_path, "S1"), read_table(s2_path, "S2"), read_table(s5_path, "S5"))
    wide = set.intersection(*(a | b for _, _, a, b in rows))
    summary = {}
    for name, omitted in [("all_sites", set()), ("excluding_two_widely_detected_sites", wide)]:
        kept = [(g, u, a - omitted, b - omitted) for g, u, a, b in rows]
        sum_a = Counter(s for _, _, a, _ in kept for s in a)
        sum_b = Counter(s for _, _, _, b in kept for s in b)
        summary[name] = {
            "sites_retained": 37 - len(omitted),
            "positive_calls": {"a": sum(sum_a.values()), "b": sum(sum_b.values())},
            "mean_unrestricted_whole_profile_reassignment":
                str(Fraction(sum(x * sum_b[s] for s, x in sum_a.items()), len(kept))),
            "organ_type": alignment(kept, False), "organ_type_and_unit": alignment(kept, True),
        }
    return {
        "article": "https://doi.org/10.1371/journal.pgen.1011829",
        "source_workbooks": {k: {"url": f"https://pmc-oa-opendata.s3.amazonaws.com/PMC12370204.1/pgen.1011829.s{n}.xlsx",
                                "sha256": digest} for k, (n, digest) in WORKBOOKS.items()},
        "flower": 2, "split_tissues": len(rows),
        "organ_pair_counts": dict(sorted(Counter(g for g, _, _, _ in rows).items())),
        "reference_rule": "All labeled B tissue profiles reallocated once within each group. A profiles stay fixed.",
        "wide_site_rule": "Call in at least one split in every tissue using documented matching.",
        **summary,
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("s1", "s2", "s5"):
        p.add_argument(key, type=Path)
    arg = p.parse_args()
    print(json.dumps(replay(arg.s1, arg.s2, arg.s5), indent=2))
