"""Independently enumerate additions-only rooted-tree fits under two read-support gates."""
import argparse
import csv
import json
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import product
from math import prod
from pathlib import Path


TARGET = "DHQ1_B1-1-L1"
FOCUS = ("M71", "M101")


def path_sets(k):
    """Label root 0. Decode every labelled tree once from its Prufer code."""
    for code in product(range(k+1), repeat=max(0,k-1)):
        degree=Counter({j:1 for j in range(k+1)})
        degree.update(code)
        adj=defaultdict(set)
        for parent in code:
            leaf=min(j for j in degree if degree[j] == 1)
            adj[leaf].add(parent)
            adj[parent].add(leaf)
            degree[leaf]-=1
            degree[parent]-=1
        ends=[j for j in degree if degree[j]==1]
        assert len(ends)==2
        a,b=ends
        adj[a].add(b)
        adj[b].add(a)
        todo=[(0,-1,0)]
        paths=[]
        while todo:
            j,last,mask=todo.pop()
            if j:
                mask |= 1 << (j-1)
            paths.append(mask)
            todo.extend((i,j,mask) for i in adj[j] if i!=last)
        yield paths


def solve_branch(names, markers, supports, panel, thresholds):
    old=[]
    upper=[]
    for name in names:
        measured=sum(1 << i for i,m in enumerate(markers) if name in supports[m])
        blocked=sum(1 << i for i,m in enumerate(markers)
                    if m in thresholds and name not in supports[m]
                    and panel[name]["counts"][m][1] < thresholds[m])
        old.append(measured)
        upper.append(((1 << len(markers))-1) ^ blocked)
    best=None
    feasible=[]
    for tree in path_sets(len(markers)):
        options=[]
        cost=0
        for measured,allowed in zip(old,upper):
            fits=[p for p in tree if p & measured == measured and p & allowed == p]
            if not fits:
                break
            local=min((p^measured).bit_count() for p in fits)
            cost+=local
            if best is not None and cost>best:
                break
            options.append([p for p in fits if (p^measured).bit_count()==local])
        if len(options)!=len(names):
            continue
        if best is None or cost<best:
            best,feasible=cost,[]
        feasible.extend(product(*options))
    fits=set(feasible)
    info={"minimum_additions":best, "distinct_optima":len(fits)}
    if TARGET in names and fits:
        target=names.index(TARGET)
        focus=[1<<markers.index(m) for m in FOCUS]
        outcomes=Counter()
        for rows in fits:
            pair=[{i for i,r in enumerate(rows) if r&bit} for bit in focus]
            if pair[0]<pair[1]:
                rel="M71_strictly_inside_M101"
            elif pair[1]<pair[0]:
                rel="M101_strictly_inside_M71"
            else:
                assert pair[0]==pair[1] or pair[0].isdisjoint(pair[1])
                rel="identical" if pair[0]==pair[1] else "disjoint"
            value="listed" if rows[target]&focus[1] else "unlisted"
            outcomes[(rel,value)]+=1
        info["focal_outcomes"]=[{"relation":rel,"M101_in_L1":v,"local_tables":n}
                                for (rel,v), n in sorted(outcomes.items())]
    return info


def analyze(carriers, table):
    data=json.loads(table.read_bytes())
    assert data["counts_order"]==["REF","ALT"]
    assert sha256(carriers.read_bytes()).hexdigest()==data["normalized_2019_tsv_sha256"]["carriers"]
    panel=data["2016_leaf_panel"]
    with carriers.open() as f:
        sites=sorted(csv.DictReader(f,delimiter="\t"),key=lambda r:(r["chromosome"],int(r["position"])))
    supports={f"M{i}":set(r["listed_leaves"].split(";")) for i,r in enumerate(sites,71)}
    assert len(supports)==48 and set().union(*supports.values())==set(panel)
    result={}
    conditions=[(0,0),(1,1),(2,2),(3,3),(0,3),(3,0)]
    for k71,k101 in conditions:
        by_branch={}
        limits=dict(zip(FOCUS,(k71,k101)))
        for branch in ("B1","B2","B3","B4"):
            names=sorted(n for n in panel if n.startswith("DHQ1_"+branch+"-"))
            markers=[m for m,S in supports.items() if len(S)>1 and S.intersection(names)]
            assert all(supports[m]<=set(names) for m in markers)
            by_branch[branch]=solve_branch(names,markers,supports,panel,limits)
        count=prod(z["distinct_optima"] for z in by_branch.values())
        minimum=sum(z["minimum_additions"] for z in by_branch.values()) if count else None
        result[f"M71_ge_{k71}_M101_ge_{k101}"]={
            "minimum_additions":minimum, "distinct_optima":count,"branches":by_branch}
    return result


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("carriers",type=Path)
    parser.add_argument("peach_inputs",type=Path)
    args=parser.parse_args()
    print(json.dumps(analyze(args.carriers,args.peach_inputs),indent=2))
