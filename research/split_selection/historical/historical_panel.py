"""Extract and score the two explicitly prior-study markers displayed in Ji Table S7."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
import json
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = "https://doi.org/10.1371/journal.pgen.1011829.s021"
DIGESTS = {
    "S2": "b101c5288f34ca8853d2dd8592b1fd80e1ea4347a96dc049913693ca79302fa4",
    "S3": "80774928a21b4aaa717e5c87afdb3d01aae9d8392b1cbfc23e542358ff292d6f",
    "S5": "a37bcda6a357e779840974bd8cf51bb526db863bb689013eac02f28c076e4394",
}


def workbook(path):
    from openpyxl import load_workbook

    book = load_workbook(path, read_only=True, data_only=True)
    try:
        return list(book.active.values)
    finally:
        book.close()


def s7_rows(path):
    if path.suffix.lower() == ".xlsx":
        return workbook(path)
    return [[c.strip() for c in line.strip().strip("|").split("|")]
            for line in path.read_text().splitlines() if line.startswith("|")]


def extract(s2, s3, s5, s7):
    tables = {}
    for name, path in (("S2", s2), ("S3", s3), ("S5", s5)):
        if sha256(path.read_bytes()).hexdigest() != DIGESTS[name]:
            raise ValueError(f"Unexpected {name} workbook checksum")
        tables[name] = workbook(path)
    s2 = tables["S2"]
    meta = {r[0]: r for r in s2[5:] if r[0]}
    if s2[4][5:7] != ("Ref", "Alt") or s2[4][12] != "Citation":
        raise ValueError("Unexpected S2 columns")
    prior = [site for site, r in meta.items() if r[12] == "Wang et al. 2019"]
    rows = s7_rows(s7)
    h = next(r for r in rows if list(r[:4]) == ["#", "Year", "Group", "Sample ID"])
    end = max(i for i, val in enumerate(h) if val not in ("", None)) + 1
    columns = {h[i].split("_")[0]: i for i in range(4, end, 3)}
    if len(prior) != 48 or len(columns) != 8:
        raise ValueError("Unexpected inventory of candidate sites")
    selected = [site for site in prior if site in columns]
    if selected != ["M71", "M101"] or [site for site in prior if meta[site][10] == "Yes"] != selected:
        raise ValueError("Displayed prior-study inventory differs from S2 records")
    s7_samples = [r for r in rows if r and str(r[0]).isdigit()]
    by_name = {r[3]: r for r in s7_samples}
    if len(by_name) != len(s7_samples) or len(by_name) != 187:
        raise ValueError("Unexpected S7 library roster")
    flower = tables["S3"]
    split = flower[3].index("Splitsample")
    s3_samples = {r[split + 1]: r for r in flower[4:] if r[split] and r[split - 3] == "Flower#2"}
    pairs = defaultdict(dict)
    crosschecks = 0
    result = {site: [] for site in selected}
    for row in tables["S5"][4:]:
        pair, side, name = row[:3]
        if side not in ("a", "b"):
            continue
        s7_row = by_name[name]
        if side in pairs[pair] or "Flower#2" not in s7_row[2] or str(s7_row[1]) != "2019":
            raise ValueError("Invalid split pair or S7 provenance")
        pairs[pair][side] = s7_row
        for site in ("M21", "M42"):
            i, j = flower[3].index(site + "_Ref"), columns[site]
            if tuple(int(v) for v in s7_row[j:j+2]) != s3_samples[name][i:i+2]:
                raise ValueError("Overlapping S3 and S7 counts differ")
            crosschecks += 1
    if len(pairs) != 20 or any(set(m) != {"a", "b"} for m in pairs.values()):
        raise ValueError("Unexpected S5 pairs")
    for site in selected:
        j = columns[site]
        if list(h[j:j+2]) != [site + "_" + state for state in meta[site][5:7]]:
            raise ValueError("Historical site alleles differ between S2 and S7")
        for pair, sides in pairs.items():
            counts = [int(n) for side in "ab" for n in sides[side][j:j+2]]
            if min(counts) < 0:
                raise ValueError("Invalid read count")
            result[site].append([pair, *counts])
    return {"s7_source": SOURCE, "s2_s3_s5_sha256": DIGESTS, "prior_sites_attributed_in_s2": len(prior),
            "s7_displayed_markers": list(columns), "displayed_prior_sites": selected,
            "s7_sample_rows": len(by_name), "s3_s7_matching_control_counts_by_sample_and_site": crosschecks,
            "row_fields": ["tissue_pair", "a_ref", "a_alt", "b_ref", "b_alt"], "rows": result}


def summarize(rows):
    expected = Fraction()
    exclusions = Counter()
    cases = []
    for pair, ar, aa, br, ba in rows:
        a, b, k = ar + aa, br + ba, aa + ba
        if min(a, b) == 0:
            exclusions["zero_depth"] += 1
        elif k < 2:
            exclusions["zero_or_one_alternate"] += 1
        else:
            q = Fraction(comb(a, k) + comb(b, k), comb(a + b, k))
            expected += q
            if min(aa, ba) == 0:
                cases.append({"pair": pair, "depth_a": a, "depth_b": b, "alt_a": aa, "alt_b": ba})
    return {"frame": len(rows), "zero_depth": exclusions["zero_depth"],
            "zero_or_one_alternate": exclusions["zero_or_one_alternate"],
            "eligible": len(rows) - sum(exclusions.values()), "observed_one_sided": len(cases),
            "expected_one_sided": round(float(expected), 12), "one_sided_rows": cases}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--extract", nargs=4, type=Path, metavar=("S2", "S3", "S5", "S7"),
                   help="use the publisher workbook or the displayed S7 Markdown table")
    p.add_argument("--profiles", type=Path, default=HERE / "historical_profiles.json")
    args = p.parse_args()
    if args.extract:
        info = extract(*args.extract)
    else:
        data = json.loads(args.profiles.read_bytes())["rows"]
        info = {"by_marker": {k: summarize(rows) for k, rows in data.items()},
                "both_markers": summarize([r for rows in data.values() for r in rows])}
    print(json.dumps(info, indent=2))
