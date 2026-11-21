# What a cell-division assignment resolves

Dowsett and colleagues followed serial divisions of seven baker’s yeast mother-cell lineages. Their 2021 study assigned changes to the replication cycle from which they were inferred to have arisen, using inheritance by multiple descendants. A replication error can first be present as a mismatch and become a double-stranded mutation in a later division. The physically recorded division index and the descendants used to infer that index are distinct pieces of evidence. The source’s selected mutation-prone pedigrees and its requirement for interpretable descendant patterns determine this roster. [Original article and figure 1](https://doi.org/10.1038/s42003-020-01544-6)

We checked all 13,801 entries in the authors’ final list against their table of group counts for 50 scored divisions. How many pairs of those changes can the published division assignments put in order? Within each mother lineage, every pair assigned to different division numbers has a relative order under the source assignment. Two changes assigned to the same division share a window. Their molecular order within that window is unresolved. Missing division numbers supply no zero counts. A comparison across different mother lineages has no common chronology from the division indices alone.

For a pedigree with counts $n_d$ per scored division, the number of unresolved within-division pairs is $\sum_d \binom{n_d}{2}$. The number ordered by distinct divisions is $\sum_{i<j} n_i n_j$. These sum to $\binom{\sum_d n_d}{2}$. Counts below are for pairs of distinct changes and use each pair once.

| Relation under the published assignment | Pairs |
| --- | ---: |
| Different ordered divisions of the same mother lineage | 13,374,707 |
| Same scored division of the same mother lineage | 1,932,601 |
| Different mother lineages, without a common clock in this table | 79,919,592 |

Among 15,307,308 same-pedigree pairs, **87.37%** have different ordered division windows. Giving each of the seven pedigrees equal weight gives **84.32%**. These percentages describe resolution among the published changes. They share cells and lineages and are not independent trials or mutation-detection probabilities. The grouping concerns the source's replication-cycle assignments. Fixation in a culture, ecological selection, a base change’s exact molecular time, and establishment of a new route need additional observations. [Output by pedigree](results.json)

## Replay and sources

The released TSV contains three fields. `pedigree` is a local identifier numbered in ascending order of source lineage ID. `physical_division` is the integer labelled “LinDiv #” in the source. `assigned_changes` is the per-division total reconstructed from the four inherited groups. The native verifier checks this total for every division against the original change list and matches its physical division and lineage fields. The publisher and PMC copies of Supplementary Data 1 matched byte for byte (4,874,094 bytes, SHA-256 `cb2ebd86284731f8386f58ee67effbd1e6eeca0e3f73fbbe08897caf0c738fc7`). The worksheet names are `MutInSegGroups` and `Full Mutation List`. [Dowsett et al., Supplementary Data 1](https://static-content.springer.com/esm/art%3A10.1038%2Fs42003-020-01544-6/MediaObjects/42003_2020_1544_MOESM4_ESM.xlsx) · [PMC open archive](https://pmc-oa-opendata.s3.amazonaws.com/PMC7782790.1/42003_2020_1544_MOESM4_ESM.xlsx) · [Original attribution and CC BY 4.0 license](https://www.nature.com/articles/s42003-020-01544-6#rightslink)

From this directory, the first command uses the included table. The second regenerates the anonymous counts from the original workbook.

```sh
python3 -B resolution.py | diff - results.json
python3 -B verify_workbook.py 42003_2020_1544_MOESM4_ESM.xlsx | diff - divisions.tsv
```
