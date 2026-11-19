"""Check nested-marker signals and library coverage in Ji et al.'s split lysates."""
import argparse
import csv
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
DIGESTS = {
    "S1": "ae7b0fabfb402c26518c49fef0a5e7a47ac0d2383a6168085fbee27e4d201227",
    "S3": "80774928a21b4aaa717e5c87afdb3d01aae9d8392b1cbfc23e542358ff292d6f",
    "S5": "a37bcda6a357e779840974bd8cf51bb526db863bb689013eac02f28c076e4394",
}
MARKERS = {"M101": ("G","A"), "M119": ("C","T"), "M21": ("T","C"),
           "M71": ("A","C"), "M42": ("G","A")}
RELATIONS = [("M101", "M119"), ("M101", "M21"), ("M119", "M21"), ("M71", "M42")]
COLUMNS = ["pair", "side", "sample", "organ", "organ_unit", "mapped_depth", "coverage_5x_pct"]
COLUMNS += [f"{m}_{state}" for m in MARKERS for state in ("ref","alt")]


def table(path, name):
    if name in DIGESTS and sha256(path.read_bytes()).hexdigest() != DIGESTS[name]:
        raise ValueError(f"{name} source digest differs")
    if path.suffix.lower() == ".xlsx":
        from openpyxl import load_workbook
        book = load_workbook(path, read_only=True, data_only=True)
        try:
            return list(book.active.values)
        finally:
            book.close()
    if name in DIGESTS:
        raise ValueError(f"{name} must be the pinned workbook")
    return [[cell.strip() for cell in row.strip().strip("|").split("|")]
            for row in path.read_text().splitlines() if row.lstrip().startswith("|")]


def keyed(rows, pos):
    result = {r[pos]:r for r in rows}
    if len(result) != len(rows):
        raise ValueError("Duplicate source sample")
    return result


def numeric_rows(rows):
    return [r for r in rows if r and str(r[0]).isdigit()]


def normalized(text):
    return " ".join(str(text).split())


def extract(s1, s3, s5, s7, s8):
    qc, flower, roster, vaf, cvf = [table(p,n) for p,n in
                                     zip((s1,s3,s5,s7,s8),("S1","S3","S5","S7","S8"),strict=True)]
    h1 = list(qc[2])
    split = flower[3].index("Splitsample")
    h7 = next(r for r in vaf if r[:4] and list(r[:4])==["#", "Year","Group","Sample ID"])
    h8 = next([normalized(x) for x in r] for r in cvf if len(r)>4 and r[4]=="Sample")
    qc_rows = keyed(numeric_rows(qc),h1.index("Sample_ID"))
    flower_rows = keyed([r for r in flower[4:] if r[split-3]=="Flower#2"],split+1)
    vaf_rows = keyed(numeric_rows(vaf),h7.index("Sample ID"))
    cvf_rows = keyed([r for r in numeric_rows(cvf) if r[h8.index("Location")]=="Flower#2"],h8.index("Sample"))
    result = []
    for pair, side, sample, *_ in roster[4:]:
        if side not in ("a","b"):
            continue
        a,b,c,d = (group[sample] for group in (qc_rows, flower_rows, vaf_rows, cvf_rows))
        organ = a[h1.index("Group")].removeprefix("Flower#2_")
        unit = a[h1.index("Unit")]
        if (not a[h1.index("Group")].startswith("Flower#2_") or a[h1.index("SplitSample")] != pair
                or b[split]!=pair or b[split-2]!=organ or str(b[split-1])!=str(unit)
                or c[h7.index("Group")]!="Branch1-1_Flower#2_"+organ or d[h8.index("Organ")]!=organ):
            raise ValueError(f"Inconsistent sample identity or organ at {sample}")
        row = dict(pair=pair,side=side,sample=sample, organ=organ, organ_unit=unit,
                   mapped_depth=a[h1.index("Mapped Depth (Mapping Quality ≥ 20)")],
                   coverage_5x_pct=a[h1.index("Genome (%) covered by reads ≥ 5")])
        for marker, bases in MARKERS.items():
            for label,base in zip(("ref","alt"), bases, strict=True):
                n = int(c[h7.index(marker+"_"+base)])
                expected = int(d[h8.index("#"+label.capitalize()+"_reads #"+marker)])
                if n!=expected or n<0:
                    raise ValueError(f"S7/S8 source counts differ for {sample} at {marker}")
                if marker in ("M21","M42") and b[flower[3].index(marker+"_"+label.capitalize())]!=n:
                    raise ValueError(f"S3/S7 source counts differ for {sample} at {marker}")
                row[marker+"_"+label] = n
        result.append(row)
    return result


def states(rows):
    summary = {}
    for parent, child in RELATIONS:
        strata = Counter((r[parent+"_alt"]>0,r[child+"_alt"]>0) for r in rows)
        summary[parent+"_and_"+child] = {
            "parent_and_child_positive":strata[True, True],
            "only_child_positive":strata[False, True],
            "only_parent_positive":strata[True, False],
            "neither_positive":strata[False, False],
        }
    return summary


def nesting(rows):
    """Count observations and find separately attainable minimal edits to the nested chain."""
    nested = ("000", "100", "110", "111")
    patterns = Counter("".join("1" if r[m+"_alt"] > 0 else "0" for m in ("M101","M119","M21"))
                       for r in rows)
    costs = Counter()
    for pattern, number in patterns.items():
        options = [(sum(x=="0" and y=="1" for x,y in zip(pattern, valid)),
                    sum(x=="1" and y=="0" for x,y in zip(pattern, valid)))
                   for valid in nested]
        costs["unrestricted"] += number * min(a+d for a,d in options)
        costs["additions_only"] += number * min(a for a,d in options if d==0)
        costs["deletions_only"] += number * min(d for a,d in options if a==0)
    return {"order":["M101","M119","M21"], "observed_bits":dict(sorted(patterns.items())),
            "minimum_cell_edits":dict(costs)}


def summarize(rows):
    if {r["pair"] for r in rows} != {f"Pair{i}" for i in range(1,21)} or len(rows)!=40:
        raise ValueError("Expected 20 split pairs of aliquots")
    if len({r["sample"] for r in rows})!=40:
        raise ValueError("Duplicate input aliquot")
    for row in rows:
        for m in MARKERS:
            for state in ("ref","alt"):
                key=m+"_"+state
                row[key]=int(row[key])
                if row[key]<0: raise ValueError("Negative read count")
    pairs = []
    for p in range(1,21):
        group=[r for r in rows if r["pair"]==f"Pair{p}"]
        if sorted(r["side"] for r in group)!=["a","b"]:
            raise ValueError("Aliquot pairing differs from source")
        pairs.append({m+"_alt":sum(r[m+"_alt"] for r in group) for m in MARKERS})
    target = [{**{k:r[k] for k in ("side","sample","organ")},"organ_unit":int(r["organ_unit"]),
               "mapped_depth":float(r["mapped_depth"]), "genome_coverage_ge_5x_pct":float(r["coverage_5x_pct"]),
               "alternate_and_depth": {m:[r[m+"_alt"],r[m+"_alt"]+r[m+"_ref"]] for m in MARKERS}}
              for r in rows if r["pair"]=="Pair19"]
    return {"unit":"20 paired lysates in peach Flower #2, each sequenced in two aliquots",
            "positive_marker_rule":"At least one reported alternate read",
            "pair19":target, "aliquot_cross_counts":states(rows),"pooled_lysate_cross_counts":states(pairs),
            "aliquot_nesting":nesting(rows), "pooled_lysate_nesting":nesting(pairs)}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--extract",nargs=5,type=Path,metavar=("S1","S3","S5","S7","S8"))
    p.add_argument("--input",type=Path,default=HERE/"aliquot_profiles.csv")
    args=p.parse_args()
    if args.extract:
        rows=extract(*args.extract)
        if len(rows)!=40:raise ValueError("Expected 40 samples")
        out=csv.DictWriter(sys.stdout,fieldnames=COLUMNS,lineterminator="\n")
        out.writeheader();out.writerows(rows)
    else:
        with args.input.open(newline="") as f:
            print(json.dumps(summarize(list(csv.DictReader(f))),indent=2))
