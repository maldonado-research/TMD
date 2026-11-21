"""Independent four-point split and joint missing-call audit of Satake et al. Supplementary file 1."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
from xml.etree import ElementTree as XML
from zipfile import ZipFile

INPUT_SHA256 = "a5916e95facc077a137ce03627b2a94ef7ecf3cc9a148223587bdb719d2a06af"
PANEL = ("0", "1_1", "1_2", "2_1", "2_2", "3_1", "3_2", "4")
LABELS = tuple(range(8))
PAIRS = list(combinations(LABELS, 2))
ALL_TIPS = (1 << 8) - 1


def worksheet(book, part, strings):
    for row in XML.fromstring(book.read(f"xl/worksheets/sheet{part}.xml")).findall(".//{*}row"):
        values = {}
        for cell in row:
            val = cell.find("{*}v")
            if val is None:
                continue
            key = cell.attrib["r"].rstrip("0123456789")
            values[key] = strings[int(val.text)] if cell.get("t") == "s" else val.text
        yield values


def load_workbook(path):
    if sha256(path.read_bytes()).hexdigest() != INPUT_SHA256:
        raise ValueError("Unexpected source workbook")
    physical = defaultdict(dict)
    genetic = defaultdict(dict)
    records = defaultdict(list)
    with ZipFile(path) as book:
        strings = ["".join(s.itertext()) for s in XML.fromstring(book.read("xl/sharedStrings.xml"))]
        b = list(worksheet(book, 2, strings))
        assert [b[0][c] for c in "DEFGHIJ"] == list(PANEL[:-1])
        for row in b[1:]:
            if "B" not in row:
                continue
            i = PANEL.index(row["C"])
            for j, col in enumerate("DEFGHIJ"[:i]):
                dist, variants = row[col].split()
                metre, dot, centi = dist.partition(".")
                physical[row["B"]][j, i] = 100*int(metre) + int(centi.ljust(2, "0"))
                genetic[row["B"]][j, i] = int(variants.strip("()"))
        f = list(worksheet(book, 6, strings))
        totals = {r["B"]: int(r["H"]) for r in f[1:] if "H" in r}
        k = list(worksheet(book, 11, strings))
        assert [k[0][c].replace("\xa0", "") for c in "FGHIJKLM"] == list(PANEL)
        for r in k[1:]:
            calls = tuple(r[c] for c in "FGHIJKLM")
            records[r["A"]].append(calls)
    attached = {}
    for name, calls in records.items():
        observed = {(i,j): sum(row[i] != row[j] for row in calls) for i,j in PAIRS}
        matches = [tree for tree in genetic if observed == genetic[tree]]
        assert len(matches) == 1
        tree, = matches
        assert tree not in attached and len(calls) == totals[tree]
        attached[tree] = (name, calls)
    return physical, attached


def masks():
    for mask in range(2, 256, 2):
        yield mask, [i for i in LABELS if mask & (1<<i)], [i for i in LABELS if not mask & (1<<i)]


def isolate_splits(metric):
    """Buneman split isolation in exact integer units. Lengths are twice-centimetres."""
    def distance(i,j):
        return metric[tuple(sorted((i,j)))] if i != j else 0

    edges = {}
    for mask, left, right in masks():
        # Permit equal leaves in a pair on a singleton side, as for pendant edges.
        left_pairs = list(combinations(left, 2)) or [(left[0], left[0])]
        right_pairs = list(combinations(right, 2)) or [(right[0], right[0])]
        gaps = []
        for a,b in left_pairs:
            for c,d in right_pairs:
                across = distance(a,c) + distance(b,d)
                other = distance(a,d) + distance(b,c)
                within = distance(a,b) + distance(c,d)
                if across != other:
                    gaps.append(0)
                else:
                    gaps.append(across-within)
        if min(gaps) > 0:
            edges[mask] = min(gaps)
    assert len(edges) == 2*len(LABELS)-3
    for i,j in PAIRS:
        reconstructed = sum(value for mask,value in edges.items() if bool(mask & 1<<i) != bool(mask & 1<<j))
        assert reconstructed == 2*distance(i,j)
    return edges


def fitch(calls, splits):
    """Unordered-state parsimony on a binary tree with a basal leaf joined to the crown."""
    def visit(node):
        if node.bit_count() == 1:
            return 0, {calls[node.bit_length()-1]}
        desc = [other for other in splits if other != node and other & node == other]
        children = [x for x in desc if not any(x != y and x & y == x for y in desc)]
        assert len(children) == 2
        (c1,s1),(c2,s2) = [visit(x) for x in children]
        return c1 + c2 + int(not s1.intersection(s2)), s1.intersection(s2) or s1.union(s2)
    cost, states = visit(ALL_TIPS-1)
    return cost + (calls[0] not in states)


def relation(left, right):
    if left == right:
        return "same"
    if left & right == left:
        return "later"
    if left & right == right:
        return "earlier"
    assert left & right == 0
    return "different_branches"


def order_examples(counts, compatible, budgets):
    pair_stats = {case: Counter() for case in budgets}
    for p, n in counts.items():
        for q, m in counts.items():
            if q < p:
                continue
            weight = comb(n, 2) if p == q else n*m
            if not weight:
                continue
            for case, accept in budgets.items():
                paths = {relation(e, f) for e,c in compatible[p].items() for f,d in compatible[q].items()
                         if accept(p,q,c,d)}
                if not paths:
                    result = "incompatible"
                elif len(paths) == 1:
                    result, = paths
                    if result in {"later","earlier"}:
                        result = "strict_order"
                else:
                    result = "multiple_relationships"
                pair_stats[case][result] += weight
    return pair_stats


def one_extra(hist, costs, order_at_minimum):
    """Count all global placements with exactly one extra miss without listing raw loci."""
    baseline = {p:min(edges, key=edges.get) for p,edges in costs.items()}
    assert all(sum(cost == edges[baseline[p]] for cost in edges.values()) == 1
               for p, edges in costs.items())
    totals = Counter()
    for pattern, choices in costs.items():
        nest = baseline[pattern]
        for other, cost in choices.items():
            if cost != choices[nest] + 1:
                continue
            difference = 0
            for q, count in hist.items():
                count -= (q == pattern)
                orig = relation(nest, baseline[q])
                alt = relation(other, baseline[q])
                difference += count * (int(alt in {"later","earlier"}) - int(orig in {"later","earlier"}))
            totals[order_at_minimum + difference] += hist[pattern]
    return totals


def verify(path):
    physical, attached = load_workbook(path)
    trees = {}
    merged = defaultdict(Counter)
    one_extra_by_tree = {}
    for tree in sorted(physical):
        label, records = attached[tree]
        edges = isolate_splits(physical[tree])
        multistate_changes = Counter()
        for row,n in Counter(records).items():
            multistate_changes[fitch(row, edges)] += n
        masks2 = [sum(1<<i for i in LABELS if r[i] != r[0]) for r in records if len(set(r)) == 2]
        hist = Counter(masks2)
        costs = {p:{e:(e^p).bit_count() for e in edges if e & p == p} for p in hist}
        minimum = {p:min(c.values()) for p,c in costs.items()}
        min_cost = sum(n*minimum[p] for p,n in hist.items())
        budgets = {"exact_calls":lambda p,q,c,d: max(c,d)==0,
                   "one_per_site":lambda p,q,c,d: max(c,d)<=1,
                   "two_per_site":lambda p,q,c,d: max(c,d)<=2}
        for extra in (0,1,2):
            budgets[f"joint_minimum_plus_{extra}"] = lambda p,q,c,d,slack=extra: c+d <= minimum[p]+minimum[q]+slack
        order = order_examples(hist, costs, budgets)
        n = len(masks2)
        for k, v in order.items():
            assert sum(v.values()) == comb(n,2)
            merged[k].update(v)
        min_orders = order["joint_minimum_plus_0"]["strict_order"]
        one_extra_by_tree[tree] = one_extra(hist, costs, min_orders)
        trees[tree] = {
            "sheet_k_native_header":label,"loci":len(records),"two_state_loci":n,
            "exact_physical_metric_clades_and_twice_cm": {
                ",".join(PANEL[j] for j in LABELS if e & (1<<j)):w for e,w in sorted(edges.items())},
            "unordered_genotype_changes":dict(sorted(multistate_changes.items())),
            "minimum_required_missed_genotypes":min_cost,
            "sites_by_number_of_possible_edges":{str(b):dict(Counter(sum(cost<=b for cost in costs[p].values())
                for p in masks2)) for b in (0,1,2)},
            "within_tree_distinct_pairs":comb(n,2), "locus_pairs_by_budget":dict(order)
        }
    combined = Counter()
    all_minimum_orders = merged["joint_minimum_plus_0"]["strict_order"]
    for tree, distribution in one_extra_by_tree.items():
        unaffected = all_minimum_orders - trees[tree]["locus_pairs_by_budget"]["joint_minimum_plus_0"]["strict_order"]
        for comparable, sites in distribution.items():
            combined[comparable+unaffected] += sites
    return {"native_sha256":INPUT_SHA256, "trees":trees, "all_within_tree_pairs_by_budget":dict(merged),
            "exactly_one_extra_miss": {"distinct_complete_placements":combined.total(),
                                        "min_pairs_on_nested_edges_in_one_placement":min(combined),
                                        "max_pairs_on_nested_edges_in_one_placement":max(combined)}}


if __name__ == "__main__":
    a=ArgumentParser(description=__doc__)
    a.add_argument("workbook",type=Path)
    print(json.dumps(verify(a.parse_args().workbook),sort_keys=True,indent=2))
