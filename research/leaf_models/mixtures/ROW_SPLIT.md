# How many cellular signatures could produce the observed bulk-leaf calls?

Keep all 3,600 entries of the peach catalogue as recorded. Consider one rooted cellular lineage tree in which each marker arose once and was inherited without loss. Allow one bulk leaf to contain cells from several parts of that tree. A marker is listed at a leaf exactly when at least one cellular signature in the leaf carries it. This last assumption treats an unlisted entry as a true absence from the sampled material. The study does not establish that sensitivity. A signature here is a pattern over the 48 measured markers. The method imposes no measured cellular proportions. [Peach study and sampling diagram](https://doi.org/10.1371/journal.pbio.3000191.g004) · [Supplementary carrier lists](https://doi.org/10.1371/journal.pbio.3000191.s019)

Mathematically, each leaf row is the Boolean OR of one or more latent rows. The columns of the resulting expanded matrix must be disjoint or nested, allowing equality. This is the established *minimum conflict-free row split* problem. Its objective counts signature occurrences separately for each sample in which they appear. The original paper distinguishes this objective from counting the number of distinct signatures across an entire study. We apply that mathematics to the peach catalogue. Baghirova, Galby and Milanič subsequently identified classes of inputs where the corresponding branching problem can be solved in polynomial time. [Hujdurović et al., Definitions 1.1–1.2](https://arxiv.org/abs/1701.05492) · [Baghirova et al.](https://doi.org/10.1109/TCBBIO.2025.3580476)

| Minimum signatures for one leaf | Leaves meeting that minimum | B1 | B2 | B3 | B4 |
|---|---:|---:|---:|---:|---:|
| 1 | 55 | 12 | 32 | 4 | 7 |
| 2 | 15 | 12 | 1 | 2 | 0 |
| 3 | 5 | 5 | 0 | 0 | 0 |

The minimum is **100 signature occurrences across the 75 samples**, or 25 extra occurrences. Twenty specific leaves must contain more than one signature under the model. The calculation attains all 75 individual minima on one common tree. Five leaves require at least three signatures, and three suffice for every leaf. More signatures can be present. These counts cannot determine the true number of cells or clonal lineages in the tree.

## A lower bound for every leaf

If marker A arose before B on the same cellular path, every leaf containing a B-positive cell must also list A. The B carrier list is then contained in the A list. Two markers with incomparable carrier lists, each having at least one leaf missing from the other list, can never share one path under these assumptions. If a leaf lists several such mutually incomparable markers, it needs at least one signature per marker. The verifier enumerates the largest such group for every leaf. For example, DHQ1_B1-1-L2 lists M71, M92 and M101. All three pairs have incomparable lists, so the three markers require separate signatures there.

## A single witness attaining all bounds

For each leaf, first take the markers with at least two listed leaves, grouping markers with identical full lists. For each inclusion-minimal carrier list at that leaf, make a signature containing the markers at that list and every marker with a larger list containing it. Use one empty signature as a starting point if the leaf has no multi-leaf marker. Attach the markers unique to this leaf to any one of its signatures. The resulting 100-row witness is stored by named leaf. Its signatures reconstruct every original row exactly by union. All 1,128 pairs of marker columns in the expanded witness are disjoint, nested or identical. This is sufficient for a common rooted perfect phylogeny. Each leaf uses exactly the number of signatures required by its own lower bound. The construction is verified on this matrix, and can fail to produce a perfect phylogeny or to reach the bound on other matrices. [Complete witness](row_split_witness.json) · [Calculation and checks](row_split_witness.py)

The exact-call mixture model and the earlier minimum-addition analysis predict different cell states at the recorded double-positive leaf DHQ1_B1-1-L2. In the earlier one-lineage-per-leaf model the two recorded markers M71 and M101 occur together in that leaf. Under the exact-call mixture model, both are represented in the leaf but cannot occur on the same cellular path anywhere in this catalogue. A confirmed co-occurrence in a single cell from that leaf would rule out the latter model under the single-origin and permanent-inheritance assumptions. The bulk measurements already available cannot resolve that contrast. [Earlier minimum-addition analysis](https://github.com/maldonado-research/TMD/blob/b96446a969e066f4835fba0ce49412100a388343/research/leaf_lineages/completion/CERTIFICATE.md)

Run the following from this directory, using the two TSVs released in the preceding study.

```sh
python3 -B row_split_witness.py /path/to/carriers.tsv /path/to/sample_roster.tsv | diff - row_split_witness.json
```
