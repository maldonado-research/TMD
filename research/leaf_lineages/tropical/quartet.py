"""Compare physical and SNV distance sums on the seven branch tips of each tropical tree."""
from collections import Counter
from decimal import Decimal
from hashlib import sha256
from itertools import combinations
import argparse
import io
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
DOI = "https://doi.org/10.7554/eLife.88456"
URL = "https://cdn.elifesciences.org/articles/88456/elife-88456-supp1-v1.xlsx"
SHA = "a5916e95facc077a137ce03627b2a94ef7ecf3cc9a148223587bdb719d2a06af"
TIPS = ("1_1", "1_2", "2_1", "2_2", "3_1", "3_2", "4")
SAMPLES = ("0",) + TIPS
TREES = ("S1", "S2", "F1", "F2")


def extract(path):
    from openpyxl import load_workbook
    data = path.read_bytes()
    if sha256(data).hexdigest() != SHA:
        raise ValueError("Unexpected Supplementary File 1 SHA-256")
    book = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    try:
        sheet = list(book["b"].values)
    finally:
        book.close()
    header = [str(x) for x in sheet[0]]
    first = header.index("0")
    assert header[first + 1:first + 7] == list(TIPS[:-1])
    recorded = {tree: [] for tree in TREES}
    for row in sheet[1:]:
        if not any(v is not None for v in row):
            continue
        tree, tip = row[1], str(row[2])
        for index, prior in enumerate(SAMPLES[:SAMPLES.index(tip)]):
            value = row[first + index]
            distance, count = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)\s*\((\d+)\)", value).groups()
            scaled = Decimal(distance) * 100
            assert scaled == int(scaled)
            recorded[tree].append([prior, tip, int(scaled), int(count)])
    all_pairs = set(combinations(SAMPLES, 2))
    assert all({(a,b) for a,b,_,_ in rows} == all_pairs and len(rows) == 28 for rows in recorded.values())
    return {"article": DOI, "source_workbook": URL, "sha256": SHA, "sheet": "b",
            "columns": ["sample_a","sample_b","physical_distance_centimetres","SNV_distance"],
            "trees": recorded}


def classify(sums):
    order = sorted(range(3), key=sums.__getitem__)
    low, mid, high = (sums[i] for i in order)
    minimum = order[0] if low < mid else None
    return minimum, high-mid, mid-low


def audit(rows, with_cambium):
    matrix = {(a,b): (d,n) for a,b,d,n in rows}
    counts = Counter()
    unique_conflict = []
    examples = []
    all_tied = 0
    for a,b,c,d in combinations(SAMPLES,4):
        if (a == "0") != with_cambium:
            continue
        pairings = (((a,b),(c,d)), ((a,c),(b,d)), ((a,d),(b,c)))
        distance_sums = [[matrix[p][i]+matrix[q][i] for p,q in pairings] for i in (0,1)]
        physical, error, physical_margin = classify(distance_sums[0])
        snv, snv_error, snv_margin = classify(distance_sums[1])
        all_tied += len(set(distance_sums[1])) == 1
        counts["quartets"] += 1
        counts["physical_exact_four_point"] += error == 0
        counts["physical_unique_smallest"] += physical is not None
        counts["snv_exact_four_point"] += snv_error == 0
        counts["snv_unique_smallest"] += snv is not None
        if physical is None:
            counts["physical_unresolved"] += 1
        elif snv is None:
            counts["snv_tied_minimum"] += 1
        elif physical == snv:
            counts["unique_agreement"] += 1
        else:
            counts["unique_disagreement"] += 1
            unique_conflict.append({"samples":[a,b,c,d],"physical_sums_cm":distance_sums[0],"snv_sums":distance_sums[1]})
        if snv_error:
            examples.append({"samples":[a,b,c,d],"sums":distance_sums[1],"largest_minus_middle":snv_error})
    return {"quartets": counts["quartets"], "snv_all_three_sums_equal": all_tied,"physical_exact_four_point": counts["physical_exact_four_point"],
            "physical_unique_smallest": counts["physical_unique_smallest"], "snv_exact_four_point": counts["snv_exact_four_point"],
            "snv_unique_smallest":counts["snv_unique_smallest"],
            "comparison": {key: counts[key] for key in ("unique_agreement","unique_disagreement","snv_tied_minimum","physical_unresolved")},
            "disagreements":unique_conflict, "nonadditivity_maximum_example":max(examples,key=lambda e:e["largest_minus_middle"],default=None)}


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extract",type=Path,help="original Satake et al. XLSX supplement")
    parser.add_argument("--input",type=Path,default=HERE/"tip_distances.json")
    options=parser.parse_args()
    out=extract(options.extract) if options.extract else {tree: {"four_tips": audit(rows, False), "basal_cambium_and_three_tips": audit(rows, True)}
             for tree,rows in json.loads(options.input.read_text())["trees"].items()}
    print(json.dumps(out,indent=2))
