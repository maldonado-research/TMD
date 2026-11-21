"""Score within-path order and directly supported daughter-index timing from anonymous counts."""
import argparse
import csv
import json
from collections import Counter, defaultdict
from itertools import combinations
from math import inf
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def pair_order(groups):
    # Each path compares only its own site observations. Cross-path indices are not a clock.
    counts = Counter()
    first = {}
    for path, records in groups.items():
        minimum_upper = min(last for _,last in records)
        first[path] = dict(index=minimum_upper,
                           possible_first_sites=sum(start <= minimum_upper for start,_ in records))
        for (lo1,hi1),(lo2,hi2) in combinations(records,2):
            if hi1 < lo2 or hi2 < lo1:
                counts["strict_order"] += 1
            elif lo1 == hi1 == lo2 == hi2:
                counts["same_index"] += 1
            else:
                counts["overlap_including_multislot"] += 1
    return dict(sites=sum(len(v) for v in groups.values()), pairs=sum(counts.values()),
                **{k:counts[k] for k in ("strict_order","same_index","overlap_including_multislot")},
                first_candidates=first)


def analyze(directory):
    divisions = defaultdict(dict)
    for row in read(directory/"divisions.tsv"):
        path, d = row["path"], int(row["daughter_index"])
        assert d not in divisions[path]
        divisions[path][d] = row
    obs = read(directory/"observations.tsv")
    site_ids = [r["site_id"] for r in obs if r["source_status"]!="inherited"]
    assert len(site_ids)==len(set(site_ids))==237
    source, repeated, adjacent = defaultdict(list),defaultdict(list),defaultdict(list)
    direct_only = defaultdict(list)
    observed_windows = defaultdict(list)
    unspecific = Counter()
    per_path = {}
    for path, slots in divisions.items():
        all_events = [r for r in obs if r["path"] == path and r["source_status"] != "inherited"]
        source_counts = Counter()
        support = Counter()
        for row in all_events:
            positive = {int(x) for x in row["positive_daughter_indices"].split(",")}
            first = min(positive)
            assert max(positive)==max(slots)
            source_counts[first] += 1
            bounds = (first-1,first) if row["source_status"]=="interval" else (first,first)
            source[path].append(bounds)
            sampled = {d for d,v in slots.items() if v["sample"] in ("daughter","granddaughter")}
            daughter = {d for d,v in slots.items() if v["sample"] == "daughter"}
            realized = positive & sampled
            assert realized and realized == {d for d in sampled if d>=min(realized)}
            first_measured = min(realized)
            earlier = [d for d in sampled if d < first_measured]
            # A first positive at the left edge gives an upper bound with no prior negative.
            lower = max(earlier)+1 if earlier else -inf
            observed_windows[path].append((lower,first_measured))
            if lower != first_measured:
                label = f"{int(lower)}-{first_measured}" if earlier else f"left-censored through {first_measured}"
                unspecific[f"{path}: {label}"] += 1
            if len(realized)==1:
                support["visible_only_in_terminal"] += 1
            else:
                repeated[path].append(bounds)
                # Includes directly measured granddaughter proxies on the mother axis.
                if first in sampled and first-1 in sampled:
                    adjacent[path].append((first,first))
            positive_daughters = positive & daughter
            if (len(positive_daughters)>=2 and first in daughter and first-1 in daughter):
                direct_only[path].append((first,first))
        for d,v in slots.items():
            assert source_counts[d] == int(v["s1_matrix_new"] or 0)
        per_path[path] = dict(source_sites=len(all_events),
            terminal_only=support["visible_only_in_terminal"], repeated_sample_columns=len(repeated[path]),
            repeated_and_adjacent=len(adjacent[path]), daughter_only_repeated_and_adjacent=len(direct_only[path]),
            callable_bases=int(next(iter(slots.values()))["callable_bases_per_division"]))
    totals={}
    for key in ("s1_matrix_new","s2_model_new","s1_docx_new"):
        values=[int(v[key]) for slots in divisions.values() for v in slots.values() if v[key]!=""]
        totals[key] = dict(numeric_rows=len(values), sum_new_events=sum(values))
    order = {k:pair_order(g) for k,g in (("all_source_calls",source),("observed_column_windows",observed_windows),("repeated_columns",repeated),
            ("repeated_plus_adjacent",adjacent),("daughter_only_repeated_plus_adjacent",direct_only))}
    g1 = {r["site_id"] for r in obs if r["path"]=="G1"}
    g2 = {r["site_id"] for r in obs if r["path"]=="G2"}
    common = g1 & g2
    assert common == {r["site_id"] for r in obs if r["source_status"]=="inherited"}
    # Shared trunk versus G2's new sites are additional pairs beyond the G1 sheet.
    # G1-specific versus G2-specific sites lie on different branches in a single-origin tree.
    fork = {"shared_sites": len(common), "g1_specific":len(g1-common), "g2_specific":len(g2-common),
            "additional_trunk_to_g2_pairs":len(common)*len(g2-common),
            "between_limb_pairs": len(g1-common)*len(g2-common)}
    return {"per_path":per_path, "branched_family_G":fork,
            "observed_column_single_index":len(site_ids)-sum(unspecific.values()),
            "other_observed_windows":dict(unspecific), "source_summary_crosscheck":totals,
            "repeated_across_g_branches_and_counted_once":sum(r["source_status"]=="inherited" for r in obs),
            "terminal_only":sum(v["terminal_only"] for v in per_path.values()),
            "source_single_index":sum(lo==hi for grp in source.values() for lo,hi in grp),
            "source_interval":sum(lo!=hi for grp in source.values() for lo,hi in grp),
            "within_path_order": order}


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--directory", type=Path, default=HERE)
    print(json.dumps(analyze(p.parse_args().directory),indent=2))
