"""Conditional read-allocation benchmark on the observed split-positive peach comparisons."""
import argparse
import hashlib
import json
import math
import re
from collections import Counter
from fractions import Fraction
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
HASHES = {
    "S2": "b101c5288f34ca8853d2dd8592b1fd80e1ea4347a96dc049913693ca79302fa4",
    "S3": "80774928a21b4aaa717e5c87afdb3d01aae9d8392b1cbfc23e542358ff292d6f",
    "S5": "a37bcda6a357e779840974bd8cf51bb526db863bb689013eac02f28c076e4394",
}


def source_rows(path, name):
    """Read cells directly from a pinned original worksheet, indexed by row and column."""
    if hashlib.sha256(path.read_bytes()).hexdigest() != HASHES[name]:
        raise ValueError(f"{name} source hash differs")
    with ZipFile(path) as z:
        sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        strings = ["".join(t.text or "" for t in si.iterfind(".//{*}t"))
                   for si in ET.fromstring(z.read("xl/sharedStrings.xml"))]
    rows = {}
    for row in sheet.findall(".//{*}sheetData/{*}row"):
        values = {}
        for cell in row.findall("{*}c"):
            raw = cell.findtext("{*}v")
            if raw is None:
                continue
            col = re.match(r"[A-Z]+", cell.get("r")).group()
            values[col] = strings[int(raw)] if cell.get("t") == "s" else raw
        rows[int(row.get("r"))] = values
    return rows


def numeric_count(value):
    if not re.fullmatch(r"[0-9]+", value):
        raise ValueError("Expected nonnegative source read count")
    return int(value)


def extract(s2_path, s3_path, s5_path):
    s2, s3, s5 = [source_rows(path, name) for path, name in
                  [(s2_path, "S2"), (s3_path, "S3"), (s5_path, "S5")]]
    fields = {v: k for k, v in s2[5].items()}
    calls = {row[fields["ID"]]: (row[fields["Ref"]], row[fields["Alt"]])
             for row in s2.values() if row.get(fields["SampleLocation"]) == "Flower#2"}
    pairs = {}
    site_cols = {v: k for k, v in s5[4].items() if v in calls}
    if len(calls) != 37 or set(site_cols) != set(calls):
        raise ValueError("Mismatch in Flower 2 candidate sites")
    for row in s5.values():
        if row.get("B") not in ("a", "b"):
            continue
        members = pairs.setdefault(row["A"], {})
        if row["B"] in members:
            raise ValueError("Duplicate split record")
        members[row["B"]] = row
    if len(pairs) != 20 or any(set(members) != {"a", "b"} for members in pairs.values()):
        raise ValueError("Mismatch in split tissues")
    site_fields = {v: k for k, v in s3[4].items() if v in calls or v.split("_")[0] in calls}
    # The side-by-side blocks in S3 each have a Sample and Group header.
    sample_cols = [col for col, v in s3[4].items() if v == "Sample"]
    group_cols = [col for col, v in s3[4].items() if v == "Group"]
    has_pair = next(col for col, v in s3[4].items() if v == "Splitsample")
    wanted = {row["C"] for m in pairs.values() for row in m.values()}
    samples = {}
    for row in s3.values():
        if any(row.get(c) == "Flower#2" for c in group_cols):
            for col in sample_cols:
                name = row.get(col)
                if name in wanted:
                    if name in samples:
                        raise ValueError("Duplicate split read-count record")
                    samples[name] = row
    if set(samples) != wanted or len(samples) != 40:
        raise ValueError("Missing source sample")
    profiles = Counter()
    zeros = 0
    for pair_name, members in pairs.items():
        for site, col in site_cols.items():
            split_depths = []
            alt_counts = []
            for suffix in ("a", "b"):
                member = members[suffix]
                record = samples[member["C"]]
                ref = numeric_count(record[site_fields[site + "_Ref"]])
                alt = numeric_count(record[site_fields[site + "_Alt"]])
                if (ref + alt == 0 or record[has_pair] != pair_name
                        or record[site_fields[site]] != member[col]
                        or member[col] != calls[site][int(alt > 0)]):
                    raise ValueError("S2, S3 and S5 cross-check failed")
                split_depths.append(ref + alt)
                alt_counts.append(alt)
            k = sum(alt_counts)
            if k:
                low, high = sorted(split_depths)
                profiles[low, high, k, min(alt_counts) == 0] += 1
            else:
                zeros += 1
    return {
        "source_sha256": HASHES, "split_tissues": len(pairs), "ascertained_sites": len(calls),
        "double_reference_comparisons": zeros,
        "columns": ["smaller_depth", "larger_depth", "pooled_alternate_reads", "one_sided", "number_of_comparisons"],
        "positive_profiles": [[*profile, n] for profile, n in sorted(profiles.items())],
    }


def one_sided_probability(a, b, k):
    """Probability all k marked slots land in one half given two fixed depths."""
    if a <= 0 or b <= 0 or not 1 <= k <= a + b:
        raise ValueError("Invalid positive read-depth profile")
    return Fraction(math.comb(a, k) + math.comb(b, k), math.comb(a + b, k))


def summarize(profiles):
    count = observed = 0
    expected = Fraction()
    for a, b, k, one_sided, n in profiles:
        if type(one_sided) is not bool or type(n) is not int or n <= 0 or a > b:
            raise ValueError("Malformed anonymous profile")
        p = one_sided_probability(a, b, k)
        if p == 0 and one_sided or p == 1 and not one_sided:
            raise ValueError("Observed state impossible at these depths")
        expected += p * n
        count += n
        observed += n * one_sided
    return {"positive_comparisons": count, "observed_one_sided": observed,
            "expected_one_sided": round(float(expected), 8)}


def analyze(data):
    profiles = data["positive_profiles"]
    if (sum(p[-1] for p in profiles) + data["double_reference_comparisons"]
            != data["split_tissues"] * data["ascertained_sites"]):
        raise ValueError("Positive and double-reference comparison totals differ")
    levels = [("1", 1, 1), ("2", 2, 2), ("3", 3, 3), ("4-5", 4, 5), ("6-10", 6, 10),
              ("11 or more", 11, max(p[2] for p in profiles))]
    return {
        "unit": "An ascertained site in a split tissue with at least one recorded alternate read.",
        "all_positive": summarize(profiles),
        "two_or_more_alternate_reads": summarize([r for r in profiles if r[2] >= 2]),
        "by_pooled_alternate_reads": {label: summarize([r for r in profiles if lo <= r[2] <= hi])
                                      for label, lo, hi in levels},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extract", nargs=3, type=Path, metavar=("S2", "S3", "S5"),
                        help="emit anonymous read-depth profiles from the original workbooks")
    parser.add_argument("--profiles", type=Path, default=HERE / "allocation_profiles.json")
    args = parser.parse_args()
    output = extract(*args.extract) if args.extract else analyze(json.loads(args.profiles.read_bytes()))
    print(json.dumps(output, indent=2))
