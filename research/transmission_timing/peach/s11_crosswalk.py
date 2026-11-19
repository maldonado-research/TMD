"""Read Ji S11 native workbook XML and audit the named peach memberships."""
import argparse
import csv
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import re
from xml.etree import ElementTree as ET
from zipfile import ZipFile

SHEET = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
SHA = "51caef01a89815100928b4f6fbd7c6b41753d99e0192b4c609cbeee61ac4ed30"
SITES = {"M101": "Pp04:21561355", "M103": "Pp05:11214460"}
COLUMNS = {"M101": ("E","F","G","H"), "M103": ("I","J","K","L"),
           "M120": ("M","N","O","P")}


def read_xlsx(path):
    assert sha256(path.read_bytes()).hexdigest() == SHA
    with ZipFile(path) as source:
        sheets = [n for n in source.namelist() if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", n)]
        assert sheets == ["xl/worksheets/sheet1.xml"]
        shared = ["".join(si.itertext()) for si in ET.fromstring(source.read("xl/sharedStrings.xml")).findall("x:si", SHEET)]
        xml = ET.fromstring(source.read(sheets[0]))
        assert xml.find("x:dimension", SHEET).get("ref") == "A1:P37"
    rows = {}
    for row in xml.findall(".//x:row", SHEET):
        values = {}
        for cell in row.findall("x:c", SHEET):
            value = cell.find("x:v", SHEET)
            if value is not None:
                values[cell.get("r").rstrip("0123456789")] = shared[int(value.text)] if cell.get("t") == "s" else value.text
        rows[int(row.get("r"))] = values
    assert rows[3] == {"E":"#M101","I":"#M103","M":"#M120"}
    assert all(tuple(rows[4][key] for key in cols)==("REF","ALT","VAF(%)","CALL") for cols in COLUMNS.values())
    samples = {}
    for i in range(5,38):
        row = rows[i]
        assert row["B"] == ("First True Leaf" if i < 12 else "Branch Leaf")
        sample = row["D"]
        assert sample not in samples
        vals = {}
        for marker,(r,a,v,c) in COLUMNS.items():
            ref,alt = int(row[r]),int(row[a])
            assert abs(100*alt/(ref+alt)-float(row[v])) < 1e-9
            call = row.get(c)
            assert (call in {"HOM","HET","Absent"}) if i<12 else call is None
            vals[marker] = {"ref":ref,"alt":alt,"depth":ref+alt,"call":call}
        samples[sample]=(row["B"],vals)
    return samples


def tsv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def grouped(rows):
    groups = {}
    for listed in (False,True):
        chosen = [r for r in rows if r["listed"] == listed]
        if not chosen:
            continue
        groups["listed" if listed else "unlisted"] = {
            "n":len(chosen),
            "alt_read_histogram":dict(sorted(Counter(r["alt"] for r in chosen).items())),
            "positive_alt_reads":sum(r["alt"]>0 for r in chosen),
            "min_alt_count":min(r["alt"] for r in chosen),
            "max_alt_count":max(r["alt"] for r in chosen),
            "min_vaf":str(min(Fraction(r["alt"],r["depth"]) for r in chosen)),
            "max_vaf":str(max(Fraction(r["alt"],r["depth"]) for r in chosen)),
        }
    return groups


def analyze(samples, historical):
    records = tsv(historical / "carrier/carriers.tsv")
    sites = {f'{r["chromosome"]}:{r["position"]}':set(r["listed_leaves"].split(";")) for r in records}
    roster = {r["sample_id"] for r in tsv(historical / "carrier/sample_roster.tsv")}
    b1 = {s for s in roster if s.startswith("DHQ1_B1-")}
    parents = {s:values for s,(kind,values) in samples.items() if kind=="Branch Leaf"}
    children = {s:values for s,(kind,values) in samples.items() if kind=="First True Leaf"}
    assert len(parents)==26 and len(children)==7 and set(parents)<=b1 and len(b1)==29
    assert not (set(children) & roster)
    detail = {marker:[{"leaf":sample,"listed":sample in sites[key],**values[marker]}
                      for sample,values in sorted(parents.items())]
              for marker,key in SITES.items()}
    common = json.loads((historical / "completion/orientation_result.json").read_bytes())["unrestricted"]["additions_common_to_all_optima"]
    lookup = {key:marker for marker,key in SITES.items()}
    overlapping = []
    for site,leaves in common.items():
        for leaf in leaves:
            if site in lookup and leaf in parents:
                marker=lookup[site]
                overlapping.append({"marker":marker,"leaf":leaf,**parents[leaf][marker]})
    thresholds = []
    for k in range(1, max(r["alt"] for r in detail["M101"])+2):
        pred = {r["leaf"] for r in detail["M101"] if r["alt"]>=k}
        listed = sites[SITES["M101"]] & parents.keys()
        thresholds.append({"minimum_alt_reads":k,"identified":len(pred),
                           "additional_to_2019_list":len(pred-listed),"missed_2019_listings":len(listed-pred)})
    assert [r['minimum_alt_reads'] for r in thresholds if r['additional_to_2019_list']==r['missed_2019_listings']==0] == [3]
    hypothesized = {r["leaf"] for r in overlapping if r["marker"] == "M101"}
    target_comparison = {}
    for cutoff in (1,2,3):
        out = {}
        for group, members in (("shared_additions",hypothesized),
                               ("other_unlisted",parents.keys()-sites[SITES["M101"]]-hypothesized)):
            out[group] = {"meeting_count":sum(parents[leaf]["M101"]["alt"] >= cutoff for leaf in members),
                          "number_measured":len(members)}
        target_comparison[str(cutoff)] = out
    calls = {m:dict(sorted(Counter(child[m]["call"] for child in children.values()).items())) for m in COLUMNS}
    joint = Counter(tuple(child[m]["call"]!="Absent" for m in COLUMNS) for child in children.values())
    return {"native_sheet_range":"A1:P37","parent_leaves":len(parents),"progeny":len(children),
            "unrepresented_original_B1_samples":sorted(b1-parents.keys()),
            "original_catalogue_stratified_read_counts":{m:grouped(rows) for m,rows in detail.items()},
            "M101_count_cutoffs_on_26_named_parental_leaves":thresholds,
            "overlap_with_ten_minimum_completion_additions":overlapping,
            "M101_support_in_named_additions_vs_other_unlisted":target_comparison,
            "parent_crosswalk":detail,"source_calls_in_progeny":calls,
            "joint_positive_progeny_M101_M103_M120":{"".join("1" if v else "0" for v in pattern):n for pattern,n in sorted(joint.items())}}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("workbook",type=Path)
    p.add_argument("historical",type=Path,help="Path to previously published research/leaf_lineages")
    args=p.parse_args()
    print(json.dumps(analyze(read_xlsx(args.workbook),args.historical),indent=2))
