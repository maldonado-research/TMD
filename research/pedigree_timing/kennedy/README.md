# How finely can serial yeast daughters order new variant calls?

Kennedy et al. sequenced clones derived from successive daughters of the same baker’s yeast mother. In their seven mutation-prone lineages, the authors counted 237 maternal mutation events over 87 divisions. One lineage branched, giving eight recorded paths. This retrospective reanalysis asks which pairs of those events the archived measurements can order and how often they identify one first candidate. The published paper studied variation in mutation counts across divisions. The calculations here use the paper's existing calls. [Kennedy et al. (2015)](https://doi.org/10.1371/journal.pgen.1005151) · [Open full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC4395103/)

**The daughter-index assignments order 3,153 of 3,605 within-path event pairs. Only one of the eight paths has a unique first candidate.** The counts of calls at the earliest assigned index in B, C, D, E, F, G1, G2 and H are **2, 3, 2, 2, 3, 1, 7 and 7**. The G2 result covers its five recorded branch-specific indices and excludes two sites inherited from the shared history. Events that first appear together have unresolved within-index order. The sampled paths share experimental background and G1 and G2 share a mother. Comparisons between sites share observations, so the 3,605 pairs are a descriptive denominator.

## Three different times

The workbook’s “Cell Division” numbers index the daughter produced by a division. For this analysis an event's index is the first listed daughter with the published maternal call. The paper’s Figure 1 shows a possible replication error in the first mother division that becomes a stable mutation on the next replication and appears in the third and later daughters. Thus the first positive daughter can occur two divisions after the molecular error. A call in every subsequent sampled daughter supports retention in that family. It provides no population-level establishment time or fitness comparison. The experiment assayed sequences callable across each path, spanning approximately 9.68–11.04 million bases per path. Three wild-type controls yielded zero maternal calls in the paper. The 237 events come from the mutation-prone group. [Figure 1, Table 1 and Methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC4395103/)

The S1 Dataset gives 233 of the 237 calls a single daughter index. Four F calls first appear in daughter 9; the failed sequence from daughter 8 leaves indices 8 and 9 compatible. The S2 Dataset explicitly excludes both indices for its division-by-division modeling. Every other interval in the all-source calculation uses the published assignment. A site can have an assigned index even when the previous daughter is unavailable in that sheet. The tighter observation checks below test this. [S1 Dataset](https://doi.org/10.1371/journal.pgen.1005151.s010) · [S2 Dataset](https://doi.org/10.1371/journal.pgen.1005151.s011)

| Which calls enter | Calls | Within-path pairs | Strictly ordered | Same single index | Overlapping nonsingleton windows |
| --- | ---: | ---: | ---: | ---: | ---: |
| Source-assigned calls, including the four F interval calls | 237 | 3,605 | 3,153 | 446 | 6 |
| Windows from actually sampled predecessor and first positive columns | 237 | 3,605 | 3,153 | 404 | 48 |
| Recorded in at least two sampled positive columns | 213 | 2,993 | 2,602 | 385 | 6 |
| Also requires sampled first positive and immediately preceding negative | 195 | 2,624 | 2,281 | 343 | 0 |
| Same rule using daughter measurements alone | 173 | 2,129 | 1,844 | 285 | 0 |

Two integer windows are strictly ordered when the largest index in one is smaller than the smallest index in the other. In the first row the six overlaps are the six ways to compare the four F calls in their two-index gap. The second row uses only sampled columns. Conditional on a persistent call, its first possible daughter index lies after the last sampled negative and at or before the first sampled positive. Of 237 source events, **219** have adjacent sampled bounds. Four F calls span indices 8–9, seven H calls span 2–3 because H2 is marked DEAD, and seven G2-specific calls have no earlier sampled negative on that sheet. For those seven, the upper end is 5 and the sheet supplies no lower bound. The G2 ancestry supplies separate information as described below. Widening these intervals moves 42 pairs from the same single index to the overlap column and leaves the strictly ordered count unchanged. Within the 233 single-index assignments, every event pair at the same index is a timing tie at this resolution. Disjoint reported indices establish order on this sampling axis, conditional on the call assignments. Twenty-four site calls appear only in the last displayed sampled column of their path. The Methods describe designating a maternal mutation when a variant in the last daughter is shared by one or more preceding daughters. For these 24 rows, an independent reader needs supporting evidence beyond the displayed preceding columns to reproduce that particular rule. Their counts by path B, D, E, F, G1 and H are 4, 2, 10, 1, 4 and 3. An additional specimen or evidence outside those columns could provide support.

In the 213-call row, the count of positive columns excludes the inferred E8 column. Two D samples were granddaughters used in place of their mothers. For the 195-call row they qualify as sampled proxies. The additional adjacency requirement removes four F calls following the sequencing gap, seven H calls whose previous column is marked DEAD, and seven new G2 calls at the left edge of its sheet. The daughter-only row excludes granddaughter proxies from both confirmation and adjacency. It still requires two positive sampled daughters, including the first assigned index, and the preceding sampled daughter to be negative. The score is conditional on the detectable sites that meet the relevant rule. Unsequenced new changes and variants lost before producing a sampled descendant have no entry in these tables.

The two G sheets share two inherited markers. The extraction links their anonymous identifiers and counts each event once. In a single-origin tree without recurrent change, those two shared sites precede the 18 G2-specific sites, giving 36 additional ancestral-order comparisons. The 30 G1-specific and 18 G2-specific sites yield 540 pairs across different branches. Neither limb descends from the other. The paper reports sample order as well as pedigree structure, and calendar ordering across limbs is a separate question. The results in the table compare only sites on the same reported path, after inherited duplicate rows are removed.

## Why the three native tables have different totals

| Native object | Numeric division entries | Sum of new calls | What differs |
| --- | ---: | ---: | --- |
| S1 Dataset, XLSX “New Fixed Mutations” row | 86 | 237 | The F8 entry is empty. Four yellow rows first seen at F9 remain interval-ambiguous. |
| S2 Dataset, XLSX first table | 85 | 233 | The footnote marks both F8 and F9 unresolvable for the per-division distribution. |
| S1 Table, DOCX | 84 | 229 | Both F slots are dashes. The numeric B block ends at division 10. B11 contributes four calls in both workbooks. |

These are row-level differences between the posted objects. The author calculation of 87 physical divisions includes both positions in the F window. The S1 matrix also has two unhighlighted G2 rows inherited from the other sheet, which reproduce the two shared genomic positions. One other genomic position occurs in two separate source-assigned paths (E and F) and is counted once per source path. The XLSX header on C reorders three sample identifiers relative to numerical suffix order. All calculations use the workbook’s explicit daughter-index row. A path's callable bases in the attached table are its source denominator, not evidence of a successful measurement for an individual missing sample. [S1 Table](https://doi.org/10.1371/journal.pgen.1005151.s001) · [Author’s aggregate Table 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC4395103/)

## Reproduction

The two included TSVs contain anonymous observation patterns and source-index summaries. With Python 3.9 or later, replay the results offline from this directory.

```sh
python3 -B score_timing.py | diff - results.json
```

To reproduce the TSVs from the original CC BY 4.0 source files, download the three files below into the current directory, then run the commands. The public PMC archive lists the original file sizes and MD5 checksums. The extractor verifies SHA-256 and reads the spreadsheet XML, including fill colors and the source's explicit division column. It also checks the author summary rows separately against the individual source site rows. Source credit goes to Scott R. Kennedy, Eric M. Schultz, Thomas M. Chappell, Brendan Kohrn, Gary M. Knowels and Alan J. Herr. [PMC source inventory](https://pmc-oa-opendata.s3.amazonaws.com/?list-type=2&prefix=PMC4395103.1/)

| Source | SHA-256 |
| --- | --- |
| [S1 Dataset, matrix](https://pmc-oa-opendata.s3.amazonaws.com/PMC4395103.1/pgen.1005151.s010.xlsx) | `e6005dbf96624706897b630bf36fcab64eeaf7c794266e16db08ae6461852ed3` |
| [S2 Dataset, model inputs](https://pmc-oa-opendata.s3.amazonaws.com/PMC4395103.1/pgen.1005151.s011.xlsx) | `45eba792cedbe93922934bb462a176658f3b835ab911521c891c053aba209922` |
| [S1 Table, Word](https://pmc-oa-opendata.s3.amazonaws.com/PMC4395103.1/pgen.1005151.s001.docx) | `bc1ecc3d3d11ee78be8343f99770089b87a0b4d4af300122a379780c0a5ce0b8` |

```sh
python3 -B extract_kennedy.py pgen.1005151.s010.xlsx pgen.1005151.s011.xlsx pgen.1005151.s001.docx regenerated
diff -u observations.tsv regenerated/observations.tsv
diff -u divisions.tsv regenerated/divisions.tsv
python3 -B score_timing.py --directory regenerated | diff - results.json
```
