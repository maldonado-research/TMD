# How many observed leaf patterns can fit a single tree?

The Wang et al. DHQ1 supplement lists 48 marker locations and 75 distinct leaf samples. A separate retrieval of the publisher-rendered table reproduced every leaf membership in the shared input. The checker sorts the chromosome–position keys and binds their complete leaf lists to a single digest. The labels M71 through M118 in that order were checked at the corresponding locations in Ji et al. Table S2. A leaf missing from a marker’s list is treated as unlisted in this calculation. [Wang et al. S2 Data](https://doi.org/10.1371/journal.pbio.3000191.s019) · [Ji et al. Table S2](https://doi.org/10.1371/journal.pgen.1011829.s016)

Of 1,128 marker pairs, 54 have strictly nested, nonempty sets of listed leaves, 9 have equal sets, 1,055 are disjoint, and 10 cross. A pair crosses if at least one leaf lists both markers, one lists just the first and one lists just the second. Descendant leaf sets in a rooted tree are nested or disjoint. Inferring mutation ancestry from a strict nest additionally requires a single irreversible origin for each marker and faithful observation of one comparable cellular lineage per leaf. Bulk leaves can contain multiple lineages. Equal sets leave the order unresolved, and disjoint sets supply no chronology between branches.

## Restricting the set of markers

The largest collection with no crossing has **43 of 48 markers**. Five independent constraints prove the upper bound. Each of the pairs (M71, M92), (M77, M94), (M95, M109), (M97, M110) and (M101, M103) crosses, and the ten marker IDs are distinct. At least one marker must be omitted from every pair. Omitting M77, M92, M95, M97 and M101 eliminates every crossing and attains the bound. Enumerating covers of all ten crossing pairs gives four minimum omission sets. This calculation cannot identify which observation was biologically wrong.

## Restricting the set of leaves

The minimum is **seven leaves** if a marker is allowed to lose all its listed leaves. On branch B1 the three witness regions for M92 versus M101 contain 3, 5 and 9 leaves. Only one omission of exactly three leaves could eliminate this crossing. Those three leaves have no effect on the M71 versus M101 crossing, requiring at least a fourth omission on B1. On B3 each of the three M77 versus M109 witness regions contains two leaves, requiring at least two omissions. The M97 versus M110 crossing on B2 requires at least one. These branches use disjoint labels, so the lower bound is 4 + 2 + 1. The program finds four sets of seven attaining it. They leave either three or four markers with no listed leaf.

**No restriction to whole leaves can eliminate all crossings while preserving a positive leaf for every marker.** In the M92 versus M101 crossing, B1-8-L2 is the sole listed leaf of M84 and lies on the M92-only side. B1-1-L2 is the sole listed leaf of M100 and carries both. B1-14-L2 is the sole listed leaf of M80 and lies on the M101-only side. Preserving all three singleton markers preserves the crossing.

## Sensitivity to one omitted leaf

Of the 54 strict nests, only five remain strict and nonempty under *every* possible single-leaf omission. Those pairs, shown as inner and outer, are M116 within M81, M96 within M86, M97 within M86, M110 within M86, and M94 within M109. Each has at least two leaves in the inner set and two in the outer-only set. The other 49 each have at least one leaf whose removal empties the inner set or removes the difference. These vulnerable leaves differ across pairs. Omitting any *one* leaf destroys at most four of the 54 nests, a maximum attained by B3-5-L1. Three of the ten crossings survive every possible single-leaf omission. Removing B1-1-L2 eliminates four crossings, the largest drop from one omitted leaf.

Run the checker from its own directory, passing the study's normalized carrier TSV. The source digest covers chromosome, position, mutation change, Ji marker ID and all listed leaf identifiers. Within the exact leaf-omission search, a pending crossing can only be eliminated by removing one of its three witness regions in full. Branching on those three possibilities covers every minimal solution.

```sh
python3 -B leaf_omissions.py /path/to/carriers.tsv | diff - omission_results.json
```

[Exact bounds and omission sets](omission_results.json) · [Independent checker](leaf_omissions.py)
