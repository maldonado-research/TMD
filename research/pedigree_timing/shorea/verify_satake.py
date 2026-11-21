"""Independently check Satake edge placements by quartets, enumerated calls and parsimony."""
from collections import Counter
from itertools import combinations, combinations_with_replacement, product
import json
import argparse
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent

def quartets(distances):
    d = dict(zip(combinations(range(8),2),distances,strict=True))
    def dist(i,j):
        return d[tuple(sorted((i,j)))]
    splits = {}
    for mask in range(1,128):
        a = [tip for tip in range(1,8) if mask & (1 << (tip-1))]
        b = [tip for tip in range(8) if tip not in a]
        if all(dist(i,j)+dist(k,l) < dist(i,k)+dist(j,l) == dist(i,l)+dist(j,k)
               for i,j in combinations(a,2) for k,l in combinations(b,2)):
            splits[mask] = set(a)
    assert len(splits) == 13
    return splits


def minimum_changes(calls,splits):
    # Enumerate states of all six branch vertices, fixing the eight sampled states.
    internal = [s for s in splits if len(splits[s]) > 1]
    choices = sorted(set(calls))
    pairs = []
    for child in splits:
        parents = [p for p in splits if splits[child] < splits[p]]
        parent = min(parents,key=lambda p:len(splits[p])) if parents else 0
        pairs.append((child,parent))
    terminal = {1 << (i-1): calls[i] for i in range(1,8)}
    terminal[0] = calls[0]
    best = len(pairs)
    for xs in product(choices,repeat=len(internal)):
        assign = terminal | dict(zip(internal,xs))
        best = min(best,sum(assign[c] != assign[p] for c,p in pairs))
    return best


def verify(data,expect):
    for tree,info in data['trees'].items():
        saved = expect[tree]
        splits = quartets(info['physical_cm_by_pair_order'])
        h = Counter()
        obs = Counter()
        for calls,n in info['state_patterns'].items():
            h[str(minimum_changes(calls,splits))] += n
            if len(set(calls)) == 2:
                mask = sum(1 << i for i,x in enumerate(calls[1:]) if x != calls[0])
                obs[mask] += n
        assert dict(h) == saved['all_sites_by_minimum_genotype_changes']
        for bound in (0,1,2):
            possible = {}
            cardinality = Counter()
            for mask,count in obs.items():
                zeros = [1 << i for i in range(7) if not mask & (1 << i)]
                possible[mask] = [mask+sum(xs) for b in range(bound+1)
                                  for xs in combinations(zeros,b) if mask+sum(xs) in splits]
                cardinality[str(len(possible[mask]))] += count
            pairs = Counter()
            matched = Counter()
            for a,b in combinations_with_replacement(obs,2):
                n = comb(obs[a],2) if a == b else obs[a]*obs[b]
                if n == 0:
                    continue
                order = set()
                for x,y in product(possible[a],possible[b]):
                    common = x & y
                    if x == y:order.add('same_edge_internal_order_unresolved')
                    elif common == 0:order.add('always_on_separate_branches')
                    elif common == x:order.add('descendant')
                    elif common == y:order.add('ancestor')
                    else:raise AssertionError('Edge clusters crossed')
                if not order:k = 'at_least_one_incompatible_site'
                elif len(order) > 1:k = 'several_relative_placements'
                elif order <= {'ancestor','descendant'}:k = 'relative_order_forced_by_strict_ancestry'
                else:k = order.pop()
                pairs[k] += n
                if a in splits and b in splits:matched[k] += n
            if bound == 1:assert dict(matched) == saved['pairs_one_miss_among_sites_with_exact_fit']
            result = saved['per_site_missed_departure_budget'][str(bound)]
            assert dict(pairs) == result['pairs'] and dict(cardinality) == result['sites_by_number_of_candidate_edges']
    print('All four physical trees, genotype parsimony scores and edge-order tables verified.')


def check_native(path,data):
    """Read workbook string/cell XML independently of the main openpyxl extractor."""
    import re
    from decimal import Decimal
    from hashlib import sha256
    from xml.etree import ElementTree
    from zipfile import ZipFile
    if sha256(path.read_bytes()).hexdigest() != data['source_sha256']:
        raise ValueError('Unexpected native workbook checksum')
    with ZipFile(path) as z:
        strings = [''.join(si.itertext()) for si in ElementTree.fromstring(z.read('xl/sharedStrings.xml'))]
        sheets = ElementTree.fromstring(z.read('xl/workbook.xml')).findall('.//{*}sheet')
        rels = {rel.get('Id'): rel.get('Target') for rel in ElementTree.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        def cells(name):
            sheet = next(s for s in sheets if s.get('name') == name)
            target = rels[sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
            filename = target.lstrip('/') if target.startswith('/') else 'xl/'+target
            out = {}
            for c in ElementTree.fromstring(z.read(filename)).findall('.//{*}c'):
                v = c.findtext('{*}v')
                if v is not None:
                    out[c.get('r')] = strings[int(v)] if c.get('t') == 's' else v
            return out
        b,k = cells('b'),cells('k')
    blocks = {}
    sample = data['sample_order']
    for i in range(2,1138):
        calls = [k[col+str(i)] for col in 'FGHIJKLM']
        values = []
        for x in calls:
            if x not in values:values.append(x)
        states = ''.join(str(values.index(x)) for x in calls)
        h = blocks.setdefault(k['A'+str(i)], Counter())
        h[states] += 1
    pair_order = list(combinations(range(8),2))
    checked = {}
    for i in range(2,30):
        tree = b['B'+str(i)]
        sample_b = sample.index(b['C'+str(i)])
        for c in 'DEFGHIJ':
            cell = b.get(c+str(i))
            if cell is None:continue
            sample_a = sample.index(b[c+'1'])
            metres, n = re.fullmatch(r'([\d.]+)\s*\((\d+)\)',cell).groups()
            checked[tree,sample_a,sample_b] = int(Decimal(metres)*100),int(n)
    assert len(checked) == 112
    for tree,info in data['trees'].items():
        state_counts = blocks[info['sheet_k_label']]
        assert state_counts == info['state_patterns']
        for k,(i,j) in enumerate(pair_order):
            differences = sum(n for s,n in state_counts.items() if s[i] != s[j])
            assert checked[tree,i,j] == (info['physical_cm_by_pair_order'][k],differences)
    print('All 112 native pairwise genetic and spatial distances and all 1,136 site patterns verified.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workbook',type=Path)
    args = parser.parse_args()
    native = json.loads((HERE/'satake_patterns.json').read_text())
    verify(native,json.loads((HERE/'satake_placements.json').read_text()))
    if args.workbook:
        check_native(args.workbook,native)
