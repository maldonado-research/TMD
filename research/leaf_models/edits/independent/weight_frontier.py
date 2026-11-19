"""Exact asymmetric cell-edit frontiers from rooted mutation tree enumeration."""
import argparse
import itertools
import json
from fractions import Fraction
from pathlib import Path

from mutation_trees import TARGET, PEACH_PAIR, trees, load


def nondominated(costs):
    best, result = None, []
    for removed, added in sorted(set(costs)):
        if best is None or added < best:
            result.append((removed, added))
            best = added
    return result


def combine(left, right):
    return nondominated((d+e,a+b) for d,a in left for e,b in right)


def local(sites, leaves, target_state):
    keys = list(sites)
    bit = 1 << keys.index(PEACH_PAIR[1]) if TARGET in leaves else None
    names = sorted(leaves)
    observed = [sum(1 << i for i,key in enumerate(keys) if leaf in sites[key]) for leaf in names]
    all_tree_costs = []
    for patterns in trees(len(sites)):
        tree_costs = [(0,0)]
        for row, (leaf, old) in enumerate(zip(names, observed)):
            allowed = [p for p in patterns
                       if leaf != TARGET or target_state is None or bool(p & bit)==target_state]
            steps = nondominated(((old & ~p).bit_count(), (p & ~old).bit_count()) for p in allowed)
            tree_costs = combine(tree_costs, steps)
        all_tree_costs.extend(tree_costs)
    return nondominated(all_tree_costs)


def best_options(costs, weight):
    value = min(weight*d+a for d,a in costs)
    return value


def phases(off, on):
    # The winning edge of the lower envelope changes only where two affine costs meet.
    costs = sorted(set(off)|set(on))
    critical = {Fraction(a-b,f-d) for (d,a),(f,b) in itertools.combinations(costs,2)
                if d!=f and Fraction(a-b,f-d)>0}
    starts = sorted({Fraction(0),*critical})
    probes = []
    for i,bound in enumerate(starts):
        if i>0:probes.append((str(bound),str(bound),bound,True))
        nxt = starts[i+1] if i<len(starts)-1 else None
        probes.append((str(bound),str(nxt) if nxt else 'infinity',(bound+nxt)/2 if nxt else bound+1,False))
    regions = []
    for lower, upper, probe, point in probes:
        x,y = best_options(off,probe),best_options(on,probe)
        state = 'unlisted' if x<y else 'listed' if x>y else 'either'
        if regions and regions[-1]['target']==state:
            regions[-1]['upper'] = upper
            regions[-1]['upper_included'] = point
        else:
            regions.append({'lower':lower,'upper':upper,'lower_included':point,'upper_included':point,'target':state})
    return regions


def run(path):
    _,leaves,active=load(path)
    others=[(0,0)]
    for b in sorted(leaves):
        if b!='B1':others=combine(others,local(active[b],leaves[b],None))
    off = combine(others,local(active['B1'],leaves['B1'],False))
    on = combine(others,local(active['B1'],leaves['B1'],True))
    return {'order':['removed','added'],'M101_unlisted_at_target':off,'M101_listed_at_target':on,
            'unconstrained':nondominated(off+on),'positive_removal_weight_relative_to_addition':phases(off,on)}


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('carriers',type=Path)
    print(json.dumps(run(p.parse_args().carriers),indent=2))
