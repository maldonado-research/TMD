"""Independent workbook check of the five-read site-level proxy in Ji et al."""
import argparse
import hashlib
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

from openpyxl import load_workbook


DIGEST = "80774928a21b4aaa717e5c87afdb3d01aae9d8392b1cbfc23e542358ff292d6f"
SITES = [f"M{i}" for i in range(21, 58)]


def divide_read_positions(a, b, k):
    """Enumerate alternate counts in half A using ratios of consecutive weights."""
    start, stop = max(0, k - b), min(a, k)
    weights = []
    weight = Fraction(1)
    for x in range(start, stop + 1):
        weights.append((x, k-x, weight))
        if x < stop:
            weight *= Fraction((a-x)*(k-x), (x+1)*(b-k+x+1))
    return weights


def one_sided_probability(outcomes):
    total = sum(weight for _, _, weight in outcomes)
    one_sided = sum(weight for x, y, weight in outcomes if min(x, y) == 0)
    return one_sided / total


def check(path):
    if hashlib.sha256(path.read_bytes()).hexdigest() != DIGEST:
        raise ValueError("Unexpected Ji Table S3 digest")
    book = load_workbook(path, data_only=True, read_only=True)
    try:
        rows = list(book["S3_Table"].values)
    finally:
        book.close()
    header = rows[3]
    split = header.index("Splitsample")
    # The sheet juxtaposes two subject blocks with duplicated metadata headings.
    assert header[split-3:split+2] == ("Group", "Organ", "Unit", "Splitsample", "Sample")
    records = [row for row in rows[4:] if row[split-3] == "Flower#2"]
    split_members = defaultdict(list)
    for row in records:
        split_members[row[split]].append(row)
    unsplit = split_members.pop(None)
    assert len(unsplit) == 30 and len(split_members) == 20
    assert all(len(rows) == 2 for rows in split_members.values())
    assert len({row[split+1] for row in records}) == len(records) == 70

    totals = {}
    sensitive = []
    max_exactly_five = []
    for site in SITES:
        ref, alt = header.index(site+"_Ref"), header.index(site+"_Alt")
        outside_pass = any(row[alt] >= 5 for row in unsplit)
        assert all(type(row[c]) is int and row[c] >= 0 for row in records for c in (ref, alt))
        max_alt = max(row[alt] for row in records)
        assert max_alt >= 5
        if max_alt == 5:
            max_exactly_five.append(site)
        possible, guaranteed = [], outside_pass
        scored = {}
        for pair, halves in split_members.items():
            x,y = [row[alt] for row in halves]
            a,b = [row[alt] + row[ref] for row in halves]
            assert min(a, b) > 0
            k = x+y
            if k < 2:
                continue
            allocations = divide_read_positions(a,b,k)
            retained = [(u,v,w) for u,v,w in allocations if max(u,v) >= 5]
            if retained:
                possible.append(pair)
            guaranteed |= len(retained) == len(allocations)
            scored[pair] = (min(x,y) == 0, one_sided_probability(allocations), retained)

        raw = sum((q for _,q,_ in scored.values()), Fraction(0))
        observed = sum(o for o,_,_ in scored.values())
        adjusted = raw
        if not guaranteed:
            # This identity is specific to the eight affected sites in this workbook.
            assert len(possible) == 1 and set(possible) == set(scored)
            adjusted = one_sided_probability(scored[possible[0]][2])
            sensitive.append(dict(site=site, one_sided=observed,
                                  screen_forces_one_sided=(adjusted == 1)))
        for group in ("all","outside_pass" if outside_pass else "outside_below_five",
                      "guaranteed" if guaranteed else "allocation_sensitive"):
            count = totals.setdefault(group,[0,0,0,Fraction(0),Fraction(0)])
            for j, value in enumerate([1,len(scored),observed,raw,adjusted]):
                count[j] += value
    assert len(sensitive) == 8 and sum(x["screen_forces_one_sided"] for x in sensitive) == 4
    return {"source_table_S3_sha256": DIGEST,
            "five_read_proxy": "One Flower #2 library contains at least five deposited alternate reads.",
            "distinguishable_groups": {g: {"sites": n, "comparisons": m, "observed_one_sided": o,
                "raw_expected": round(float(raw),8), "site_local_screen_expected": round(float(adj),8)}
                for g,(n,m,o,raw,adj) in totals.items()},
            "retained_sites_maximum_exactly_five": max_exactly_five,
            "allocation_sensitive_sites": sensitive}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("table_s3",type=Path)
    args = parser.parse_args()
    print(json.dumps(check(args.table_s3), indent=2))
