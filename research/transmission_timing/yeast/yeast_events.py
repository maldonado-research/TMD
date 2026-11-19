"""Reconstruct sampled mutation-group endpoints for a published baker's yeast time series."""
import argparse
from collections import Counter, defaultdict
import csv
from hashlib import sha256
import io
import json
from pathlib import Path
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
TIMES = (70, 1410, 2640, 5150, 7530, 10150)
KINDS = {"missense", "nonsense", "indel", "synonymous", "noncoding"}
CHROMS = {"chr" + x for x in "I II III IV V VI VII VIII IX X XI XII XIII XIV XV XVI".split()}
ENDPOINTS = ("local10", "deposited_present", "local90", "deposited_fixed")
HASHES = ("df824c56c70e4c7b6f4cc0fdf908fa0d99c5d40628381fd10c5c5df1640b2b98",
          "b6713bb965bde6064142d3261a51b31b775643b8b4fba86b236b8c8cd45b7e72")


def extract(info_path, zip_path):
    from openpyxl import load_workbook
    for path, expected in zip((info_path,zip_path),HASHES):
        assert sha256(path.read_bytes()).hexdigest() == expected
    book = load_workbook(info_path, data_only=True, read_only=True)
    try:
        table = list(book["Well_Info"].values)
    finally:
        book.close()
    info = {r[1]:dict(zip(table[0],r)) for r in table[1:]}
    out = []
    with ZipFile(zip_path) as arc:
        for member in sorted(arc.namelist()):
            if not member.startswith("processed_well_output/P1") or not member.endswith("_processed.tsv"):
                continue
            well = Path(member).name.removesuffix("_processed.tsv")
            if info[well]["strain"] not in ("a","alpha"):
                continue
            with arc.open(member) as raw, io.TextIOWrapper(raw,encoding="utf-8") as stream:
                for row in csv.DictReader(stream, delimiter="\t"):
                    kind=row["group_mutation_type"]
                    if row["CHROM"] not in CHROMS or row["in_telomere"] != "False" or kind not in KINDS:
                        continue
                    if row["filter_1"] != "True" and row["filter_2"] != "True":
                        continue
                    if int(float(row["well_total_alt_counts"])) < 5:
                        continue
                    # ? = inadequate depth, 0 = below 10%, 1 = 10% to below 90%, 2 = at least 90%.
                    calls = []
                    archived_low = []
                    archived_high = []
                    for t in TIMES:
                        ref,alt=[int(float(row[f"G{t}_{allele}_counts"])) for allele in ("ref","alt")]
                        depth=ref+alt
                        if depth < 5:
                            call = "?"
                        elif 10 * alt >= 9 * depth:
                            call = "2"
                        elif 10 * alt >= depth:
                            call = "1"
                        else:
                            call = "0"
                        archived_low.append(row[f"present_at_{t}"] == "True")
                        archived_high.append(row[f"fixed_by_{t}"] == "True")
                        calls.append(call)
                    first_stable = next((i for i,c in enumerate(calls)
                                         if c=="2" and all(x in "2?" for x in calls[i+1:])),len(TIMES))
                    assert [row[f"fixed_by_{t}"]=="True" for t in TIMES] == [j>=first_stable for j in range(len(TIMES))]
                    for i,t in enumerate(TIMES):
                        expected = (i>0 and archived_high[i-1]) or (calls[i] in "12" and all(c in "12?" for c in calls[i+1:]))
                        assert expected == archived_low[i], (well,i, calls, archived_low)
                    out.append([well,info[well]["strain"],row["mutation_group"],kind,"".join(calls),
                                "".join("1" if flag else "0" for flag in archived_low),
                                "".join("1" if flag else "0" for flag in archived_high)])
    return out


def read_groups(rows):
    populations=defaultdict(dict)
    for well,strain,identifier,kind,mask,dep_low,dep_high in rows:
        assert kind in KINDS and len(mask)==len(TIMES) and set(mask)<=set("?012")
        g=populations[well].setdefault(identifier,{"class":kind,"masks":[]})
        assert g["class"]==kind
        g["masks"].append((mask,dep_low,dep_high))
    return populations


def group_times(group):
    passed=defaultdict(list)
    for calls,dep_low,dep_high in group["masks"]:
        for i,call in enumerate(calls):
            if call in "12":
                passed["local10"].append(TIMES[i])
            if call == "2":
                passed["local90"].append(TIMES[i])
            if dep_low[i] == "1":
                passed["deposited_present"].append(TIMES[i])
            if dep_high[i] == "1":
                passed["deposited_fixed"].append(TIMES[i])
    return {k:min(v) for k,v in passed.items()}


def first(groups, endpoint):
    times = {i:g["times"][endpoint] for i,g in groups.items() if endpoint in g["times"]}
    if not times:
        return {"time":None,"groups":[],"classes":[]}
    when=min(times.values())
    ids=sorted((i for i,t in times.items() if t==when),key=int)
    return {"time":when,"groups":ids,"classes":sorted({groups[i]["class"] for i in ids})}


def analyze(rows):
    populations=read_groups(rows)
    counts={k:Counter() for k in ENDPOINTS}
    visits={k:Counter() for k in ENDPOINTS}
    overlap=defaultdict(Counter)
    samples={}
    for well,groups in sorted(populations.items()):
        for group in groups.values():
            group["times"] = group_times(group)
        events={k:first(groups,k) for k in ENDPOINTS}
        for k,event in events.items():
            if event["time"] is None:
                counts[k]["no_event"]+=1
                continue
            counts[k]["unique_group" if len(event["groups"])==1 else "tied_groups"]+=1
            counts[k]["unique_class" if len(event["classes"])==1 else "tied_classes"]+=1
            visits[k][str(event["time"])]+=1
        for a,b in (("local10","deposited_present"),("local10","local90"),("local10","deposited_fixed"),("local90","deposited_fixed"),("deposited_present","deposited_fixed")):
            for unit in ("groups","classes"):
                left,right=set(events[a][unit]),set(events[b][unit])
                if not left or not right:
                    relation = "no_event"
                elif left == right:
                    relation = "identical"
                elif left & right:
                    relation = "partial_overlap"
                else:
                    relation = "disjoint"
                overlap[f"{a}_vs_{b}_{unit}"][relation]+=1
        samples[well]=events
    disagreement = Counter()
    for well, strain, identifier, kind, visits_mask, archived_low, archived_high in rows:
        for local, past_and_future in zip(visits_mask, archived_low):
            if local in "12" and past_and_future == "0":
                disagreement["local_at_least_10_unflagged"] += 1
            elif local not in "12" and past_and_future == "1":
                assert local == "?"
                disagreement["archived_present_with_depth_below_five"] += 1
    return {"populations":len(samples),"source_variant_rows":len(rows),
            "disagreement_with_local_present":dict(disagreement),
            "mutation_groups":sum(len(g) for g in populations.values()),
            "count_observations":len(rows)*len(TIMES),
            "population_counts_by_endpoint":counts,"sampled_generation_counts":visits,
            "sets_at_first_sample":overlap,"sample_events":samples}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--extract",nargs=2,type=Path,metavar=("SUPPLEMENT_1","SUPPLEMENT_2"))
    args=p.parse_args()
    if args.extract:
        from sys import stdout
        writer=csv.writer(stdout,delimiter="\t",lineterminator="\n")
        writer.writerow(["well","strain","group","class","visits","archived_present","archived_fixed"])
        writer.writerows(extract(*args.extract))
    else:
        with (HERE/"yeast_observations.tsv").open() as stream:
            lines=list(csv.reader(stream,delimiter="\t"))
        rows=lines[1:]
        assert len(rows) == 5759 and len({r[0] for r in rows}) == 18
        full=analyze(rows)
        sensitivity=analyze([r for r in rows if r[0]!="P1B03"])
        full["excluding_the_autodiploidized_population"] = {
            k:v for k,v in sensitivity.items() if k!="sample_events"}
        print(json.dumps(full,indent=2))
