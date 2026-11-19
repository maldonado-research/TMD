"""Join Ji et al. Tables S2, S3, S5 and S6 for ascertained split-tissue pairs."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from statistics import median

from openpyxl import load_workbook


SOURCES = {
    "S2": ("016", "b101c5288f34ca8853d2dd8592b1fd80e1ea4347a96dc049913693ca79302fa4"),
    "S3": ("017", "80774928a21b4aaa717e5c87afdb3d01aae9d8392b1cbfc23e542358ff292d6f"),
    "S5": ("019", "a37bcda6a357e779840974bd8cf51bb526db863bb689013eac02f28c076e4394"),
    "S6": ("020", "3ed935d3f350ffd9d63f8e2e4bf0f8958a65bf438247d287776c5774dd6cc54b"),
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read_tables(paths):
    tables, provenance = {}, {}
    for name, path in zip(SOURCES, paths, strict=True):
        suffix, expected = SOURCES[name]
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        require(digest == expected, f"{name} differs from the published version")
        book = load_workbook(path, read_only=True, data_only=True)
        try:
            tables[name] = list(book[name + "_Table"].values)
        finally:
            book.close()
        provenance[name] = {
            "url": f"https://pmc-oa-opendata.s3.amazonaws.com/PMC12370204.1/pgen.1011829.s{suffix}.xlsx",
            "bytes": len(raw), "sha256": digest,
        }
    return tables, provenance


def unique_samples(rows, name_column):
    result = {row[name_column]: row for row in rows}
    require(len(result) == len(rows), "Duplicate subsample identifier")
    return result


def range_summary(values):
    return {"min": min(values), "median": median(values), "max": max(values)}


def analyze(tables):
    s2, s3, s5, s6 = (tables[name] for name in SOURCES)
    # S3 has separate horizontal blocks for Flower #1 and Flower #2, both headed Sample.
    block = ("Sort", "Group", "Organ", "Unit", "Splitsample", "Sample")
    offsets = [i for i in range(len(s3[3])) if s3[3][i:i + len(block)] == block]
    require(len(offsets) == 1, "Missing or ambiguous split-sample block")
    start = offsets[0]
    h3 = s3[3][start:]
    rows3 = [row[start:] for row in s3[4:] if row[start + 1] == "Flower#2" and row[start + 4]]
    counts = unique_samples(rows3, h3.index("Sample"))
    rows5 = [row for row in s5[4:] if row[1] in ("a", "b")]
    calls = unique_samples(rows5, 2)

    sites = [value for value in s5[3][3:] if value is not None]
    variants = {r[0]: r[5:7] for r in s2[5:] if r[1] == "Flower#2"}
    require(s2[4][5:7] == ("Ref", "Alt") and len(variants) == len(set(sites)) == len(sites) == 37,
            "Candidate inventory differs")
    require(set(variants) == set(sites), "Unmatched candidate key")
    require(all(ref != alt for ref, alt in variants.values()), "Indistinguishable candidate states")
    require(s6[5][:4] == ("Pair", "Organ", "a_SubsampleID", "b_SubsampleID"),
            "Unexpected S6 Section A")
    pairs = s6[6:26]
    names6 = [n for row in pairs for n in row[2:4]]
    require(len(set(names6)) == len(names6) == 40 and set(names6) == set(counts) == set(calls),
            "Split roster differs among tables")
    require(len({row[0] for row in pairs}) == 20, "Duplicate S6 parent pair")

    sign_counts = Counter()
    paired_calls, paired_depths, individual_depths = Counter(), [], []
    flagged_outcomes = Counter()
    largest_flagged_discrepancy = 0.0
    normal_percentages = 0
    positive_percentages = []
    for row in pairs:
        for suffix, sample in zip("ab", row[2:4], strict=True):
            r5, r3 = calls[sample], counts[sample]
            require(r5[1] == suffix and int(r5[0].removeprefix("Pair")) == int(row[0].removeprefix("Pair")),
                    "S5/S6 pairing or orientation differs")
            require(r3[4] == r5[0] and r3[2] == row[1], "S3/S6 pairing or organ differs")
        for site in sites:
            call_pair, depths, flagged = [], [], []
            ref, alt = variants[site]
            for suffix, sample in zip("ab", row[2:4], strict=True):
                r3, r5 = counts[sample], calls[sample]
                ref_reads, alt_reads = r3[h3.index(site + "_Ref")], r3[h3.index(site + "_Alt")]
                require(all(type(v) is int and v >= 0 for v in (ref_reads, alt_reads)), "Invalid read count")
                depth = ref_reads + alt_reads
                require(depth > 0, "Missing coverage in this roster")
                call = r5[s5[3].index(site)]
                require(r3[h3.index(site)] == call and call in (ref, alt), "Inconsistent categorical call")
                vaf = row[s6[5].index(f"{suffix}_{site}%")]
                annotated = isinstance(vaf, str)
                if annotated:
                    require(suffix == "b" and re.fullmatch(r"[0-9]+(?:\.[0-9]+)?#", vaf),
                            "Unexpected textual percentage")
                    vaf = float(vaf[:-1])
                require(isinstance(vaf, (float, int)) and 0 <= vaf <= 100, "Invalid S6 percentage")
                difference = abs(vaf - 100 * alt_reads / depth)
                if annotated:
                    # Marked values are printed as text at reduced precision.
                    largest_flagged_discrepancy = max(largest_flagged_discrepancy, difference)
                    flagged.append(suffix)
                else:
                    require(difference < 1e-10, "Unmarked S6 percentage differs from S3 read counts")
                    normal_percentages += 1
                sign_counts[(call == alt, alt_reads > 0, vaf > 0)] += 1
                if alt_reads:
                    positive_percentages.append(100 * alt_reads / depth)
                call_pair.append(call == alt)
                depths.append(depth)
            pair = tuple(call_pair)
            paired_calls[pair] += 1
            if flagged:
                flagged_outcomes[pair] += len(flagged)
            if pair == (False, False):
                paired_depths.append(sum(depths))
                individual_depths.extend(depths)

    require(set(sign_counts) == {(True, True, True), (False, False, False)},
            "Tables disagree on the support of a nonzero call")
    depth_hist = dict(sorted(Counter(paired_depths).items()))
    return {
        "frame": {"candidate_sites": len(sites), "split_pairs": len(pairs), "subsamples": len(names6)},
        "categorical_comparisons": {
            "both_reference": paired_calls[False, False], "a_only_positive": paired_calls[True, False],
            "b_only_positive": paired_calls[False, True], "both_positive": paired_calls[True, True],
        },
        "subsample_site_agreement": {
            "s3_and_s5_reference_zero_alternate_reads_zero_s6_vaf": sign_counts[False, False, False],
            "s3_and_s5_alternate_nonzero_alternate_reads_nonzero_s6_vaf": sign_counts[True, True, True],
            "min_and_max_positive_read_fraction_in_percent": [round(min(positive_percentages), 6),
                                                             round(max(positive_percentages), 6)],
        },
        "quantitative_consistency": {
            "numeric_percentages_agree_with_s3_to_1e_minus_10_percentage_points": normal_percentages,
            "marked_b_percentages": sum(flagged_outcomes.values()),
            "marked_in_a_only_positive": flagged_outcomes[True, False],
            "marked_in_both_positive": flagged_outcomes[True, True],
            "largest_marked_difference_percentage_points": round(largest_flagged_discrepancy, 6),
        },
        "double_reference": {
            "cells": len(paired_depths), "alternate_reads": 0, "ref_plus_alt_reads": sum(paired_depths),
            "pair_depth": range_summary(paired_depths), "individual_depth": range_summary(individual_depths),
            "pairs_by_combined_depth": depth_hist,
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in SOURCES:
        parser.add_argument(name.lower(), type=Path)
    args = parser.parse_args()
    tables, provenance = read_tables([getattr(args, name.lower()) for name in SOURCES])
    print(json.dumps({"study": "https://doi.org/10.1371/journal.pgen.1011829",
                      "sources": provenance, **analyze(tables)}, indent=2))
