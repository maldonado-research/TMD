"""How do read requirements on proposed additions change the peach completion result?"""
import heapq
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EARLIER = HERE.parents[1] / "leaf_lineages"
sys.path.insert(0, str(EARLIER / "completion"))
from verify_by_union import additions, first_crossing, load

SITES = ("Pp01:2130859", "Pp04:21561355")
MARKERS = ("M71", "M101")
FOCAL = "DHQ1_B1-1-L1"


def optima(original, limits):
    queue = [(0, original)]
    explored = {original}
    optimum = None
    solutions = []
    while queue:
        cost, state = heapq.heappop(queue)
        if optimum is not None and cost > optimum:
            break
        pair = first_crossing(state)
        if pair is None:
            optimum = cost
            solutions.append(state)
            continue
        i,j = pair
        union = state[i] | state[j]
        for index in pair:
            if index in limits and union & ~limits[index]:
                continue
            child = (*state[:index],union,*state[index+1:])
            if child not in explored:
                explored.add(child)
                added = (union & ~state[index]).bit_count()
                heapq.heappush(queue,(cost+added,child))
    return optimum, solutions


def main():
    sites, leaves, original = load(EARLIER / "carrier/carriers.tsv")
    panel = json.loads((HERE/"peach_inputs.json").read_text())["2016_leaf_panel"]
    assert set(panel) == set(leaves) and len(leaves)==75
    where = [sites.index(site) for site in SITES]
    output = []
    for thresholds in [(0,0),(1,1),(2,2),(3,3),(0,1),(0,2),(0,3),(1,0)]:
        limits = {}
        for i,marker,k in zip(where,MARKERS,thresholds):
            eligible=sum(1<<j for j,leaf in enumerate(leaves) if panel[leaf]["counts"][marker][1]>=k)
            limits[i]=original[i] | eligible
        cost, solutions = optima(original, limits)
        edits = [additions(original,s,sites,leaves) for s in solutions]
        common = set.intersection(*edits) if edits else set()
        output.append({"min_ALT_reads_for_new_M71_M101":thresholds,"minimum_additions":cost,
                       "distinct_minimum_tables":len(solutions),
                       "M101_in_focal_leaf_in_optima":sorted({bool(s[where[1]] & (1<<leaves.index(FOCAL))) for s in solutions}),
                       "common_added_memberships":sorted(common)})
    print(json.dumps(output,indent=2))


if __name__=="__main__":
    main()
