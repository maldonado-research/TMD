# An independent certificate for the minimum number of additions

A crossing is a pair of recorded carrier sets with at least one leaf shared and at least one unique to each set. Suppose every recorded membership must be preserved, every unlisted site–leaf combination may become a positive membership at unit cost, and the final sets must be disjoint or nested, allowing equality. The 48 original markers have ten crossing pairs. Independent enumeration gives these exact minima on the 75 sampled leaves.

| Requirement on the completed sets | Minimum added memberships | Distinct minimum tables | M71 size | M101 size |
|---|---:|---:|---:|---:|
| No extra requirement | 12 | 2 | 2 | 18 |
| M101 contained in M71, allowing equality | 26 | 2 | 18 | 17 |
| M71 and M101 equal | 27 | 2 | 18 | 18 |

Ten additions occur in both unrestricted minimum tables. Four of these add leaves to M101, including the originally M71-only leaf DHQ1_B1-1-L1. In each minimum table M71 is strictly contained in M101. The reverse containment can also be achieved with 26 additions, and both optimal reverse solutions are strict. The comparison is a property of an equal-cost completion of recorded memberships. The source supplies no biological probability for these hypothetical completions. [Wang et al., 2019](https://doi.org/10.1371/journal.pbio.3000191) · [Recorded rows in S2 Data](https://doi.org/10.1371/journal.pbio.3000191.s019)

## Why the certificate works

Once a pair crosses, adding memberships cannot make its shared leaf disappear. A laminar completion must put its two sets in one containment direction or the other. Equality satisfies both directions. The program enumerates all 1,024 assignments of directions to the ten original crossings. It computes the directed transitive closure for each assignment. A marker must contain the union of the recorded leaves of every marker required to be within it. Those unions form the least enlargement consistent with the chosen directions. Its cost bounds below the cost of every completion satisfying the assignment.

Only two of the original assignments have a lower bound of 12. In each case the least enlargement is already laminar, and the two completed tables differ. Any further addition increases cost. This certifies both minimality and the exact number of solutions. To cover additional marker constraints, the verifier can refine an assignment at one remaining crossing by trying both directions and computing closure again. The first bound of 25 for reverse containment rises to 26 through this refinement. Equality begins at 27 and achieves it. Assignments leading to identical completed tables are counted once. A comparison of all feasible binary tables on three leaves checks the optimization and the complete set of minima in 1,029 small labeled examples.

Run from the directory holding these scripts and supply the path to the normalized carrier table.

```sh
python3 -B orientation_certificate.py /path/to/carriers.tsv | diff - orientation_result.json
python3 -B test_orientation_certificate.py
```

A second algorithm starts at the recorded sets, resolves each crossing by enlarging one side to its union with the other, and searches by total cost. It independently recovers the actual added cells for every minimum table in all three scenarios. Applying it directly to the numbered leaf icons gives the same minimum sizes and counts. In the figure, M71 and M101 correspond to markers 4 and 2, respectively. [Figure verification](../topology/FIGURE_MATCH.md)

```sh
python3 -B verify_by_union.py
```
