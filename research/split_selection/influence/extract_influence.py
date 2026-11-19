"""Join Ji et al. Tables S2, S3 and S5 and export aggregate read profiles for Flower #2."""
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
from openpyxl import load_workbook

SOURCES = {
    "S2": ("016", "b101c5288f34ca8853d2dd8592b1fd80e1ea4347a96dc049913693ca79302fa4"),
    "S3": ("017", "80774928a21b4aaa717e5c87afdb3d01aae9d8392b1cbfc23e542358ff292d6f"),
    "S5": ("019", "a37bcda6a357e779840974bd8cf51bb526db863bb689013eac02f28c076e4394"),
}


def read_book(path, key):
    if sha256(path.read_bytes()).hexdigest() != SOURCES[key][1]:
        raise ValueError(f"Original source digest differs for {key}")
    book = load_workbook(path, read_only=True, data_only=True)
    try:
        return list(book[f"{key}_Table"].values)
    finally:
        book.close()


def read_profile(row, index, state):
    ref, alt = row[index:index + 2]
    if any(type(n) is not int or n < 0 for n in (ref, alt)) or ref + alt == 0:
        raise ValueError("Read counts expected with positive reference-plus-alternate depth")
    if row[index + 2] != state[int(alt > 0)]:
        raise ValueError("Reported base and alternate read evidence differ")
    return ref + alt, alt


def extract(s2, s3, s5):
    states = {r[0]: (r[5], r[6]) for r in s2[5:] if r[1] == "Flower#2"}
    sites = [site for site in s5[3][3:] if site is not None]
    if set(sites) != set(states) or len(sites) != 37 or s5[3][:3] != ("Pair", "Subsample", "Name"):
        raise ValueError("Flower #2 site inventory differs")
    offset = s3[3].index("Splitsample") - 4
    header = s3[3][offset:]
    if header[:6] != ("Sort", "Group", "Organ", "Unit", "Splitsample", "Sample"):
        raise ValueError("Unexpected Flower #2 read-count block")
    columns = {site: header.index(site + "_Ref") for site in sites}
    for site, col in columns.items():
        if header[col:col + 3] != (site + "_Ref", site + "_Alt", site):
            raise ValueError("Source read-count columns differ")
    flower = [r[offset:] for r in s3[4:] if r[offset + 1] == "Flower#2"]
    samples = {r[5]: r for r in flower}
    if len(samples) != len(flower):
        raise ValueError("Flower #2 libraries repeat")
    pairs = defaultdict(dict)
    for row in s5[4:]:
        pair, side, name = row[:3]
        if side not in ("a", "b"):
            continue
        source = samples[name]
        if (source[4] != pair or side in pairs[pair] or
                any(source[columns[site]+2] != row[3+j] for j, site in enumerate(sites))):
            raise ValueError("Source split roster or call differs")
        pairs[pair][side] = name
    split = {name for members in pairs.values() for name in members.values()}
    outside = [r for r in flower if r[5] not in split]
    if (len(pairs) != 20 or len(split) != 40 or len(outside) != 30
            or any(set(x) != {"a", "b"} for x in pairs.values()) or any(r[4] is not None for r in outside)):
        raise ValueError("Unexpected split and non-split frames")
    other_evidence = {}
    for site in sites:
        alts = [read_profile(r, columns[site], states[site])[1] for r in outside]
        other_evidence[site] = [max(alts), sum(n > 0 for n in alts)]
    organs = {}
    rows = []
    k_counts = Counter()
    for pair, members in pairs.items():
        a, b = samples[members["a"]], samples[members["b"]]
        if a[2:4] != b[2:4]:
            raise ValueError("Source tissue halves differ in organ or unit")
        organs[pair] = a[2]
        for site in sites:
            depth_a, alt_a = read_profile(a, columns[site], states[site])
            depth_b, alt_b = read_profile(b, columns[site], states[site])
            k = alt_a + alt_b
            k_counts[min(2, k)] += 1
            if k >= 2:
                rows.append([pair, site, depth_a, depth_b, k, min(alt_a, alt_b) == 0])
    return {
        "article": "https://doi.org/10.1371/journal.pgen.1011829",
        "source_workbooks": {key: {"sha256": digest, "url": f"https://pmc-oa-opendata.s3.amazonaws.com/PMC12370204.1/pgen.1011829.s{suffix}.xlsx"}
                             for key, (suffix, digest) in SOURCES.items()},
        "organ_by_tissue": organs, "other_flower_libraries": len(outside),
        "other_library_fields": ["largest_alternate_count_in_one_library", "libraries_with_positive_alternate_count"],
        "other_library_evidence_by_site": other_evidence,
        "pooled_alternates_0_1_ge2": [k_counts[n] for n in range(3)],
        "eligible_fields": ["tissue", "site", "depth_a", "depth_b", "pooled_alternate", "one_sided"],
        "eligible": rows,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for book in SOURCES:
        parser.add_argument(book.lower(), type=Path)
    args = parser.parse_args()
    print(json.dumps(extract(*(read_book(getattr(args, k.lower()), k) for k in SOURCES)), indent=2))
