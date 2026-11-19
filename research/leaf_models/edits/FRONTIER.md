# How much does the predicted M101 entry depend on which leaf calls can change?

The 0.9.0 analysis preserved every listed membership in 75 peach leaves and allowed unlisted entries to become positive. Its two minimum tables both added M101 to DHQ1_B1-1-L1. Here each listed cell can also become unlisted. A removal costs λ and an addition costs one, with the same positive costs at every site and leaf. All 48 columns stay in the table, with empty sets permitted. The corrected sets must be nested, identical or disjoint. The source records are retained throughout. Edits describe hypothetical tables. [Prior source and proof](https://github.com/maldonado-research/TMD/tree/b96446a969e066f4835fba0ce49412100a388343/research/leaf_lineages) · [Original Wang et al. data](https://doi.org/10.1371/journal.pbio.3000191.s019)

| Removed memberships | Fewest additions | M101 in DHQ1_B1-1-L1 in every optimum at that point | Possible relation of the two nonempty marker sets |
|---:|---:|---|---|
| 0 | 12 | Present | M71 is strictly inside M101 |
| 1 | 9 | Absent | Strictly inside or disjoint |
| 2 through 8 | 9 minus the number removed | Absent | Strictly inside or disjoint |
| 9 | 0 | Absent | Disjoint |

These are all undominated combinations, meaning that no compatible table uses fewer changes of either kind without increasing the other. For equal costs the minimum is nine changes. Requiring M101 present in the named leaf raises it to eleven. If the source positives are instead held fixed, the respective costs for M101 present and absent are 12 and 26 additions. Across the complete positive range of λ, the predicted entry is absent below **3**, can take either value at **3**, and is present above **3**. At the boundary a 12-addition table and a table with one removal and nine additions have equal cost. The source provides no biological calibration of λ. [Frontiers for both cell states and exact relations](mixed_result.json)

For λ below 1 the optimal edit count is (9 removed, 0 added). At 1 every point from (2,7) through (9,0) ties. Between 1 and 2 the optimum is (2,7). At 2 it ties with (1,9), and between 2 and 3 only (1,9) minimizes the loss. Above 3 only (0,12) minimizes it. These comparisons follow by evaluating each pair at loss additions + λ × removals. Multiple compatible tables can have the same counts.

Two complete examples differ in just which M71 observation they remove. Both add the same nine memberships elsewhere, and neither adds M101 in the named leaf. Removing M71 in DHQ1_B1-1-L1 makes M71 strictly contained in M101. Removing M71 in DHQ1_B1-1-L2 instead makes their sets disjoint. All 1,128 marker pairs are compatible in each resulting table. These constructions establish nonidentifiability under that cost convention. They do not identify an erroneous source call. [Named edit witnesses](witness_result.json)

## Why the finite enumeration is exact

Every original marker is confined to one of four main branches. Restrict each marker to its own branch. Within a branch this applies the same restriction to every set and preserves disjointness and containment. Different branches now have disjoint supports. The restriction removes only added memberships and keeps the focal cell in its own branch. An undominated corrected table cannot contain a cross-branch addition. Each of the 34 original singleton columns can also be restored without causing a crossing with any set. The singleton restorations reduce or preserve each edit cost, and neither historical marker is a singleton. These two reductions apply to the full frontier and the two frontiers conditional on the focal cell. The 75 named leaves of the carrier table exhaust the source roster for this tree.

A second calculation requires every marker to retain at least one positive leaf on its original branch. Tracking which markers have at least one assigned carrier and accepting only full coverage reproduces the same global frontier, the same joint marker and focal states at each undominated point, and the same two focal-state frontiers. The unconstrained search supplies the lower bounds, and the coverage-constrained search establishes attainment. Thus none of these tradeoffs depends on erasing a whole marker.

This leaves four multi-leaf markers on each of B1, B2 and B3, and two on B4. In any compatible corrected family, the distinct nonempty sets form an inclusion forest with an artificial root. Equal sets can occupy a chain of adjacent markers in arbitrary order. Empty markers may be attached to the root with no observations assigned to them. Then every leaf's positive markers form one root-to-marker path, including the empty path. Conversely, assigning each leaf to a path in such a tree always yields a compatible matrix. Enumerating each rooted labelled marker tree therefore covers every feasible table. There are 125, 125, 125 and three trees for the respective branches. These enumeration counts have no interpretation as numbers or probabilities of biological histories.

For each tree and each leaf, the routine computes the removals and additions needed to assign that leaf to each allowed path. Its dynamic program keeps only undominated cost pairs with the same partial state. The state records whether at least one assigned leaf is M71-only, M101-only or shared, and whether the focal leaf has acquired M101. Future assignments depend on none of the earlier row choices beyond that state. The union across trees and the sums across the four branches yield the joint frontiers. The output lists relation possibilities only on the global undominated frontier, where the projection proof applies. The separate conditional frontiers fix just the named cell.

The analysis treats a reported bulk leaf as a terminal observation under an irreversible single-lineage model. Several cellular lineages in one organ can violate that assumption even if every listed observation is accurate. There are no independently measured false-call and missed-call probabilities here. These cost comparisons give a test of sensitivity, and cannot establish a mutation time, cause, genotype or first successful evolutionary route. [Source and biological limitations](https://github.com/maldonado-research/TMD/blob/b96446a969e066f4835fba0ce49412100a388343/research/leaf_lineages/PEACH_SOURCES.md)

## Reproduce

Supply the unmodified 0.9.0 carrier TSV. The standard-library scripts use Python 3.10 or later. The exhaustive small test compares every one of 512 three-by-three source matrices against all 398 compatible corrected matrices and checks their joint frontiers, then repeats with all three corrected markers required to be represented.

```sh
python3 -B mixed_frontier.py /path/to/carriers.tsv | diff - mixed_result.json
python3 -B mixed_frontier.py --require-all-markers /path/to/carriers.tsv | diff - mixed_result.json
python3 -B witnesses.py /path/to/carriers.tsv | diff - witness_result.json
python3 -B test_mixed_frontier.py
```

For the optional requirement that every marker retain a listed carrier, the unrestricted computation gives a lower bound. Repeating the restricted search and attaining each bound with a positive carrier on the marker’s own branch proves the same frontiers under that requirement.
