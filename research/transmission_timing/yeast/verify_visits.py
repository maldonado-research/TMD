"""Audit sample-time threshold crossings in the 18 focal haploid YPD wells of Johnson et al."""
import argparse
import csv
from collections import Counter, defaultdict
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

TIMES = (70, 1410, 2640, 5150, 7530, 10150)
CHROMS = {"chr" + s for s in "I II III IV V VI VII VIII IX X XI XII XIII XIV XV XVI".split()}
CLASSES = {"missense", "nonsense", "indel", "synonymous", "noncoding"}
HASHES = ["df824c56c70e4c7b6f4cc0fdf908fa0d99c5d40628381fd10c5c5df1640b2b98",
          "b6713bb965bde6064142d3261a51b31b775643b8b4fba86b236b8c8cd45b7e72"]


def haploid_ypd(roster):
    """Read supplement 1 at source, independently of any allele-table class labels."""
    with ZipFile(roster) as z:
        ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        book = ET.fromstring(z.read("xl/workbook.xml"))
        sheets = book.findall(".//m:sheet", ns)
        ix = next(i for i, sh in enumerate(sheets, 1) if sh.get("name") == "Well_Info")
        strings = ["".join(t.text or "" for t in item.findall(".//m:t", ns))
                   for item in ET.fromstring(z.read("xl/sharedStrings.xml"))]
        text = ET.fromstring(z.read(f"xl/worksheets/sheet{ix}.xml"))
        rows = []
        for r in text.findall(".//m:row", ns):
            vals = {}
            for c in r.findall("m:c", ns):
                v = c.findtext("m:v", namespaces=ns)
                if v is not None:
                    col = "".join(char for char in c.get("r") if char.isalpha())
                    vals[col] = strings[int(v)] if c.get("t") == "s" else v
            rows.append(vals)
        assert [rows[0][x] for x in "BCEF"] == ["platewell", "plate", "contam", "strain"]
        return {r["B"] for r in rows[1:] if r["C"] == "P1" and r["E"] == "No" and r["F"] in ("a","alpha")}


def visits(row, discrepancies):
    outcome = []
    for t in TIMES:
        alt = float(row[f"G{t}_alt_counts"])
        ref = float(row[f"G{t}_ref_counts"])
        assert alt.is_integer() and ref.is_integer()
        total = int(ref + alt)
        # Negative state means insufficient depth, 0 below 10%, 1 from 10 to below 90%, 2 at least 90%.
        state = -1 if total < 5 else int(10 * alt >= total) + int(10 * alt >= 9 * total)
        outcome.append(state)
    start = stable_start(outcome, 2)
    assert [x >= start for x in range(len(TIMES))] == [row[f"fixed_by_{t}"] == "True" for t in TIMES]
    for i, t in enumerate(TIMES):
        # The published parser invokes fixed_by with a different threshold here.
        # It carries forward a previous fixed_by flag, which is the 90% flag in haploids.
        flag = i > start or (outcome[i] >= 1 and 0 not in outcome[i+1:])
        assert (row[f"present_at_{t}"] == "True") == flag, (t,outcome)
        if flag and outcome[i] < 1:
            discrepancies["flagged_but_not_local"] += 1
        if not flag and outcome[i] >= 1:
            discrepancies["local_but_not_flagged"] += 1
        discrepancies["compared"] += 1
    return outcome


def stable_start(states, threshold):
    """First counted visit meeting the threshold after the last adequately measured subthreshold visit."""
    last_low = max((i for i, state in enumerate(states) if 0 <= state < threshold), default=-1)
    return next((i for i, state in enumerate(states) if state >= threshold and i > last_low), len(states))


def first(visits_by_group, keep):
    sizes = (len(keep),) * 4
    by_group = {}
    for group, rows in visits_by_group.items():
        group_start = sizes
        for raw in rows:
            states = [raw[i] for i in keep]
            early = next((j for j,state in enumerate(states) if state >= 1),len(keep))
            high = next((j for j,state in enumerate(states) if state == 2),len(keep))
            stable = stable_start(states, 2)
            flagged = stable_start(states, 1)
            group_start = tuple(min(a,b) for a,b in zip(group_start, (early,flagged,high,stable)))
        by_group[group] = group_start
    result=[]
    for k in range(4):
        tmin=min(t[k] for t in by_group.values())
        if tmin == len(keep):
            result.append((None,set()))
        else:
            result.append((TIMES[keep[tmin]],{group for group,t in by_group.items() if t[k]==tmin}))
    return result


def compute(roster, measurements):
    assert [sha256(p.read_bytes()).hexdigest() for p in (roster,measurements)] == HASHES
    allowed=haploid_ypd(roster)
    data={}
    classes={}
    rows_by_well = Counter()
    discrepancies_by_well = defaultdict(Counter)
    named_example = {}
    with ZipFile(measurements) as archive:
        for path in archive.namelist():
            well=Path(path).name.split("_")[0]
            if well not in allowed or not path.endswith(".tsv"):
                continue
            groups=defaultdict(list)
            types={}
            for r in csv.DictReader(StringIO(archive.read(path).decode()),delimiter="\t"):
                if r["CHROM"] not in CHROMS or r["in_telomere"] != "False" or r["group_mutation_type"] not in CLASSES:
                    continue
                if "True" not in (r["filter_1"],r["filter_2"]) or float(r["well_total_alt_counts"]) < 5:
                    continue
                g=r["mutation_group"]
                assert r["group_mutation_type"] == types.setdefault(g,r["group_mutation_type"])
                groups[g].append(visits(r, discrepancies_by_well[well]))
                rows_by_well[well] += 1
                if well == "P1E11" and g in {"55", "145"}:
                    assert g not in named_example
                    named_example[g] = {
                        "class": types[g],
                        "alternate_and_total_reads": [
                            [int(float(r[f"G{t}_alt_counts"])),
                             int(float(r[f"G{t}_alt_counts"]) + float(r[f"G{t}_ref_counts"]))]
                            for t in TIMES
                        ],
                    }
            data[well]=groups
            classes[well]=types
    assert len(data)==18
    return {"source_sha256": HASHES, "visit_generations": list(TIMES),
            "endpoint_order": ["local_10", "source_present_at", "local_90", "source_fixed_by"],
            "P1E11_group_example": named_example,
            "all_initially_haploid": summarize(data, classes, rows_by_well, discrepancies_by_well),
            "excluding_autodiploidized_P1B03": summarize(
                {well: groups for well, groups in data.items() if well != "P1B03"},
                classes, rows_by_well, discrepancies_by_well, details=False)}


def summarize(data, classes, rows_by_well, discrepancies_by_well, details=True):
    summaries={key:Counter() for key in ("first10","flag10","first90","stable90","group_overlap","class_overlap","thinned")}
    by_visit={key:Counter() for key in ("first10","flag10","first90","stable90")}
    thin_rows=[]
    endpoint_rows=[]
    for well in sorted(data):
        full=first(data[well],range(6))
        entry=[]
        for k, label in enumerate(("first10","flag10","first90","stable90")):
            t,g=full[k]
            c=sorted({classes[well][i] for i in g})
            summaries[label]["multiple_groups"] += len(g)>1
            summaries[label]["multiple_classes"] += len(c)>1
            by_visit[label][t]+=1
            entry.append({"endpoint":label,"visit":t,"groups":len(g),"classes":c})
        endpoint_rows.append({"well":well,"first":entry})
        for a,b in ((0,1),(0,2),(0,3),(1,2),(1,3),(2,3)):
            x,y=full[a][1],full[b][1]
            kind="equal" if x==y else "overlap" if x & y else "disjoint"
            summaries["group_overlap"][f"{a}vs{b}_{kind}"]+=1
            cx={classes[well][i] for i in x}
            cy={classes[well][i] for i in y}
            kind="equal" if cx==cy else "overlap" if cx & cy else "disjoint"
            summaries["class_overlap"][f"{a}vs{b}_{kind}"]+=1
        for skip in range(1,5):
            grid=[i for i in range(6) if i!=skip]
            thinned=first(data[well],grid)
            changes=[]
            for k,(t,g) in enumerate(thinned):
                t0,g0=full[k]
                order="earlier" if t<t0 else "later" if t>t0 else "same"
                rel="equal" if g==g0 else "overlap" if g & g0 else "disjoint"
                summaries["thinned"][f"{k}_{order}"]+=1
                summaries["thinned"][f"{k}_group_{rel}"]+=1
                changes.append([t,order,rel])
            thin_rows.append({"well":well,"omitted_generation":TIMES[skip],"endpoints":changes})
    result = {"local_vs_source_present_cells":sum((discrepancies_by_well[w] for w in data),Counter()),
              "populations":len(data), "eligible_rows":sum(rows_by_well[w] for w in data),
              "eligible_groups":sum(map(len,data.values())), "visit_histograms":by_visit, "summary":summaries}
    if details:
        result["first_visit_by_well"] = endpoint_rows
        result["changed_after_omitting_one_visit"] = [
            row for row in thin_rows if any(x[1] != "same" or x[2] != "equal" for x in row["endpoints"])]
    return result



if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roster",type=Path)
    parser.add_argument("measurements",type=Path)
    a=parser.parse_args()
    print(json.dumps(compute(a.roster,a.measurements),indent=2))
