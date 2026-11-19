"""Enumerate all small rooted mutation trees and minimize binary edits to the DHQ1 catalogue."""
import argparse
import csv
import itertools
import json
from collections import defaultdict
from pathlib import Path

TARGET = "DHQ1_B1-1-L1"
PEACH_PAIR = ("Pp01:2130859", "Pp04:21561355")


def branch(leaf):
    return leaf.split("_")[1].split("-")[0]


def load(path):
    with path.open() as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    markers = {}
    active = defaultdict(dict)
    leaves = defaultdict(set)
    for row in rows:
        site = f"{row['chromosome']}:{row['position']}"
        calls = set(row["listed_leaves"].split(";"))
        names = {branch(x) for x in calls}
        if len(names) != 1:
            raise ValueError(f"Marker {site} spans branches")
        b = names.pop()
        markers[site] = calls
        leaves[b].update(calls)
        if len(calls) > 1:
            active[b][site] = calls
    return markers, leaves, active


def trees(k):
    # Nodes are 1..k, with implicit root 0. Each array lists all parent pointers.
    for parents in itertools.product(range(k + 1), repeat=k):
        tips = []
        for node in range(1, k + 1):
            seen = 0
            while node:
                bit = 1 << (node-1)
                if seen & bit:
                    break
                seen |= bit
                node = parents[node-1]
            if node:
                break
            tips.append(seen)
        if len(tips) == k:
            yield [0, *tips]


def pair_state(call, bits):
    left, right = bits
    return int(bool(call & left)) + 2 * int(bool(call & right))


# Each scenario describes allowed joint states and a required set of witnesses across leaves.
# A state of 1 means only M71, 2 means only M101, and 3 means both.
RELATIONS = {
    "unconstrained": (set(range(4)), set()),
    "M71_properly_within_M101_both_present": ({0, 2, 3}, {2, 3}),
    "M101_properly_within_M71_both_present": ({0, 1, 3}, {1, 3}),
    "equal_both_present": ({0, 3}, {3}),
    "disjoint_both_present": ({0, 1, 2}, {1, 2}),
}


def minimize_on_tree(patterns, observed, bits, relation, target, target_allele, require_witnesses=True):
    allowed, needed = RELATIONS[relation]
    if not require_witnesses:
        needed = set()
    wanted = sum(1 << s for s in needed)
    if bits:
        permitted = [p for p in patterns if pair_state(p, bits) in allowed]
        realizable = {pair_state(p, bits) for p in permitted}
        if not needed <= realizable:
            return None
    else:
        permitted = patterns
    # Each state stores the least cost and all predecessor patterns/seen masks attaining it.
    costs = {0: 0}
    ancestors = []
    for row, old in enumerate(observed):
        choices = permitted
        if target == row and target_allele is not None:
            choices = [p for p in permitted if bool(p & bits[1]) == target_allele]
        layer = {}
        trace = defaultdict(list)
        for seen, prior in costs.items():
            for p in choices:
                witness = ((1 << pair_state(p, bits)) & wanted) if bits else 0
                new = witness | seen
                score = prior + (p ^ old).bit_count()
                if new not in layer or score < layer[new]:
                    layer[new] = score
                    trace[new] = []
                if score == layer[new]:
                    trace[new].append((seen, p))
        costs = layer
        ancestors.append(trace)
    if wanted not in costs:
        return None
    return costs[wanted], ancestors, wanted


def backtrack(ancestors, wanted):
    def walk(i, state):
        if i == 0:
            yield ()
        else:
            for last, call in ancestors[i-1][state]:
                for prefix in walk(i-1, last):
                    yield prefix + (call,)
    yield from walk(len(ancestors), wanted)


def solve(leaves, sites, relation="unconstrained", target_allele=None, require_witnesses=True):
    names = sorted(leaves)
    ordered = list(sites)
    original = [sum(1 << i for i,key in enumerate(ordered) if leaf in sites[key]) for leaf in names]
    target = names.index(TARGET) if TARGET in names else None
    bits = [1 << ordered.index(key) for key in PEACH_PAIR] if target is not None else None
    best, traces = None, []
    treenum = 0
    for patterns in trees(len(ordered)):
        treenum += 1
        result = minimize_on_tree(patterns, original, bits, relation, target, target_allele, require_witnesses)
        if result is None:
            continue
        value, trace, wanted = result
        if best is None or value < best:
            best, traces = value, []
        if value == best:
            traces.append((trace, wanted))
    assert best is not None
    solutions = set(table for trace, wanted in traces for table in backtrack(trace, wanted))
    details = defaultdict(int)
    pair_counts = defaultdict(int)
    retain_all = 0
    for table in solutions:
        if all(any(row & (1 << i) for row in table) for i in range(len(ordered))):
            retain_all += 1
        adds = sum((new & ~old).bit_count() for new, old in zip(table, original))
        details[(adds,best-adds)] += 1
        if bits:
            old = pair_state(table[target], bits)
            joint = {pair_state(x,bits) for x in table}
            assert not {1,2,3} <= joint
            left = bool(joint & {1,3})
            right = bool(joint & {2,3})
            if not left and not right: name = "both_empty"
            elif not left: name = "M71_empty"
            elif not right: name = "M101_empty"
            elif 3 not in joint: name = "disjoint"
            elif 1 not in joint and 2 not in joint: name = "equal"
            elif 1 not in joint: name = "M71_properly_within_M101"
            else: name = "M101_properly_within_M71"
            pair_counts[(name,int(bool(old & 2)))] += 1
    return {"minimum":best,"distinct_local_tables":len(solutions),"trees_evaluated":treenum,"retaining_every_local_marker":retain_all,
            "by_edits":[{"added":a,"removed":d,"tables":n} for (a,d),n in sorted(details.items())],
            "pair_and_M101_at_target":[{"relation":name,"M101_at_target":value,"tables":n}
                                            for (name,value),n in sorted(pair_counts.items())]}


def run(path):
    markers, leaves, active = load(path)
    assert sum(map(len,leaves.values())) == 75 and len(markers)==48
    baseline = {b:solve(leaves[b],active[b]) for b in sorted(leaves)}
    outside_cost = sum(d["minimum"] for b,d in baseline.items() if b!="B1")
    outside_count = 1
    for b in baseline:
        if b!="B1": outside_count*=baseline[b]["distinct_local_tables"]
    constraints = {}
    for name in RELATIONS:
        for target in ([None, False, True] if name == "unconstrained" else [None]):
            c = solve(leaves["B1"],active["B1"],name,target)
            # Dropping forbidden cross-branch additions can remove a strictness witness.
            # The relaxed local optimum bounds all global optima with witnesses anywhere.
            relaxed = solve(leaves["B1"], active["B1"], name, target, require_witnesses=False)
            assert relaxed["minimum"] == c["minimum"]
            key = name + ["", "_target_absent","_target_present"][[None,False,True].index(target)]
            constraints[key] = {"whole_table_minimum":c["minimum"]+outside_cost,
                                "whole_table_minimizers":c["distinct_local_tables"]*outside_count,
                                "B1":c}
    return {"branches":baseline,"conditions":constraints}


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("carriers",type=Path)
    print(json.dumps(run(p.parse_args().carriers),indent=2))
