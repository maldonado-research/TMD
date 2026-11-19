"""Verify the native Ji S7 leaf counts using workbook XML and earlier published inputs."""
import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from s11_crosswalk import SHEET, read_xlsx, tsv
from hashlib import sha256

DIGEST = "9a8ffb1020eeeddf9e2c129b91b0f710a41a4ad68b59f9444fabd2b88ce8f5c3"
MARKERS = {
    "M120": ("E","F","G"), "M71": ("H","I","J"), "M42": ("K","L","M"), "M10": ("N","O","P"),
    "M101": ("Q","R","S"), "M119": ("T","U","V"), "M21": ("W","X","Y"), "M11": ("Z","AA","AB"),
}
KEYS = {"M101":"Pp04:21561355", "M71":"Pp01:2130859"}


def load_s7(path):
    assert sha256(path.read_bytes()).hexdigest() == DIGEST
    with ZipFile(path) as source:
        ss = ET.fromstring(source.read("xl/sharedStrings.xml"))
        strings = ["".join(s.itertext()) for s in ss.findall("x:si", SHEET)]
        sheet = ET.fromstring(source.read("xl/worksheets/sheet1.xml"))
        assert sheet.find("x:dimension", SHEET).get("ref") == "A1:AB194"
    parsed,header = {},{}
    for row in sheet.findall(".//x:row", SHEET):
        n = int(row.get("r"))
        values = {}
        for c in row.findall("x:c", SHEET):
            v = c.find("x:v", SHEET)
            if v is not None:
                letters = c.get("r").rstrip("0123456789")
                values[letters] = strings[int(v.text)] if c.get("t") == "s" else v.text
        if n == 7:
            header = values
            assert [values[c] for c in ("D","Q","R","H","I")] == ["Sample ID","M101_G","M101_A","M71_A","M71_C"]
        if n < 8: continue
        sample = values["D"]
        assert int(values["A"]) == n-7 and sample not in parsed
        counts = {}
        for marker,(r,a,v) in MARKERS.items():
            assert all(header[k].split("_")[0]==marker for k in (r,a,v))
            ref,alt = int(values[r]),int(values[a])
            # Samples with no covering reads are possible outside the leaf roster.
            if ref+alt:
                assert abs(100*alt/(ref+alt)-float(values[v])) < 1e-8
            counts[marker] = (ref,alt)
        parsed[sample] = (int(values["B"]),n,counts)
    assert len(parsed) == 187
    return parsed


def report(s7,s11,historical):
    all_samples=load_s7(s7)
    counts={k:p for k,(year,n,p) in all_samples.items() if year==2016}
    roster = {d["sample_id"] for d in tsv(historical/"carrier/sample_roster.tsv")}
    assert counts.keys()==roster and len(roster)==75
    sites = {f'{r["chromosome"]}:{r["position"]}':set(r["listed_leaves"].split(";"))
             for r in tsv(historical/"carrier/carriers.tsv")}
    membership,comparison={},{}
    for marker,site in KEYS.items():
        membership[marker] = sites[site]
        states = {}
        for group,leaves in [("listed",sites[site]),("unlisted",roster-sites[site])]:
            records=[(*counts[leaf][marker],leaf) for leaf in leaves]
            assert all(r+a>0 for r,a,k in records)
            states[group]={"n":len(leaves),"alt_histogram":dict(sorted(Counter(a for r,a,k in records).items())),
                           "depth_range":[min(r+a for r,a,k in records),max(r+a for r,a,k in records)],
                           "vaf_range":[str(fn(Fraction(a,r+a) for r,a,k in records)) for fn in (min,max)]}
        comparison[marker]=states

    required=json.loads((historical/"completion/orientation_result.json").read_bytes())["unrestricted"]["additions_common_to_all_optima"]
    predicted=set(required[KEYS["M101"]])
    remaining={l for l in roster if l.startswith("DHQ1_B1-") and l not in membership["M101"] and l not in predicted}
    matched=[]
    for sample,(_,per_marker) in read_xlsx(s11).items():
        if sample not in counts: continue
        for m in ("M101","M120"):
            assert counts[sample][m] == (per_marker[m]["ref"],per_marker[m]["alt"])
            matched.append((sample,m))
    assert len(matched)==52

    def frequencies(leaves,marker):
        data=[counts[l][marker] for l in leaves]
        return {"number":len(data), "ref_read_sum":sum(r for r,a in data),"alt_read_sum":sum(a for r,a in data),
                "min_total":min(r+a for r,a in data),"max_total":max(r+a for r,a in data),
                "at_least_k_alt":{k:sum(a>=k for r,a in data) for k in (1,2,3)}}
    cohorts={"four_minimum_additions":predicted,"other_B1_unlisted":remaining,
             "B1_listed":membership["M101"],"other_branches":{l for l in roster if not l.startswith("DHQ1_B1-")}}
    cutoffs=[]
    for k in (1,2,3,4):
        a={l for l in counts if counts[l]["M71"][1]>=k}
        b={l for l in counts if counts[l]["M101"][1]>=k}
        cutoffs.append({"minimum_alt":k,"shared":len(a&b),"M71_only":len(a-b),"M101_only":len(b-a),
                        "neither":len(roster-a-b)})
    return {"source_sha256":DIGEST, "source_rows_by_year":dict(sorted(Counter(y for y,n,p in all_samples.values()).items())),
            "marker_panels":list(MARKERS),"matched_2016_leaves":len(roster),"source_id_sets_match":True,
            "shared_S11_parent_sample_marker_read_pairs_verified":len(matched),
            "catalogue_comparison_2016":comparison,"M101_branch_and_prediction_summary":{k:frequencies(v,"M101") for k,v in cohorts.items()},
            "four_M101_minimum_addition_rows":{l:{"worksheet_row":all_samples[l][1],"ref":counts[l]["M101"][0],"alt":counts[l]["M101"][1]} for l in sorted(predicted)},
            "two_focal_leaves":{l:{"worksheet_row":all_samples[l][1], **{m:{"ref":counts[l][m][0],"alt":counts[l][m][1]} for m in KEYS}} for l in ["DHQ1_B1-1-L1","DHQ1_B1-1-L2"]},
            "M71_M101_read_thresholds_across_75_leaves":cutoffs}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("s7_xlsx",type=Path)
    p.add_argument("s11_xlsx",type=Path)
    p.add_argument("historical",type=Path)
    args=p.parse_args()
    print(json.dumps(report(args.s7_xlsx,args.s11_xlsx,args.historical),indent=2))
