"""Cross-match the DHQ1 branch catalogue from Wang 2019 with Ji 2025 Table S2."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

from openpyxl import load_workbook

HERE = Path(__file__).resolve().parent
JI_S2 = "b101c5288f34ca8853d2dd8592b1fd80e1ea4347a96dc049913693ca79302fa4"


def source_summary(path):
    with path.open() as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    keyed = {(r["chromosome"], int(r["position"])): (r["change"], int(r["listed_samples"]))
             for r in rows}
    assert len(rows) == len(keyed) == 48
    return keyed


def verify(ji, wang_summary):
    if hashlib.sha256(ji.read_bytes()).hexdigest() != JI_S2:
        raise ValueError("Unexpected 2025 Wang-attribution table digest")
    known = source_summary(wang_summary)
    book = load_workbook(ji, read_only=True, data_only=True)
    try:
        rows = list(book["S2_Table"].values)
    finally:
        book.close()
    header = rows[4]
    entries = [dict(zip(header, r)) for r in rows[5:]]
    earlier = [r for r in entries if r["Citation"] == "Wang et al. 2019"]
    assert len(earlier) == len(known)
    assert {(r["Chr"],r["Base"]) for r in earlier} == set(known)
    snvs = 0
    for row in earlier:
        change, _ = known[row["Chr"],row["Base"]]
        if change.startswith("SNV:"):
            assert change == f'SNV:{row["Ref"]}>{row["Alt"]}'
            snvs += 1
    assert snvs == 46
    featured = {r["ID"]: known[r["Chr"],r["Base"]][1] for r in earlier
                if r["Present in Flower#2"] == "Yes"}
    absent = [r["ID"] for r in entries if r["ID"] in ("M119", "M120")
              and (r["Chr"],r["Base"]) not in known and r["Citation"] == "This paper"]
    assert set(absent) == {"M119","M120"}
    assert featured == {"M71": 2, "M101": 14}
    return dict(matched_coordinate_pairs=len(known), exact_SNV_allele_matches=snvs,
                indel_coordinate_matches=2, historical_leaf_sample_counts_for_flower_markers=featured,
                current_paper_deep_markers_absent_from_2019_catalogue=sorted(absent))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ji_table_s2", type=Path)
    parser.add_argument("--wang-summary", type=Path, default=HERE/"wang_dhq1_site_summary.tsv")
    args = parser.parse_args()
    print(json.dumps(verify(args.ji_table_s2, args.wang_summary),indent=2))
