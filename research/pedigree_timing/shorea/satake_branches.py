"""Reconstruct genotype blocks and map two-state patterns to the sampled physical tree."""
import argparse
from collections import Counter
from decimal import Decimal
from hashlib import sha256
from itertools import combinations, combinations_with_replacement
import json
from math import comb
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
NAMES = ('0', '1_1', '1_2', '2_1', '2_2', '3_1', '3_2', '4')
SOURCE = 'a5916e95facc077a137ce03627b2a94ef7ecf3cc9a148223587bdb719d2a06af'
PAIRS = tuple(combinations(range(len(NAMES)), 2))


def extract(path):
    from openpyxl import load_workbook
    if sha256(path.read_bytes()).hexdigest() != SOURCE:
        raise ValueError('Unexpected native workbook checksum')
    book = load_workbook(path, read_only=True, data_only=True)
    geom, base_dist, by_block = {}, {}, {}
    for row in list(book['b'].values)[1:]:
        if row[0] is None:
            continue
        tree = row[1]
        e = geom.setdefault(tree, {})
        counts = base_dist.setdefault(tree, {})
        for j, cell in enumerate(row[3:10]):
            if cell is None:
                continue
            pair = (j, NAMES.index(str(row[2])))
            m = re.fullmatch(r'([\d.]+)\s*\((\d+)\)', str(cell))
            cm = Decimal(m[1]) * 100
            assert cm == int(cm) and pair not in e
            e[pair] = int(cm)
            counts[pair] = int(m[2])
    variants = list(book['k'].values)
    assert tuple(str(x).replace('\xa0','') for x in variants[0][5:13]) == NAMES
    unique = set()
    for row in variants[1:]:
        label, contig, position = row[:3]
        key = (label, contig, position)
        assert key not in unique
        unique.add(key)
        calls = tuple(row[5:13])
        assert set(calls) <= {'0/0', '0/1', '1/1'}
        by_block.setdefault(label, []).append(calls)
    total_by_tree = {}
    for row in list(book['f'].values)[1:]:
        if row[7] is not None:
            total_by_tree[row[1]] = int(row[7])
    trees = {}
    for label, records in by_block.items():
        geno = {pair: sum(r[pair[0]] != r[pair[1]] for r in records) for pair in PAIRS}
        scores = {t: sum(abs(geno[p] - d[p]) for p in PAIRS) for t,d in base_dist.items()}
        matches = [t for t in scores if scores[t] == 0]
        if len(matches) != 1 or len(records) != total_by_tree[matches[0]]:
            raise ValueError('Cannot identify genotype block from distances and final source counts')
        tree, = matches
        assert tree not in trees
        # Basal-relative genotype differences; two genotypes required for primary mapping.
        hist = Counter()
        state_patterns = Counter()
        for r in records:
            # Anonymous state coding follows first appearance, with the baseline state zero.
            index = {value: i for i,value in enumerate(dict.fromkeys(r))}
            state_patterns[''.join(str(index[x]) for x in r)] += 1
            states = len(set(r))
            bits = ''.join('1' if x != r[0] else '0' for x in r[1:])
            assert states in (2,3) and '1' in bits
            hist[states, bits] += 1
        trees[tree] = {'sheet_k_label': label, 'source_sites': len(records),
                       'summed_absolute_distance_mismatch_by_tree': dict(sorted(scores.items())),
                       'physical_cm_by_pair_order': [geom[tree][p] for p in PAIRS],
                       'state_patterns': dict(sorted(state_patterns.items())),
                       'patterns': [[s,b,n] for (s,b),n in sorted(hist.items())]}
    assert set(trees) == {'S1','S2','F1','F2'} and len(unique) == 1136
    return {'source_sha256': SOURCE, 'sample_order': list(NAMES), 'trees': dict(sorted(trees.items()))}


def clades(distances):
    # Twice the base-to-branchpoint distance avoids fractional centimetres.
    matrix = dict(zip(PAIRS, distances, strict=True))
    def distance(i,j):
        return 0 if i == j else matrix[tuple(sorted((i,j)))]
    tips = range(1, len(NAMES))
    shared = {(i,j): distance(0,i)+distance(0,j)-distance(i,j) for i in tips for j in tips}
    edges = set()
    for i in tips:
        for level in {shared[i,j] for j in tips if shared[i,j] > 0}:
            edges.add(frozenset(j for j in tips if shared[i,j] >= level))
    assert len(edges) == 13 and frozenset(tips) in edges
    assert all(not a & b or a<=b or b<=a for a,b in combinations(edges,2))
    end = {e: min(shared[i,j] for i in e for j in e) for e in edges}
    for i,j in combinations(tips,2):
        a = min((e for e in edges if i in e and j in e), key=len)
        assert end[a] == shared[i,j]
    return edges


def minimum_state_changes(edges, calls):
    """Sankoff parsimony with unit cost between distinct observed genotype states."""
    states = set(calls)
    best = {}
    for edge in sorted(edges,key=len):
        if len(edge) == 1:
            tip, = edge
            best[edge] = {v: 0 if calls[tip] == v else float('inf') for v in states}
            continue
        descendants = [e for e in edges if e < edge]
        children = [e for e in descendants if not any(e < f for f in descendants)]
        assert len(children) == 2
        best[edge] = {v: sum(min(n + (w != v) for w,n in best[c].items()) for c in children)
                      for v in states}
    crown = frozenset(range(1,len(NAMES)))
    return min(n + (w != calls[0]) for w,n in best[crown].items())


def pair_summary(patterns, candidates):
    counts = Counter()
    for a,b in combinations_with_replacement(patterns,2):
        count = comb(patterns[a],2) if a == b else patterns[a]*patterns[b]
        if not count:
            continue
        left, right = candidates[a], candidates[b]
        if not left or not right:
            kind = 'at_least_one_incompatible_site'
        else:
            if all(i > j for i in left for j in right) or all(i < j for i in left for j in right):
                kind = 'relative_order_forced_by_strict_ancestry'
            elif all(i.isdisjoint(j) for i in left for j in right):
                kind = 'always_on_separate_branches'
            elif len(left) == len(right) == 1 and left == right:
                kind = 'same_edge_internal_order_unresolved'
            else:
                kind = 'several_relative_placements'
        counts[kind] += count
    assert counts.total() == comb(sum(patterns.values()),2)
    return dict(sorted(counts.items()))


def summarize(data):
    result = {}
    for tree, info in data['trees'].items():
        edges = clades(info['physical_cm_by_pair_order'])
        pats = {frozenset(i for i,bit in enumerate(b,1) if bit=='1'): n
                for s,b,n in info['patterns'] if s == 2}
        gap = Counter()
        for p,n in pats.items():
            gap[min(len(e-p) for e in edges if p<=e)] += n
        budgets = {}
        for b in (0,1,2):
            candidates = {p: {e for e in edges if p<=e and len(e-p)<=b} for p in pats}
            placement = Counter()
            for p,n in pats.items():
                placement[len(candidates[p])] += n
            budgets[str(b)] = {'sites_by_number_of_candidate_edges': dict(sorted(placement.items())),
                               'pairs': pair_summary(pats,candidates)}
        initially_exact = {site:n for site,n in pats.items() if site in edges}
        one_miss = {p:{e for e in edges if p<=e and len(e-p)<=1} for p in initially_exact}
        steps = Counter()
        for calls,n in info['state_patterns'].items():
            steps[minimum_state_changes(edges,calls)] += n
        result[tree] = {
            'all_sites_by_minimum_genotype_changes': dict(sorted(steps.items())),
            'pairs_one_miss_among_sites_with_exact_fit': pair_summary(initially_exact,one_miss),
            'source_sites': info['source_sites'], 'two_genotype_sites': sum(pats.values()),
            'three_genotype_sites_excluded': info['source_sites']-sum(pats.values()),
            'minimum_additional_departures_by_site_count': dict(sorted(gap.items())),
            'per_site_missed_departure_budget': budgets}
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--extract', type=Path, help='Read Satake et al. native workbook; requires openpyxl')
    args = parser.parse_args()
    if args.extract:
        out = extract(args.extract)
    else:
        out = summarize(json.loads((HERE/'satake_patterns.json').read_text()))
    print(json.dumps(out, indent=2))
